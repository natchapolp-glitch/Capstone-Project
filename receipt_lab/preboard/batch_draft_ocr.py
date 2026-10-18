"""Read all candidate photos for annotation assistance, never create ground truth."""
import re
import argparse

from .common import WORK, read_json, utc, write_json
from .dataset import MANIFEST
from .ocr import OCREngine, prepare_image


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--engine',choices=['tesseract','easyocr'],default='tesseract')
    ap.add_argument('--run-id')
    args=ap.parse_args()
    rows=[r for r in read_json(MANIFEST)["records"] if not r.get('challenge_candidate')]
    priority=read_json(WORK/'annotations/priority_queue.json')['doc_ids']
    rows=sorted(rows,key=lambda r:priority.index(r['doc_id']) if r['doc_id'] in priority else 999)
    run_id=args.run_id or f"draft-{args.engine}-all59-v1"
    if not run_id.replace('-','').replace('_','').isalnum():ap.error('Use a simple run ID')
    folder=WORK/'runs'/run_id
    engine=OCREngine(args.engine)
    for index,row in enumerate(rows,1):
        path=folder/"attempts"/(row["doc_id"]+".json")
        if path.exists():continue
        result={"doc_id":row["doc_id"],"purpose":"unreviewed OCR assistance only; not reference text or accuracy"}
        try:
            mode="reference" if len(row["original_pixel_boxes"])==1 else "full"
            image,transform=prepare_image(row,mode)
            result.update(engine.run(image))
            result["transform"]=transform
            result["date_string_candidates"]=re.findall(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",result["text"])
        except Exception as exc:
            result.update({"status":"failed","text":"","error":str(exc)})
        write_json(path,result)
        print(index,row["doc_id"],result["status"],len(result["text"]),flush=True)
    attempts=[read_json(p) for p in (folder/"attempts").glob("*.json")]
    write_json(folder/"completion.json",{"timestamp":utc(),"expected_doc_ids":sorted(r["doc_id"] for r in rows),
               "actual_doc_ids":sorted(r["doc_id"] for r in attempts),"attempts":len(attempts),
               "failed":sum(r["status"]!="ok" for r in attempts),"accuracy_scored":False})


if __name__=="__main__":main()
