"""Add new real-photo candidates without promoting duplicates or annotations."""
import argparse
import hashlib
import io
import shutil
from pathlib import Path

from .common import WORK, digest, read_json, utc, write_json
from .dataset import MANIFEST, dhash


def main():
    from PIL import Image, ImageOps
    ap=argparse.ArgumentParser()
    ap.add_argument("directory",type=Path)
    args=ap.parse_args()
    data=read_json(MANIFEST)
    hashes={h for r in data["records"] for h in [r["sha256"],r.get('original_sha256')] if h}
    reports=[]
    for path in sorted(args.directory.rglob("*")):
        if path.suffix.lower() not in {".jpg",".jpeg",".png",".webp"} or not path.is_file():continue
        sha=digest(path)
        if sha in hashes:
            reports.append({"file":path.name,"status":"exact_duplicate_rejected"});continue
        doc="R"+sha[:12].upper()
        # Browser, labels and OCR must share the same pixel frame, including phone EXIF orientation.
        normalized=WORK/'dataset/new_photos'/(doc+'.png')
        with Image.open(path) as im:
            orientation=im.getexif().get(274,1)
            upright=ImageOps.exif_transpose(im).convert('RGB')
            w,h=upright.size
            upright.info.clear()
            encoded=io.BytesIO();upright.save(encoded,format='PNG')
        normalized_sha=hashlib.sha256(encoded.getvalue()).hexdigest()
        if normalized_sha in hashes:
            reports.append({'file':path.name,'status':'normalized_pixel_duplicate_rejected'});continue
        normalized.parent.mkdir(parents=True,exist_ok=True)
        normalized.write_bytes(encoded.getvalue())
        original=normalized.with_name(doc+'.original'+path.suffix.lower())
        shutil.copy2(path,original)
        if digest(original)!=sha:raise ValueError('Source changed during intake')
        data["records"].append({"doc_id":doc,"source":str(normalized.resolve()),"sha256":normalized_sha,"width":w,"height":h,
             'original_source':str(original.resolve()),'original_sha256':sha,
             'pixel_frame':'EXIF-transposed RGB PNG; boxes refer to these normalized original-image pixels',
             'original_exif_orientation':orientation,
             "store":"unreviewed","condition":"unreviewed_new_scene","doc_type":"unreviewed",
             "original_pixel_boxes":[],"box_status":"needs_review","bbox_exclusion_reason":"New photo requires region labels",
             "rotation_to_read":"none","rotation_source":"unreviewed","historical_yolo_split":"not_previously_seen",
             "transaction_group_id":None,"group_status":"unresolved","split":"unassigned","annotation_status":"not_started",
             "prior_item_name_status":"not_started","prior_item_name_fragments":[],"notes":"New challenge candidate; do not tune on this photo",
             "challenge_candidate":True,"intake_at":utc()})
        hashes.update([sha,normalized_sha])
        reports.append({"doc_id":doc,"status":"awaiting_source_conditions_group_review_and_truth","file":path.name})
    if any(r.get("doc_id") for r in reports):
        data["version"]+=1
        write_json(MANIFEST,data)
    write_json(WORK/"dataset/challenge_intake.json",{"timestamp":utc(),"files":reports})
    print(reports)


if __name__=="__main__":main()
