"""Both OCR engines use the identical fixed LLM; these are OCR+extractor metrics."""
import argparse
import uuid
import random
from itertools import product
from pathlib import Path

from json_extraction_scorer import score, failed_result
from .common import REPO, WORK, read_json, write_json, utc, digest, environment
from .dataset import MANIFEST, validate, fingerprints
from .field_metrics import field_metrics
from .llm import LocalLLM
from .experiment import checked_ocr_run
from .assets import require_registry


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--split", choices=["development","evaluation","challenge"], required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--ocr-run", type=Path, required=True)
    ap.add_argument("--crop", choices=["reference","predicted","both"], default="both")
    ap.add_argument('--repetitions',type=int,default=3)
    ap.add_argument('--run-id')
    args=ap.parse_args()
    if args.repetitions<1:ap.error('repetitions must be positive')
    data=read_json(MANIFEST)
    source_ids=read_json(args.ocr_run/'manifest.json')['doc_ids']
    rows=[r for r in data["records"] if r["split"]==args.split and r['doc_id'] in source_ids]
    errors=validate({**data,"records":rows},require_review=True)
    if not rows or errors:
        ap.error("No complete reviewed split: "+"; ".join(errors))
    source_run=checked_ocr_run(args.ocr_run,rows,args.split)
    selection=WORK/'selection.json'
    if args.split!='development':
        if not selection.exists() or read_json(selection)['model_id']!=args.model:
            ap.error('Use the model frozen from development before evaluation/challenge')
        chosen=read_json(selection)
        for key,path in [('model_registry_sha256',WORK/'model_registry.json'),('scorer_sha256',REPO/'json_extraction_scorer.py'),('schema_sha256',REPO/'receipt_schema.json'),('llm_driver_sha256',REPO/'receipt_lab/preboard/llm.py')]:
            if chosen.get(key)!=digest(path):ap.error('Frozen extractor version changed: '+key)
    folder=WORK/"runs"/(args.run_id or "ocr-fields-"+uuid.uuid4().hex[:12])
    engines=['easyocr','tesseract'];modes=['reference','predicted'] if args.crop=='both' else [args.crop]
    jobs=list(product(rows,engines,modes,range(args.repetitions)))
    sources={};hashes={}
    for row,engine,mode,_ in jobs:
        key=f"{row['doc_id']}-{engine}-{mode}"
        path=source_run/'attempts'/(key+'-r0.json')
        hashes[key]=digest(path) if path.exists() else None
        sources[key]=read_json(path) if path.exists() else {'text':'','status':'missing_output'}
    manifest={"timestamp":utc(),"dataset_sha256":digest(MANIFEST),"dataset_snapshot":fingerprints(rows),"split":args.split,
               "purpose":"scored_ocr_fields_with_fixed_extractor","model":args.model,
               'environment':environment(),'ocr_source_hashes':hashes,'modes':modes,'repetitions':args.repetitions,
               'asset_registry_sha256':require_registry(),
               "ocr_run":str(source_run),"ocr_completion_sha256":digest(source_run/'completion.json'),
               "selection_sha256":digest(selection) if selection.exists() else None,
               'scorer_sha256':digest(REPO/'json_extraction_scorer.py'),
               'driver_sha256':{name:digest(REPO/'receipt_lab/preboard'/name) for name in ['evaluate_ocr_fields.py','llm.py','field_metrics.py']},
               "engines":engines,"grammar":True,"expected_attempts":len(jobs),
               'timing_scope':'Fixed extractor only; OCR times are in the paired OCR benchmark',
               "metric_scope":"OCR followed by same fixed local extractor; not isolated OCR field accuracy"}
    if (folder/'manifest.json').exists():
        old=read_json(folder/'manifest.json')
        for key in ['dataset_snapshot','ocr_source_hashes','selection_sha256','scorer_sha256','model','modes','engines','repetitions','driver_sha256','asset_registry_sha256']:
            if old.get(key)!=manifest[key]:ap.error('Cannot resume changed inputs/config/code; preserve old evidence and use a new run ID')
    else:write_json(folder/'manifest.json',manifest)
    def job_key(row,engine,mode,rep):return f"{row['doc_id']}-{engine}-{mode}-r{rep}"
    random.Random(20261018).shuffle(jobs)
    pending=[job for job in jobs if not (folder/'attempts'/(job_key(*job)+'.json')).exists()]
    if pending:
        session=folder/'sessions'/uuid.uuid4().hex
        with LocalLLM(args.model) as llm:
            write_json(session/'load-fixed-extractor.json',llm.load)
            write_json(session/'warmup.json',{'synthetic':True,'included_in_metrics':False,
                       **llm.extract('RECEIPT\nSAMPLE SHOP\nMilk 1 20.00\nTOTAL 20.00 THB',grammar=True)})
            for row,engine,mode,rep in pending:
                doc=row['doc_id'];truth=read_json(WORK/'annotations/adjudicated'/f'{doc}.json')['extraction']
                key=f'{doc}-{engine}-{mode}';source=sources[key]
                result=llm.extract(source["text"],grammar=True)
                result["doc_id"]=doc;result["engine"]=engine
                result['mode']=mode;result['repetition']=rep;result['attempt_key']=job_key(row,engine,mode,rep)
                result['upstream_status']=source['status']
                result['source_evidence_sha256']=hashes[key]
                pred=result["parsed_output"] if result["status"]=="ok" and source["status"]=="ok" else None
                result["fields"]=field_metrics(truth,pred)
                result["score"]=score(truth,pred) if result['parse_valid'] and result['status']=='ok' and source['status']=='ok' else failed_result(int(result['parse_valid']),['upstream or extraction failure'])
                write_json(folder/'attempts'/(result['attempt_key']+'.json'),result)
                print(result['attempt_key'],result["score"]["f1"],flush=True)
    actual=[read_json(p) for p in (folder/'attempts').glob('*.json')]
    expected={job_key(*job) for job in jobs};keys=[r['attempt_key'] for r in actual]
    write_json(folder/'completion.json',{'complete':set(keys)==expected and len(keys)==len(expected),'attempts':len(actual),
               'expected_attempts':len(jobs),'doc_ids':sorted(r['doc_id'] for r in rows),'accuracy_scored':True,
               'accuracy_repetition':0,'failed_inputs_or_requests':sum(r['status']!='ok' or r['upstream_status']!='ok' for r in actual)})
    print(folder,flush=True)


if __name__=="__main__":main()
