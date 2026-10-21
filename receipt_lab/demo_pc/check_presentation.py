"""Exercise the real local demo API; confirmations are explicitly automated tests."""
import json
import time
import urllib.request

from receipt_lab.preboard.common import REPO, WORK, utc, write_json
from receipt_lab.preboard.services import access_token, request
from receipt_lab.preboard.profile_transport import ENTITIES, check_states
from .store import Store


def main():
    base = 'http://127.0.0.1:8090'
    def api(path, data=None):
        body = None if data is None else json.dumps(data).encode()
        req = urllib.request.Request(base + path, body, headers={
            'Content-Type': 'application/json', 'X-Seminar-Token': token})
        with urllib.request.urlopen(req, timeout=600) as response:
            return json.load(response)
    token = ''
    state = api('/api/state')
    token = state['token']
    store = Store(WORK / 'services/demo.sqlite')
    if store.pending():
        raise RuntimeError('Existing pending events require separate review before this test')
    report = {'timestamp': utc(), 'purpose': 'Presentation PC readiness; automatic engineering confirmation, not human review or semantic accuracy',
              'browser_click_test': 'not performed: no connected browser', 'documents': len(state['documents']),
              'saved_transcripts': sum(d['has_saved_transcript'] for d in state['documents']), 'trials': []}
    ha_token = access_token()
    for doc_id in ['R4F4EA934251E', 'R3B0A1D27A6DC', 'R74946CAAC57E']:
        doc = next(d for d in state['documents'] if d['doc_id'] == doc_id)
        began = time.perf_counter()
        processed = api('/api/process', {'doc_id': doc_id, 'rotation': doc['rotation']})
        elapsed = time.perf_counter() - began
        saved = api('/api/receipt?id=' + processed['id'])
        raw = saved['raw_result']
        trial = {'doc_id': doc_id, 'receipt_id': saved['id'], 'pipeline_run_id': raw['run_id'],
                 'process_http_seconds': elapsed, 'rotation': doc['rotation'], 'status': raw['status'],
                 'configuration': raw['configuration'], 'processing_measurement': raw['processing_measurement'],
                 'ocr_status': raw.get('ocr', {}).get('status'), 'llm_status': raw.get('llm', {}).get('status'),
                 'schema_valid': raw.get('llm', {}).get('schema_valid')}
        if raw['status'] != 'pending_review' or not trial['schema_valid'] or trial['llm_status'] != 'ok':
            trial['error'] = raw.get('error', 'Output incomplete or invalid')
        else:
            payload = {'id': saved['id'], 'revision': saved['revision'],
                       'reviewer': 'automated_presentation_readiness_test_not_human_ground_truth',
                       'extraction': raw['extraction']}
            confirmed = api('/api/confirm', payload)
            trial['event_id'] = confirmed['event_id']
            trial['mqtt_puback'] = any(d['event_id'] == confirmed['event_id'] and d['mqtt_puback'] for d in confirmed['delivery'])
            observed = []
            for _ in range(30):
                observed = [s for s in request('/api/states', token=ha_token)
                            if s['entity_id'] in ENTITIES and s['attributes'].get('event_id') == confirmed['event_id']]
                if len(observed) == 2:
                    break
                time.sleep(.2)
            trial['ha_value_checks'] = check_states(observed, raw['extraction'])
            trial['ha_entities'] = [{'entity_id': s['entity_id'], 'state': s['state'], 'event_id': s['attributes'].get('event_id')} for s in observed]
            duplicate = api('/api/confirm', payload)
            trial['same_confirmation_idempotent'] = duplicate['event_id'] == confirmed['event_id'] and not duplicate['delivery']
            trial['status'] = 'ok' if all(trial[k] for k in ['mqtt_puback', 'ha_value_checks', 'same_confirmation_idempotent']) else 'failed'
        report['trials'].append(trial)
        write_json(REPO / 'reports/preboard/presentation_pc_check_2026-10-21.json', report)
        print(json.dumps(trial, ensure_ascii=True), flush=True)
    report['all_passed'] = all(t['status'] == 'ok' for t in report['trials'])
    report['pending_outbox_after'] = len(store.pending())
    write_json(REPO / 'reports/preboard/presentation_pc_check_2026-10-21.json', report)
    if not report['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
