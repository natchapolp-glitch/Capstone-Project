"""Publish aggregate engineering evidence without receipt text or auth credentials."""
import csv
import json
import statistics
from pathlib import Path

from .common import REPO, WORK, digest, environment, read_json, utc, write_json
from .dataset import MANIFEST, annotations, validate


def main():
    output=REPO/"reports/preboard"
    output.mkdir(parents=True,exist_ok=True)
    data=read_json(MANIFEST)
    status={s:sum(r['annotation_status']==s for r in data['records']) for s in sorted({r['annotation_status'] for r in data['records']})}
    human_entries=[e for r in data['records'] for e in annotations(r['doc_id'])
                   if e.get('reviewer_kind')=='human' and e.get('attestation') is True]
    write_json(output/"dataset_audit.json",{"timestamp":utc(),"photo_candidates":len(data['records']),
         "original_photo_candidates":sum(not r.get('challenge_candidate') for r in data['records']),
         "new_challenge_candidates":sum(bool(r.get('challenge_candidate')) for r in data['records']),
         "original_annotation_status_counts":{s:sum(r['annotation_status']==s and not r.get('challenge_candidate') for r in data['records']) for s in status},
         "manifest_sha256":digest(MANIFEST),"original_boxes_present":sum(bool(r['original_pixel_boxes']) for r in data['records']),
         "complex_or_missing_boxes":sum(not r['original_pixel_boxes'] for r in data['records']),"annotation_status_counts":status,
         "unresolved_transaction_groups":sum(r['group_status']!='reviewed' for r in data['records']),
         "human_review_rounds_received":len(human_entries),
         "photos_with_human_entries":len({e['doc_id'] for e in human_entries}),
         "human_round_counts":{s:sum(e['slot']==s for e in human_entries) for s in ['first','second']},
         "structural_errors":validate(data),"review_method":"single_reviewer_double_entry as authorized; AI drafts not human-reviewed"})
    coverage=[]
    expected={r['doc_id'] for r in data['records'] if not r.get('challenge_candidate')}
    for engine in ['tesseract','easyocr']:
        folder=WORK/f'runs/draft-{engine}-all59-v1'
        paths=list((folder/'attempts').glob('*.json'))
        results=[read_json(p) for p in paths]
        actual={r['doc_id'] for r in results}
        coverage.append({'engine':engine,'purpose':'unreviewed annotation assistance, not ground truth or accuracy',
                         'expected_photos':len(expected),'attempted_photos':len(actual),
                         'successful_runs':sum(r['status']=='ok' for r in results),
                         'failed_runs':sum(r['status']!='ok' for r in results),
                         'coverage_complete':actual==expected,'missing_doc_ids':sorted(expected-actual),
                         'unexpected_doc_ids':sorted(actual-expected),'accuracy_scored':False,
                         'raw_evidence_hashes':{p.name:digest(p) for p in paths}})
    write_json(output/'draft_ocr_coverage.json',{'timestamp':utc(),'engines':coverage})
    registry=read_json(WORK/"model_registry.json")
    public_models=[{k:v for k,v in m.items() if k!='path'} for m in registry['models']]
    write_json(output/"runtime_models.json",{"llama_tag":registry['llama_tag'],"binary_archive_sha256":registry['binary_archive_sha256'],"models":public_models,
                "sources":["https://huggingface.co/Qwen/Qwen3-0.6B-GGUF","https://huggingface.co/Qwen/Qwen3-1.7B-GGUF","https://github.com/ggml-org/llama.cpp/releases/tag/"+registry['llama_tag']]})
    private=WORK/"runs/engineering-matrix-real-ocr-v1"
    attempts=[read_json(p) for p in (private/"attempts").glob('*.json')]
    from json_extraction_scorer import strict_json_loads, schema_errors
    reparsed=[]
    for attempt in attempts:
        try:
            value=strict_json_loads(attempt['raw_content']);parsed=True;valid=not schema_errors(value)
        except (ValueError,TypeError):parsed=False;valid=False
        reparsed.append({'attempt_key':attempt['attempt_key'],'parse_valid':parsed,'schema_valid':valid,
                         'changed':parsed!=attempt['parse_valid'] or valid!=attempt['schema_valid']})
    write_json(output/'strict_parser_audit.json',{'timestamp':utc(),'scope':'Post hoc parser audit of preserved engineering output; no model reruns and no accuracy scoring',
               'scorer_sha256':digest(REPO/'json_extraction_scorer.py'),'attempts':len(reparsed),
               'parse_valid':sum(a['parse_valid'] for a in reparsed),'schema_valid':sum(a['schema_valid'] for a in reparsed),
               'changed_attempts':[a['attempt_key'] for a in reparsed if a['changed']]})
    groups={}
    for a in attempts:
        groups.setdefault((a['model']['id'],a['grammar']),[]).append(a)
    summary=[]
    for (model,grammar),rows in sorted(groups.items()):
        times=[r['measurement']['wall_seconds'] for r in rows]
        summary.append({'model':model,'grammar':grammar,'attempts':len(rows),
                        'request_failures':sum(r['status']!='ok' for r in rows),
                        'parse_valid':sum(r['parse_valid'] for r in rows),'schema_valid':sum(r['schema_valid'] for r in rows),
                        'median_seconds':statistics.median(times),'min_seconds':min(times),'max_seconds':max(times),
                        'p95_seconds':statistics.quantiles(times,n=100,method='inclusive')[94] if len(times)>1 else times[0],
                        'percentile_limitation':'Interpolated descriptive p95 from only three repetitions of one transcript; not a population estimate',
                        'sampled_peak_rss_bytes':max(r['measurement']['sampled_peak_rss_bytes'] for r in rows),
                        'accuracy_scored':False})
    write_json(output/"engineering_llm_matrix.json",{'timestamp':utc(),'scope':'one real OCR transcript; engineering evidence only; not extraction accuracy',
         'doc_id':'R3B0A1D27A6DC','source_engine':'Tesseract tha+eng','expected_attempts':24,'actual_attempts':len(attempts),
         'input_hashes':sorted({r['input_text_sha256'] for r in attempts}),'repetitions_per_cell':3,'summary':summary,
         'raw_evidence':str(private),'raw_evidence_hashes':{p.name:digest(p) for p in (private/'attempts').glob('*.json')}})
    with (output/'engineering_llm_matrix.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]) if summary else ['model']);writer.writeheader();writer.writerows(summary)
    ocr=[]
    for engine in ['easyocr','tesseract']:
        for p in (WORK/'ocr'/engine).glob('*-reference.json'):
            r=read_json(p)
            ocr.append({'doc_id':r['doc_id'],'engine':engine,'status':r['status'],'wall_seconds':r['wall_seconds'],
                        'input_sha256':r['input_sha256'],'text_length':len(r['text']),
                        'memory_bytes':r.get('sampled_peak_rss_bytes',r.get('child_peak_rss_bytes')),
                        'memory_metric':r['memory_metric'],'raw_evidence_sha256':digest(p),'accuracy_scored':False})
    write_json(output/'engineering_ocr.json',{'scope':'paired engineering runs on same reference crops; not CER/accuracy; timing not a controlled benchmark',
                                          'runs':ocr})
    delivery=WORK/'runs/delivery-integration/evidence.json'
    if delivery.exists():
        d=read_json(delivery)
        clean={k:d[k] for k in ['timestamp','purpose','event_id','broker_stopped_delivery_failed','repeat_confirmation_same_event',
              'restart_no_pending_event','invalid_schema_blocked','rejected_receipt_status','mqtt_qos','retained_state','delivery_semantics']}
        clean['real_photo_traces']=[{k:v for k,v in r.items() if k!='ha_states'} for r in d.get('real_photo_traces',[])]
        clean['ha_entities']=[s['entity_id'] for s in d['ha_states']]
        clean['private_evidence_sha256']=digest(delivery)
        write_json(output/'delivery_integration.json',clean)
    warm=WORK/'runs/warm-pipeline-engineering-v1/summary.json'
    if warm.exists():
        write_json(output/'warm_pipeline_smoke.json',{**read_json(warm),'raw_evidence_sha256':digest(warm),
                   'limitation':'Two engineering images, one warm-up and one subsequent call, with concurrent OCR workload; not accuracy or a controlled benchmark'})
    env=environment();env.pop('lab_root',None);env.pop('executable',None)
    write_json(output/'environment.json',env)
    print(json.dumps({'report_directory':str(output),'llm_attempts':len(attempts),'ocr_runs':len(ocr),'human_adjudicated':status.get('adjudicated',0)}))


if __name__=='__main__':main()
