"""Score the frozen PC pipeline on new, checked photos, before human corrections."""
import argparse
import uuid

from json_extraction_scorer import score, failed_result
from receipt_lab.demo_pc.pipeline import process, PipelineRuntime
from receipt_lab.demo_pc.store import Store
from .common import REPO, WORK, read_json, write_json, digest, utc, environment
from .dataset import MANIFEST, validate, fingerprints
from .field_metrics import field_metrics
from .assets import require_registry
from .metrics import box_iou


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
              'environment':environment(),
              'asset_registry_sha256':require_registry(),
              'selection_sha256':digest(selection),'expected_attempts':len(rows)*3,
              'scorer_sha256':digest(REPO/'json_extraction_scorer.py'),
              'score_scope':'raw model output before user correction; operator-selected orientation',
              'human_confirmation_time':None,'human_confirmation_time_note':'No user study; do not substitute automated time'}
    write_json(folder/'manifest.json',manifest)
    store=Store(WORK/'services/challenge.sqlite')
    with PipelineRuntime() as runtime:
        write_json(folder/'runtime-load.json',runtime.load)
        run_warm(rows,store,runtime,folder,manifest)
    print(folder,flush=True)


def run_warm(rows,store,runtime,folder,manifest):
    warmup_id,warmup=process(rows[0]['doc_id'],store,rotation=rows[0]['rotation_to_read'],runtime=runtime)
    write_json(folder/'warmup.json',{'included_in_metrics':False,'receipt_id':warmup_id,'pipeline_run_id':warmup['run_id']})
    attempts=[]
    for rep in range(3):
        for row in rows:
            rid,result=process(row['doc_id'],store,rotation=row['rotation_to_read'],runtime=runtime)
            truth=read_json(WORK/'annotations/adjudicated'/f"{row['doc_id']}.json")['extraction']
            pred=result.get('extraction') if result.get('llm',{}).get('status')=='ok' else None
            detected_box=result.get('detection_and_preprocessing',{}).get('transform',{}).get('box_original_pixels')
            iou=box_iou(row['original_pixel_boxes'][0],detected_box)
            scored={'doc_id':row['doc_id'],'transaction_group_id':row['transaction_group_id'],'repetition':rep,
                    'receipt_id':rid,'pipeline_run_id':result['run_id'],'status':result['status'],
                    'model_status':result.get('llm',{}).get('status'),
                    'parse_valid':result.get('llm',{}).get('parse_valid',False),
                    'schema_valid':result.get('llm',{}).get('schema_valid',False),
                    'successful_processing':result['status']=='pending_review' and result.get('llm',{}).get('status')=='ok' and result.get('llm',{}).get('schema_valid',False),
                    'detection':{'detected':detected_box is not None,'box_iou':iou,'iou50_success':iou>=0.5,
                                 'scope':'Top-one document crop against owner-confirmed original-image region; not mAP'},
                    'score':score(truth,pred) if result.get('llm',{}).get('parse_valid') and result.get('llm',{}).get('status')=='ok' else failed_result(int(result.get('llm',{}).get('parse_valid',False)),['pipeline or extraction failure']),
                    'fields':field_metrics(truth,pred),
                    'measurement':result['processing_measurement'],'configuration':result['configuration'],
                    'stage_measurements':{
                        'detection_and_preprocessing':result.get('detection_and_preprocessing'),
                        'ocr':{k:result.get('ocr',{}).get(k) for k in ['wall_seconds','sampled_peak_rss_bytes','child_peak_rss_bytes','memory_metric','windows_client_measurement','linux_tesseract_wall_seconds']},
                        'llm':result.get('llm',{}).get('measurement')},
                    'runtime_reused':result['runtime_reused']}
            attempts.append(scored)
            write_json(folder/'attempts'/f"{row['doc_id']}-r{rep}.json",scored)
            print(row['doc_id'],rep,scored['score']['f1'],flush=True)
    write_json(folder/'completion.json',{'complete':len(attempts)==manifest['expected_attempts'],'attempts':len(attempts),
              'failures':sum(not a['successful_processing'] for a in attempts),'accuracy_repetition':0,
              'failure_definition':'Any pipeline failure, failed model request, parse failure or invalid schema; retained in accuracy denominator'})


if __name__=='__main__':main()
