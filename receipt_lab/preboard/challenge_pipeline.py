"""Score the frozen PC pipeline on new, checked photos, before human corrections."""
import argparse
import uuid

from json_extraction_scorer import score, failed_result
from receipt_lab.demo_pc.pipeline import process, PipelineRuntime
from receipt_lab.demo_pc.store import Store
from .common import WORK, read_json, write_json, digest, utc
from .dataset import MANIFEST, validate, fingerprints
from .field_metrics import field_metrics


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-id');args=ap.parse_args()
    selection=WORK/'selection.json'
    if not selection.exists():ap.error('Freeze selection using development results before challenge')
    data=read_json(MANIFEST)
    rows=[r for r in data['records'] if r.get('challenge_candidate') and r['split']=='challenge']
    errors=validate({**data,'records':rows},require_review=True)
    if errors or len(rows)<6 or len({r['transaction_group_id'] for r in rows})<3:
        ap.error('Need six checked new photos / three new transactions: '+'; '.join(errors))
    folder=WORK/'runs'/(args.run_id or 'challenge-pipeline-'+uuid.uuid4().hex[:12])
    if (folder/'manifest.json').exists():ap.error('Choose a new run ID; preserve previous runs')
    manifest={'timestamp':utc(),'purpose':'scored_final_pipeline_challenge','dataset_snapshot':fingerprints(rows),
              'selection_sha256':digest(selection),'expected_attempts':len(rows)*3,
              'score_scope':'raw model output before user correction; operator-selected orientation',
              'human_confirmation_time':None,'human_confirmation_time_note':'No user study; do not substitute automated time'}
    write_json(folder/'manifest.json',manifest)
    store=Store(WORK/'services/challenge.sqlite')
    with PipelineRuntime() as runtime:
        write_json(folder/'runtime-load.json',runtime.load)
        run_warm(rows,store,runtime,folder,manifest)


def run_warm(rows,store,runtime,folder,manifest):
    warmup_id,warmup=process(rows[0]['doc_id'],store,rotation=rows[0]['rotation_to_read'],runtime=runtime)
    write_json(folder/'warmup.json',{'included_in_metrics':False,'receipt_id':warmup_id,'pipeline_run_id':warmup['run_id']})
    attempts=[]
    for rep in range(3):
        for row in rows:
            rid,result=process(row['doc_id'],store,rotation=row['rotation_to_read'],runtime=runtime)
            truth=read_json(WORK/'annotations/adjudicated'/f"{row['doc_id']}.json")['extraction']
            pred=result.get('extraction') if result.get('llm',{}).get('status')=='ok' else None
            scored={'doc_id':row['doc_id'],'transaction_group_id':row['transaction_group_id'],'repetition':rep,
                    'receipt_id':rid,'pipeline_run_id':result['run_id'],'status':result['status'],
                    'score':score(truth,pred) if result.get('llm',{}).get('parse_valid') and result.get('llm',{}).get('status')=='ok' else failed_result(int(result.get('llm',{}).get('parse_valid',False)),['pipeline or extraction failure']),
                    'fields':field_metrics(truth,pred),
                    'measurement':result['processing_measurement'],'configuration':result['configuration'],
                    'stage_measurements':{
                        'detection_and_preprocessing':result.get('detection_and_preprocessing'),
                        'ocr':{k:result.get('ocr',{}).get(k) for k in ['wall_seconds','sampled_peak_rss_bytes','child_peak_rss_bytes','memory_metric']},
                        'llm':result.get('llm',{}).get('measurement')},
                    'runtime_reused':result['runtime_reused']}
            attempts.append(scored)
            write_json(folder/'attempts'/f"{row['doc_id']}-r{rep}.json",scored)
            print(row['doc_id'],rep,scored['score']['f1'],flush=True)
    write_json(folder/'completion.json',{'complete':len(attempts)==manifest['expected_attempts'],'attempts':len(attempts),
              'failures':sum(a['status']!='pending_review' for a in attempts),'accuracy_repetition':0})


if __name__=='__main__':main()
