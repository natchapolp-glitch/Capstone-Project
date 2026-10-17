"""Focused 10+6 photo audit: visual orientation and OCR-script proxy.

The 0/90 orientation labels were checked against the existing private review
contact sheets. Thai/Latin shares count characters in uncorrected EasyOCR
output, so they are not a language ground truth or a causal explanation of mAP.
"""

import json
import statistics
import time
from pathlib import Path

import cv2
import easyocr
import torch


LAB = Path.home() / "SeminarLab"
OUT = LAB / "ocr_outputs" / "orientation_language_16"
VAL = LAB / "yolo_expanded" / "val" / "images"
LATER = LAB / "external_scene_6" / "images"

# Visual reading orientation, not inferred from width/height alone.
SIDEWAYS_VAL = {"R1C26C140E415", "RC0CFE64586A9", "RF96D447DC21E"}


def main():
    torch.set_num_threads(6)
    OUT.mkdir(parents=True, exist_ok=True)
    reader = easyocr.Reader(
        ["th", "en"], gpu=False, verbose=False,
        model_storage_directory=str(LAB / "models" / "easyocr"),
        download_enabled=False,
    )
    inputs = [("first_validation", p) for p in sorted(VAL.glob("*.jpg"))]
    inputs += [("later_holdout", p) for p in sorted(LATER.glob("*.jpg"))]
    assert len(inputs) == 16
    for group, source in inputs:
        target = OUT / f"{source.stem}.json"
        sideways = group == "later_holdout" or source.stem in SIDEWAYS_VAL
        expected_rotation = ("90_ccw" if group == "later_holdout" else "90_cw") if sideways else "none"
        if target.exists():
            previous = json.loads(target.read_text(encoding="utf-8"))
            if previous.get("correction_applied") == expected_rotation:
                print("existing", source.name, flush=True)
                continue
        frame = cv2.imread(str(source))
        if frame is None:
            raise RuntimeError(source)
        if sideways:
            direction = (cv2.ROTATE_90_COUNTERCLOCKWISE if group == "later_holdout"
                         else cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.rotate(frame, direction)
        started = time.perf_counter()
        lines = reader.readtext(frame, detail=1, paragraph=False, canvas_size=960)
        records = [
            {"text": text, "confidence": round(float(conf), 4)}
            for _, text, conf in lines
        ]
        counted = [r for r in records if r["confidence"] >= 0.2]
        thai = sum("\u0e00" <= c <= "\u0e7f" for r in counted for c in r["text"])
        latin = sum(c.isascii() and c.isalpha() for r in counted for c in r["text"])
        row = {
            "group": group,
            "photo": source.name,
            "visual_rotation_from_upright_deg": 90 if sideways else 0,
            "correction_applied": ("90_ccw" if group == "later_holdout" else "90_cw") if sideways else "none",
            "ocr_canvas_size": 960,
            "ocr_lines": len(lines),
            "ocr_counted_lines_conf_ge_0_2": len(counted),
            "ocr_thai_letters": thai,
            "ocr_latin_letters": latin,
            "ocr_thai_share_of_thai_latin_letters": round(thai / (thai + latin), 4) if thai + latin else None,
            "elapsed_seconds": round(time.perf_counter() - started, 1),
            "note": "OCR-derived script proxy after visual 90-degree correction; unreviewed OCR text, not ground truth.",
            "raw_ocr_lines_private": records,
        }
        target.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        print(source.name, group, "rotation", row["visual_rotation_from_upright_deg"],
              "thai_share", row["ocr_thai_share_of_thai_latin_letters"],
              "letters", thai + latin, "seconds", row["elapsed_seconds"], flush=True)

    rows = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(OUT.glob("*.json"))]
    assert len(rows) == 16
    summary = {}
    for group in ("first_validation", "later_holdout"):
        part = [r for r in rows if r["group"] == group]
        shares = [r["ocr_thai_share_of_thai_latin_letters"] for r in part
                  if r["ocr_thai_share_of_thai_latin_letters"] is not None]
        summary[group] = {
            "photos": len(part),
            "sideways_90_deg": sum(r["visual_rotation_from_upright_deg"] == 90 for r in part),
            "ocr_thai_share_median": round(statistics.median(shares), 3) if shares else None,
            "ocr_thai_share_range": [min(shares), max(shares)] if shares else None,
            "ocr_thai_letters_total": sum(r["ocr_thai_letters"] for r in part),
            "ocr_latin_letters_total": sum(r["ocr_latin_letters"] for r in part),
        }
    summary["interpretation"] = (
        "Orientation is a visual 0/90-degree audit, not fine skew measurement. "
        "Language numbers are EasyOCR-recognized character shares after rotating sideways photos; "
        "recognition errors and different stores/documents can bias them. This observational comparison "
        "cannot establish why the two mAP scores differ."
    )
    (LAB / "reports" / "orientation_language_16_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
