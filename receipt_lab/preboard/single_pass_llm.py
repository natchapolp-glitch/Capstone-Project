"""Actual LLM reliability/timing matrix using owner text; no semantic accuracy claim."""
import argparse
import itertools
import random
import statistics
import uuid

from .common import REPO, WORK, digest, environment, object_hash, read_json, utc, write_json
from .llm import LocalLLM


def select_samples(snapshot, count):
    # Deterministic length strata, chosen without looking at CER or LLM responses.
    rows = sorted((r for r in snapshot['records'] if not r['exclusion_reasons']
                   and r['crop_mode'] == 'reference' and r['predictions']['tesseract']['scope_matches']),
                  key=lambda r: (len(r['entry']['transcript']), r['doc_id']))
    if count < 2 or count > len(rows):
        raise ValueError('Choose 2..available single-document references')
    selected = [rows[round(i * (len(rows)-1)/(count-1))] for i in range(count)]
    samples = []
    for r in selected:
        for kind in ['owner_text', 'tesseract']:
            text = r['entry']['transcript'] if kind == 'owner_text' else r['predictions']['tesseract']['text']
            samples.append({'doc_id': r['doc_id'], 'source_kind': kind, 'text': text,
                            'text_sha256': object_hash(text), 'reference_entry_sha256': r['entry_sha256'],
                            'source_status': 'ok' if kind == 'owner_text' else r['predictions']['tesseract']['status'],
                            'declared_assistance': r['entry'].get('model_assisted_first_entry', False)})
    return samples


