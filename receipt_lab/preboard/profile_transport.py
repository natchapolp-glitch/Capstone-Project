"""Engineering timing across the PC pipeline, surrogate confirmation, MQTT and HA."""
import argparse
import json
import random
import subprocess
import time
import uuid
from contextlib import nullcontext
from decimal import Decimal

from json_extraction_scorer import schema_errors
from receipt_lab.demo_pc.pipeline import PipelineRuntime, process
from receipt_lab.demo_pc.store import Store, publish_pending
from .aggregate import distribution
from .assets import require_registry
from .common import REPO, WORK, Measurement, read_json, write_json, digest, utc, environment
from .dataset import MANIFEST
from .ocr import wsl_path
from .services import access_token, request

ENTITIES=('sensor.seminar_latest_purchase_total','sensor.seminar_latest_item_count')


class ServiceProbe:
    def __init__(self):
        self.process=subprocess.Popen(['wsl','-d','Ubuntu','--exec','python3',wsl_path(REPO/'receipt_lab/preboard/service_probe.py')],
                                     stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        ready=json.loads(self.process.stdout.readline())
        if not ready['ready']:
            self.close();raise RuntimeError('Experimental Linux service PIDs not live: '+str(ready['missing']))

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.write('stop\n');self.process.stdin.flush()
        output,error=self.process.communicate(timeout=10)
        if self.process.returncode:raise RuntimeError('Linux service probe failed: '+error[-500:])
        return json.loads(output.splitlines()[-1])


def check_states(states,extraction):
    by_id={s['entity_id']:s for s in states}
    if set(by_id)!=set(ENTITIES):return False
    total=by_id[ENTITIES[0]]['state'];count=by_id[ENTITIES[1]]['state']
    try:
        total_ok=total.lower() in {'unknown','unavailable','none'} if extraction['grand_total'] is None else Decimal(total)==Decimal(str(extraction['grand_total']))
        return total_ok and Decimal(count)==len(extraction['items'])
    except (ValueError,ArithmeticError):return False


def trial(example,rep,folder,source,rows,token,runtime,warmup=False):
    name=('warmup' if warmup else f"{example['doc_id']}-r{rep}")
    store=Store(folder/(name+'.sqlite'))
    record={'doc_id':example['doc_id'],'repetition':rep,'warmup':warmup,'source_pipeline_id':example['id'],
            'human_confirmation_time':None,'confirmation_actor':'automated_engineering_surrogate_not_human_ground_truth',
            'scope':'Image to HA, models resident; human confirmation replaced only in isolated engineering test' if runtime else 'Stored real model output to HA; no repeated inference'}
    probe=ServiceProbe();observed=[];event=None
    try:
        with Measurement() as full:
            began=time.perf_counter()
            try:
                if runtime:
                    rid,pipeline=process(example['doc_id'],store,rotation=rows[example['doc_id']]['rotation_to_read'],runtime=runtime)
                    record['pipeline_run_id']=pipeline['run_id']
                    record['model_processing']=pipeline['processing_measurement']
                    record['stage_measurements']={
                        'detection_and_preprocessing':pipeline.get('detection_and_preprocessing'),
                        'ocr':{k:pipeline.get('ocr',{}).get(k) for k in ['wall_seconds','child_peak_rss_bytes','memory_metric','windows_client_measurement','linux_tesseract_wall_seconds']},
                        'llm':pipeline.get('llm',{}).get('measurement')}
                    if pipeline['status']!='pending_review' or pipeline.get('llm',{}).get('status')!='ok':raise RuntimeError('Pipeline failed before confirmation')
                else:
                    pipeline=source.get(example['id'])['raw_result'];rid=store.add(example['doc_id'],pipeline)
                extraction=pipeline['extraction']
                if schema_errors(extraction):raise RuntimeError('Invalid extraction is not published')
                with Measurement() as confirmation:
                    event=store.confirm(rid,extraction,'automated_engineering_surrogate_not_human_ground_truth',0)
                record['confirmation_persist']=confirmation.result
                publication_start=time.perf_counter()
                delivered=publish_pending(store,profile=True)
                record['mqtt']=delivered
                if len(delivered)!=1 or delivered[0]['error']:raise RuntimeError('MQTT did not acknowledge the one expected event')
                deadline=time.monotonic()+15;polls=0
                while time.monotonic()<deadline:
                    states=request('/api/states',token=token);polls+=1
                    observed=[s for s in states if s['entity_id'] in ENTITIES and s['attributes'].get('event_id')==event]
                    if len(observed)==2:break
                    time.sleep(.05)
                now=time.perf_counter()
                record.update(publish_to_ha_observed_seconds=now-publication_start,
                              automated_window_to_ha_observed_seconds=now-began,ha_poll_count=polls,
                              ha_value_checks=check_states(observed,extraction))
                if not record['ha_value_checks']:raise RuntimeError('HA state missing or does not match confirmed total/item count')
                record['status']='ok'
            except Exception as error:
                record.update(status='failed',error=str(error))
        record['full_automated_host_measurement']=full.result
    finally:
        record['linux_service_measurement']=probe.close()
    record['event_id']=event
    record['ha_entities']=[s['entity_id'] for s in observed]
    write_json(folder/(name+'.json'),{**record,'ha_states':observed})
    print(name,record['status'],round(record.get('automated_window_to_ha_observed_seconds',0),3),flush=True)
    return record


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--transport-only',action='store_true');ap.add_argument('--repetitions',type=int,default=3);ap.add_argument('--run-id');args=ap.parse_args()
    if args.repetitions<1:ap.error('repetitions must be positive')
    folder=WORK/'runs'/(args.run_id or 'pc-delivery-profile-'+uuid.uuid4().hex[:12])
    if (folder/'manifest.json').exists():ap.error('Preserve previous timing evidence; choose a new run ID')
    source=Store(WORK/'services/demo.sqlite')
    examples=read_json(WORK/'runs/demo-engineering-v2/records.json')
    if len({e['doc_id'] for e in examples})!=len(examples):raise ValueError('Source photo IDs must be distinct')
    rows={r['doc_id']:r for r in read_json(MANIFEST)['records']}
    for example in examples:
        raw=source.get(example['id'])['raw_result']
        if raw.get('llm',{}).get('status')!='ok' or schema_errors(raw.get('extraction')):raise ValueError('Source must be a successful real pipeline, never a fixture')
    import psutil
    concurrent=any('receipt_lab.preboard.batch_draft_ocr' in (p.info['cmdline'] or []) for p in psutil.process_iter(['cmdline']))
    manifest={'timestamp':utc(),'purpose':'engineering PC/transport timing only; no accuracy or user-study claim','environment':environment(),
              'driver_sha256':{str(path.relative_to(REPO)):digest(path) for path in [
                  *(REPO/'receipt_lab/preboard'/name for name in ['profile_transport.py','service_probe.py','ocr.py','wsl_tesseract.py','tesseract_tsv.py','assets.py','llm.py','common.py']),
                  REPO/'receipt_lab/demo_pc/pipeline.py',REPO/'receipt_lab/demo_pc/store.py',REPO/'json_extraction_scorer.py',REPO/'receipt_schema.json']},
              'model_registry_sha256':digest(WORK/'model_registry.json'),
              'system_cpu_percent_before':psutil.cpu_percent(interval=1),
              'asset_registry_sha256':require_registry(),'transport_only':args.transport_only,'repetitions':args.repetitions,
              'source_photos':len(examples),'expected_attempts':len(examples)*args.repetitions,'concurrent_ocr_assistance':concurrent,
              'source_doc_ids':[e['doc_id'] for e in examples],
              'source_example_manifest_sha256':digest(WORK/'runs/demo-engineering-v2/records.json'),
              'latency_note':'HA observed latency includes HTTP polling and is an observation bound, not exact HA processing time',
              'memory_note':'Windows host/client and Linux HA/broker service-tree RSS are separate; never sum across these metrics',
              'human_confirmation_time':None,'review_method':'No human review in this engineering timing experiment'}
    write_json(folder/'manifest.json',manifest)
    token=access_token();attempts=[]
    with (nullcontext(None) if args.transport_only else PipelineRuntime()) as runtime:
        if runtime:
            write_json(folder/'model-startup.json',runtime.load)
            manifest['configuration']=runtime.configuration;write_json(folder/'manifest.json',manifest)
        warmup=trial(examples[0],-1,folder,source,rows,token,runtime,True)
        if warmup['status']!='ok':raise RuntimeError('Warm-up failed; measured warm trials were not started')
        jobs=[(e,rep) for e in examples for rep in range(args.repetitions)];random.Random(20261018).shuffle(jobs)
        for example,rep in jobs:attempts.append(trial(example,rep,folder,source,rows,token,runtime))
    summaries={}
    for name in ['publish_to_ha_observed_seconds','automated_window_to_ha_observed_seconds']:
        summaries[name]={**distribution([a.get(name) for a in attempts]),'missing':sum(a.get(name) is None for a in attempts)}
    for name in ['ha','broker']:
        summaries[name+'_linux_service_rss_bytes']=distribution([a['linux_service_measurement']['services'][name]['sampled_peak_rss_bytes'] for a in attempts])
    summaries['windows_full_host_rss_bytes']=distribution([a['full_automated_host_measurement']['sampled_peak_rss_bytes'] for a in attempts])
    # Different process boundaries are kept explicit; these RSS values are not additive.
    stage_paths={
        'detection_and_preprocessing':('stage_measurements','detection_and_preprocessing'),
        'ocr_windows_client':('stage_measurements','ocr','windows_client_measurement'),
        'llm_server':('stage_measurements','llm'),
        'confirmation_persist_surrogate':('confirmation_persist',),
    }
    stages={}
    for name,keys in stage_paths.items():
        measurements=[]
        for attempt in attempts:
            value=attempt
            for key in keys:value=(value or {}).get(key)
            measurements.append(value or {})
        stages[name]={metric:{**distribution([m.get(metric) for m in measurements]),
                             'missing':sum(m.get(metric) is None for m in measurements)}
                      for metric in ['wall_seconds','sampled_peak_rss_bytes']}
    linux=[(a.get('stage_measurements') or {}).get('ocr') or {} for a in attempts]
    stages['ocr_linux_child']={metric:{**distribution([m.get(source) for m in linux]),
                                     'missing':sum(m.get(source) is None for m in linux)}
                              for metric,source in [('wall_seconds','linux_tesseract_wall_seconds'),('child_peak_rss_bytes','child_peak_rss_bytes')]}
    mqtt=[((a.get('mqtt') or [{}])[0].get('measurement') or {}) for a in attempts]
    stages['mqtt_client']={metric:{**distribution([m.get(metric) for m in mqtt]),
                                  'missing':sum(m.get(metric) is None for m in mqtt)}
                           for metric in ['wall_seconds','sampled_peak_rss_bytes']}
    report={'timestamp':utc(),'run_id':folder.name,'purpose':manifest['purpose'],'source_photos':len(examples),'attempts':len(attempts),
            'configuration':manifest.get('configuration'),
            'failures':sum(a['status']!='ok' for a in attempts),'transport_only':args.transport_only,'concurrent_ocr_assistance':concurrent,
            'summaries':summaries,'stage_summaries':stages,'human_confirmation_time':None,'latency_note':manifest['latency_note'],'memory_note':manifest['memory_note'],
            'uncertainty':'Repeated deliveries are not independent transactions; small-sample p95 is descriptive only.',
            'raw_evidence_sha256':{f"{a['doc_id']}-r{a['repetition']}.json":digest(folder/f"{a['doc_id']}-r{a['repetition']}.json") for a in attempts},
            'traces':[{k:a[k] for k in ['doc_id','repetition','pipeline_run_id','event_id','status','ha_entities','ha_value_checks']} if 'pipeline_run_id' in a and a['status']=='ok' else {k:a[k] for k in ['doc_id','repetition','event_id','status','ha_entities']} for a in attempts]}
    write_json(folder/'completion.json',{'complete':len(attempts)==manifest['expected_attempts'],'failures':report['failures']})
    write_json(folder/'summary.json',report)
    report['manifest_sha256']=digest(folder/'manifest.json');report['private_summary_sha256']=digest(folder/'summary.json')
    write_json(REPO/'reports/preboard/pc_transport_profile.json',report)
    print(folder,flush=True)


if __name__=='__main__':main()
