"""Both OCR engines use the identical fixed LLM; these are OCR+extractor metrics."""
import argparse
import uuid
from pathlib import Path

from json_extraction_scorer import score, failed_result
from .common import WORK, read_json, write_json, utc, digest
from .dataset import MANIFEST, validate, fingerprints
from .field_metrics import field_metrics
from .llm import LocalLLM
from .experiment import checked_ocr_run


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--split", choices=["development","evaluation","challenge"], required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--ocr-run", type=Path, required=True)
    ap.add_argument("--crop", choices=["reference","predicted"], default="reference")
    args=ap.parse_args()
    data=read_json(MANIFEST)
    rows=[r for r in data["records"] if r["split"]==args.split]
    errors=validate({**data,"records":rows},require_review=True)
    if not rows or errors:
        ap.error("No complete reviewed split: "+"; ".join(errors))
    source_run=checked_ocr_run(args.ocr_run,rows,args.split)
    selection=WORK/'selection.json'
    if args.split!='development':
        if not selection.exists() or read_json(selection)['model_id']!=args.model:
            ap.error('Use the model frozen from development before evaluation/challenge')
    folder=WORK/"runs"/("ocr-fields-"+uuid.uuid4().hex[:12])
    write_json(folder/"manifest.json",{"timestamp":utc(),"dataset_sha256":digest(MANIFEST),"dataset_snapshot":fingerprints(rows),"split":args.split,
               "purpose":"scored_ocr_fields_with_fixed_extractor","model":args.model,
               "ocr_run":str(source_run),"ocr_completion_sha256":digest(source_run/'completion.json'),
               "selection_sha256":digest(selection) if selection.exists() else None,
               "engines":["easyocr","tesseract"],"grammar":True,"expected_attempts":len(rows)*2,
               "metric_scope":"OCR followed by same fixed local extractor; not isolated OCR field accuracy"})
    with LocalLLM(args.model) as llm:
        for row in rows:
            doc=row["doc_id"];truth=read_json(WORK/"annotations/adjudicated"/f"{doc}.json")["extraction"]
            for engine in ["easyocr","tesseract"]:
                path=source_run/'attempts'/f"{doc}-{engine}-{args.crop}-r0.json"
                source=read_json(path) if path.exists() else {"text":"","status":"missing_output"}
                result=llm.extract(source["text"],grammar=True)
                result["doc_id"]=doc;result["engine"]=engine
                result['source_evidence_sha256']=digest(path) if path.exists() else None
                pred=result["parsed_output"] if result["status"]=="ok" and source["status"]=="ok" else None
                result["fields"]=field_metrics(truth,pred)
                result["score"]=score(truth,pred) if result['parse_valid'] and result['status']=='ok' and source['status']=='ok' else failed_result(int(result['parse_valid']),['upstream or extraction failure'])
                write_json(folder/f"{doc}-{engine}.json",result)
                print(doc,engine,result["score"]["f1"],flush=True)
    actual=[read_json(folder/f"{r['doc_id']}-{engine}.json") for r in rows for engine in ['easyocr','tesseract']]
    write_json(folder/'completion.json',{'complete':len(actual)==len(rows)*2,'attempts':len(actual),
               'expected_attempts':len(rows)*2,'doc_ids':sorted(r['doc_id'] for r in rows),'accuracy_scored':True})


if __name__=="__main__":main()
