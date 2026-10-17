"""Private 59-photo orientation audit and reproducible skew screening.

The 90-degree orientations were visually reviewed from five private contact
sheets. Skew is estimated only where an existing single-document label exists.
No result here is a human-annotated text-baseline angle.
"""

import csv
import json
import statistics
from pathlib import Path

import cv2

from estimate_skew_projection_16 import crop_receipt, orientation, score_mask


LAB = Path.home() / "SeminarLab"
ROOT = LAB / "reports" / "orientation_skew_59"
CCW = {"R3B0A1D27A6DC", "RB1F19C1AB1E8", "R7698BF78B650",
       "RBAAD3F24CE23", "R74946CAAC57E", "R1C29238ED9D6"}
CW = {"R39A145C0C88A", "RF5483BD7E12A", "R1C26C140E415",
      "RDA6DF077D838", "R126F88D04CB4", "RE3563918095B",
      "RC0CFE64586A9", "RCF5E8E6822D9", "R6107E8387EF8",
      "R1A0DCC9ADD0C", "RD199D9E46819", "RF96D447DC21E"}
LABEL_ROOTS = [LAB / "yolo_expanded" / "train" / "labels",
               LAB / "yolo_expanded" / "val" / "labels",
               LAB / "external_scene_6" / "labels"]


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = [r for r in csv.DictReader((LAB / "reports" / "manifest.csv").open(encoding="utf-8-sig", newline=""))
                if not r["duplicate_of"] and r["doc_type"] == "itemized_purchase"]
    assert len(manifest) == 59 and len(CCW | CW) == 18
    assert (CCW | CW) <= {r["doc_id"] for r in manifest}
    files = {p.name: p for p in (LAB / "incoming").rglob("*") if p.is_file()}
    labels = {p.stem: p for root in LABEL_ROOTS for p in root.glob("*.txt")}
    rows = []
    for number, row in enumerate(manifest, 1):
        source = files[row["filename"]]
        frame = cv2.imread(str(source))
        assert frame is not None, source
        label = labels.get(row["doc_id"]) or labels.get(source.stem)
        crop = crop_receipt(frame, label) if label else frame
        direction = "ccw" if row["doc_id"] in CCW else "cw" if row["doc_id"] in CW else "none"
        if direction == "ccw":
            crop = cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif direction == "cw":
            crop = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)
        # Keep review crops private. They may contain names or payment details.
        cv2.imwrite(str(ROOT / f"{row['doc_id']}_upright_crop.jpg"), crop)
        if label:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            best, score0, _ = orientation(score_mask(gray))
            angle = best[0]
            improvement = round((best[1] / score0 - 1) * 100, 2)
        else:
            angle = None
            improvement = None
        rows.append({"index": number, "doc_id": row["doc_id"],
                     "filename": row["filename"], "condition": row["condition"],
                     "single_document_label": bool(label),
                     "rotation_to_read": direction,
                     "rotation_to_align_text_deg": angle,
                     "score_improvement_vs_0_pct": improvement,
                     "notes": row["notes"]})
        print(number, row["doc_id"], direction, angle, flush=True)
    assert len(rows) == 59 and sum(r["single_document_label"] for r in rows) == 54
    (ROOT / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    printed = [abs(r["rotation_to_align_text_deg"]) for r in rows
               if r["single_document_label"] and r["condition"] != "handwritten"]
    handwritten = [abs(r["rotation_to_align_text_deg"]) for r in rows
                   if r["single_document_label"] and r["condition"] == "handwritten"]
    summary = {"unique_itemized_candidates": len(rows),
               "orientation_readable_none": sum(r["rotation_to_read"] == "none" for r in rows),
               "orientation_readable_cw": sum(r["rotation_to_read"] == "cw" for r in rows),
               "orientation_readable_ccw": sum(r["rotation_to_read"] == "ccw" for r in rows),
               "skew_estimated_single_label": sum(r["single_document_label"] for r in rows),
               "skew_not_estimated_complex_photo": sum(not r["single_document_label"] for r in rows),
               "printed_skew_n": len(printed),
               "printed_median_absolute_alignment_deg": statistics.median(printed),
               "handwritten_form_skew_n": len(handwritten),
               "handwritten_form_median_absolute_alignment_deg": statistics.median(handwritten),
               "warning": "Automatic projection angles on line-grid forms measure printed rules more than handwritten text. Printed-paper angles are exploratory and lack human angle ground truth."}
    (ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