def publish(folder):
    manifest = read_json(folder/'manifest.json')
    rows = [read_json(p) for p in (folder/'attempts').glob('*.json')]
    expected = {f"{s['doc_id']}-{s['source_kind']}-{m}-{'grammar' if g else 'free'}-r{rep}"
                for s,m,g,rep in itertools.product(manifest['samples'], manifest['models'], [True,False], range(manifest['repetitions']))}
    actual = [r['attempt_key'] for r in rows]
    groups = []
    for m, source, grammar in itertools.product(manifest['models'], ['owner_text','tesseract'], [True,False]):
        group = [r for r in rows if r['model']['id']==m and r['source_kind']==source and r['grammar']==grammar]
        if not group:
            continue
        times = [r['measurement']['wall_seconds'] for r in group]
        groups.append({'model':m, 'source':source, 'grammar':grammar, 'attempts':len(group),
                       'photos':len({r['doc_id'] for r in group}),
                       'parse_valid':sum(r['parse_valid'] for r in group),
                       'schema_valid':sum(r['schema_valid'] for r in group),
                       'request_failures':sum(r['status']!='ok' for r in group),
                       'median_seconds':statistics.median(times), 'min_seconds':min(times), 'max_seconds':max(times),
                       'max_model_process_tree_rss_bytes':max(r['measurement']['sampled_peak_rss_bytes'] for r in group),
                       'semantic_accuracy':None})
    report = {'timestamp':utc(), 'purpose':manifest['purpose'],
              'manifest_sha256':digest(folder/'manifest.json'), 'snapshot_sha256':manifest['snapshot_sha256'],
              'expected_attempts':len(expected), 'attempts':len(rows),
              'complete':set(actual)==expected and len(actual)==len(expected),
              'missing_attempts':sorted(expected-set(actual)), 'unexpected_attempts':sorted(set(actual)-expected),
              'photo_ids':sorted({s['doc_id'] for s in manifest['samples']}),
              'semantic_accuracy':None, 'groups':groups,
              'limitations':manifest['limitations'],
              'evidence': [{'attempt_key':r['attempt_key'], 'sha256':digest(folder/'attempts'/(r['attempt_key']+'.json'))} for r in rows]}
    write_json(folder/'completion.json', report)
    write_json(REPO/'reports/preboard/single_pass_llm.json', report)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default='single-pass-llm-v2')
    ap.add_argument('--snapshot-run', default='single-pass-owner-v2')
    ap.add_argument('--documents', type=int, default=6)
    ap.add_argument('--repetitions', type=int, default=3)
    ap.add_argument('--publish-only', action='store_true')
    args = ap.parse_args()
    if any(not name.replace('-','').replace('_','').isalnum() for name in [args.run_id,args.snapshot_run]):
        ap.error('Use simple run IDs')
    folder = WORK/'runs'/args.run_id
    if args.publish_only:
        print(publish(folder)['attempts']); return
    if args.repetitions < 1:
        ap.error('Positive repetitions required')
    snapshot_path = WORK/'runs'/args.snapshot_run/'snapshot.json'
    registry = read_json(WORK/'model_registry.json')
    samples = select_samples(read_json(snapshot_path), args.documents)
    config = {'purpose':'actual_llm_schema_reliability_and_pc_cost_no_semantic_accuracy',
              'snapshot_sha256':digest(snapshot_path), 'models':[r['id'] for r in registry['models']],
              'model_registry_sha256':digest(WORK/'model_registry.json'),
              'schema_sha256':digest(REPO/'receipt_schema.json'), 'repetitions':args.repetitions,
              'source_sha256':{name:digest(REPO/name) for name in ['receipt_lab/preboard/single_pass_llm.py',
                              'receipt_lab/preboard/llm.py','json_extraction_scorer.py']},
              'samples':samples, 'selection':'Evenly spaced length ranks among saved single-document transcripts; fixed before model outputs',
              'limitations':['Not a held-out set; existing photos and single-pass transcripts.',
                             'Six length-stratified photos are not all 59 and not verified distinct transactions.',
                             'Tesseract fixed from prior demo configuration, not selected by current CER.',
                             'Parse/schema validity does not establish content accuracy; structured reference is unreviewed.',
                             'Q4_K_M requantized from publisher Q8_0, not original BF16.',
                             'Repeated deterministic calls are timing samples, not independent photos.']}
    if (folder/'manifest.json').exists():
        old = read_json(folder/'manifest.json')
        if any(old.get(k)!=v for k,v in config.items()):
            raise ValueError('Changed input/config/code: use another run ID')
    else:
        write_json(folder/'manifest.json', {**config, 'created_at':utc(), 'environment':environment()})
    rng = random.Random(20261018)
    models = config['models'][:]; rng.shuffle(models)
    session = folder/'sessions'/uuid.uuid4().hex
    for model in models:
        jobs = list(itertools.product(samples,[True,False],range(args.repetitions))); rng.shuffle(jobs)
        def key(s,g,rep):
            return f"{s['doc_id']}-{s['source_kind']}-{model}-{'grammar' if g else 'free'}-r{rep}"
        if all((folder/'attempts'/(key(*j)+'.json')).exists() for j in jobs):
            continue
        with LocalLLM(model) as llm:
            write_json(session/(model+'-load.json'), llm.load)
            warm = llm.extract(samples[0]['text'], grammar=True)
            write_json(session/(model+'-warmup.json'), {**warm,'included_in_metrics':False})
            for s,g,rep in jobs:
                attempt = key(s,g,rep); path = folder/'attempts'/(attempt+'.json')
                if path.exists():
                    continue
                result = llm.extract(s['text'], grammar=g)
                result.update({'attempt_key':attempt, 'doc_id':s['doc_id'], 'source_kind':s['source_kind'],
                               'repetition':rep, 'source_status':s['source_status'],
                               'accuracy_scored':False, 'semantic_accuracy':None, 'purpose':config['purpose']})
                write_json(path, result)
                print(attempt,result['status'],result['schema_valid'],round(result['measurement']['wall_seconds'],2),flush=True)
        publish(folder)
    report = publish(folder)
    print('complete',report['complete'],'attempts',report['attempts'],flush=True)


if __name__ == '__main__':
    main()
