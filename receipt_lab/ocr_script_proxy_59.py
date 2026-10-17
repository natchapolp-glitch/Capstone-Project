"""Private OCR-script coverage audit on all 59 itemized candidate crops.

Character shares describe EasyOCR output only. They are not the actual script
composition of the receipts, because faded print and handwriting are missed.
"""

import json
import statistics
from pathlib import Path

import cv2
import easyocr
import torch


LAB = Path.home() / "SeminarLab"
ROOT = LAB / "ocr_outputs" / "script_proxy_59"
AUDIT = LAB / "reports" / "orientation_skew_59" / "results.json"


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(6)
    rows = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert len(rows) == 59
    reader = easyocr.Reader(["th", "en"], gpu=False, verbose=False,
        model_storage_directory=str(LAB / "models" / "easyocr"), download_enabled=False)
    metrics = []
    for row in rows:
        target = ROOT / (row["doc_id"] + ".json")
        if target.exists():
            out = json.loads(target.read_text(encoding="utf-8"))
            if out.get("method") == "upright_crop_canvas960_conf0.2":
                metrics.append(out)
                print(row["index"], row["doc_id"], "cached", flush=True)
                continue
        photo = LAB / "reports" / "orientation_skew_59" / (row["doc_id"] + "_upright_crop.jpg")
        frame = cv2.imread(str(photo))
        assert frame is not None, photo
        result = reader.readtext(frame, detail=1, paragraph=False, canvas_size=960,
                                 batch_size=8)
        lines = [{"text": text, "confidence": round(float(conf), 4)}
                 for _, text, conf in result]
        accepted = [r for r in lines if r["confidence"] >= .2]
        thai = sum("\u0e00" <= c <= "\u0e7f" for r in accepted for c in r["text"])
        latin = sum(c.isascii() and c.isalpha() for r in accepted for c in r["text"])
        out = {"index": row["index"], "doc_id": row["doc_id"], "filename": row["filename"],
               "condition": row["condition"], "method": "upright_crop_canvas960_conf0.2",
               "detected_lines": len(lines), "accepted_lines": len(accepted),
               "thai_letters_ocr": thai, "latin_letters_ocr": latin,
               "thai_share_ocr": round(thai/(thai+latin), 4) if thai+latin else None,
               "raw_lines_private": lines}
        target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        metrics.append(out)
        print(row["index"], row["doc_id"], thai+latin, out["thai_share_ocr"], flush=True)
    assert len(metrics) == 59
    shares = [r["thai_share_ocr"] for r in metrics if r["thai_share_ocr"] is not None]
    summary = {"n": 59, "with_any_ocr_letters": len(shares),
               "ocr_recognized_letters_median": statistics.median(r["thai_letters_ocr"]+r["latin_letters_ocr"] for r in metrics),
               "ocr_recognized_letters_lt100": sum(r["thai_letters_ocr"]+r["latin_letters_ocr"] < 100 for r in metrics),
               "median_thai_share_in_ocr_output_only": statistics.median(shares) if shares else None,
               "warning": "OCR script proxy is not the Thai/Latin share of actual receipts and must not be used as ground truth."}
    (LAB / "reports" / "orientation_skew_59" / "ocr_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
