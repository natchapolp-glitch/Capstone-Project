"""Run local EasyOCR on unique intake images; keep text outside OneDrive."""

import argparse
import csv
import json
import time
from pathlib import Path


LAB = Path(r"C:\Users\NATCHAPOL\SeminarLab")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1, help="maximum unique images to process")
    parser.add_argument("--doc-id", action="append", help="process only this document ID; repeatable")
    parser.add_argument("--canvas-size", type=int, default=1600, help="EasyOCR detection canvas size")
    parser.add_argument("--force", action="store_true", help="overwrite existing OCR output")
    args = parser.parse_args()

    manifest = LAB / "reports" / "manifest.csv"
    if not manifest.is_file():
        parser.error("Run run_intake.ps1 first")
    with manifest.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    selected = [r for r in rows if not r["duplicate_of"]]
    if args.doc_id:
        wanted = set(args.doc_id)
        selected = [r for r in selected if r["doc_id"] in wanted]
        missing = wanted - {r["doc_id"] for r in selected}
        if missing:
            parser.error(f"Unknown or duplicate IDs: {', '.join(sorted(missing))}")
    selected = selected[: args.limit]
    if not selected:
        print("No images selected")
        return

    import easyocr

    out_dir = LAB / "ocr_outputs" / "easyocr_th_en"
    model_dir = LAB / "models" / "easyocr"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    reader = easyocr.Reader(
        ["th", "en"], gpu=False, verbose=False,
        model_storage_directory=str(model_dir), download_enabled=True,
    )
    for row in selected:
        target = out_dir / f"{row['doc_id']}.json"
        if target.exists() and not args.force:
            print(f"{row['doc_id']}: existing output preserved")
            continue
        source = LAB / "incoming" / row["filename"]
        start = time.perf_counter()
        results = reader.readtext(str(source), detail=1, paragraph=False,
                                  canvas_size=args.canvas_size)
        elapsed = time.perf_counter() - start
        record = {
            "doc_id": row["doc_id"], "engine": "EasyOCR", "languages": ["th", "en"],
            "version": easyocr.__version__, "elapsed_seconds": round(elapsed, 3),
            "canvas_size": args.canvas_size,
            "lines": [
                {"box": [[float(value) for value in point] for point in box],
                 "text": text, "confidence": float(confidence)}
                for box, text, confidence in results
            ],
            "note": "Raw OCR is unreviewed and may contain personal information. PC CPU result only.",
        }
        target.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{row['doc_id']}: {len(results)} text regions, {elapsed:.1f}s")


if __name__ == "__main__":
    main()
