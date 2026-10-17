"""Prepare and audit private, manually checked script transcriptions.

Receipt text stays under ~/SeminarLab, outside the synced project folder.
OCR output is deliberately never imported as ground truth.
"""

import argparse
import csv
import json
import re
import statistics
import unicodedata
from pathlib import Path

from PIL import Image


LAB = Path.home() / "SeminarLab"
AUDIT = LAB / "reports" / "orientation_skew_59" / "results.json"
ROOT = LAB / "language_truth_59"
RECORDS = ROOT / "records"
VALID_STATUS = {"not_started", "partial_unreadable", "no_item_lines_visible", "transcribed_once", "double_checked"}


def script_counts(lines):
    thai = latin = 0
    for line in lines:
        for char in line:
            category = unicodedata.category(char)
            if "\u0e00" <= char <= "\u0e7f" and category[0] in "LM":
                thai += 1
            elif re.fullmatch(r"[A-Za-z]", char):
                latin += 1
    return thai, latin


def initialize():
    rows = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert len(rows) == 59
    RECORDS.mkdir(parents=True, exist_ok=True)
    created = 0
    for row in rows:
        path = RECORDS / f"{row['doc_id']}.json"
        if path.exists():
            continue
        record = {
            "doc_id": row["doc_id"],
            "source_image": str(LAB / "reports" / "orientation_skew_59" / f"{row['doc_id']}_upright_crop.jpg"),
            "scope": "visible item names and other visible receipt text, recorded separately",
            "item_names": [],
            "item_fragments": [],
            "partial_line_reviewed": False,
            "other_text_lines": [],
            "unreadable_notes": [],
            "item_names_status": "not_started",
            "other_text_status": "not_started",
            "second_reviewer": "",
        }
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created += 1
    print(f"records={len(list(RECORDS.glob('*.json')))} created={created} private_dir={ROOT}")


def summarize():
    rows = json.loads(AUDIT.read_text(encoding="utf-8"))
    results = {}
    for section, status_key in (("item_names", "item_names_status"), ("all_visible", "other_text_status")):
        ready = []
        first_pass = []
        readable_partial = []
        readable_line_count = 0
        complete_line_count = 0
        partial_line_reviewed_count = 0
        status_counts = {status: 0 for status in VALID_STATUS}
        for row in rows:
            path = RECORDS / f"{row['doc_id']}.json"
            if not path.exists():
                status_counts["not_started"] += 1
                continue
            record = json.loads(path.read_text(encoding="utf-8"))
            status = record[status_key]
            if section == "item_names" and any("..." in name or "…" in name for name in record["item_names"]):
                raise ValueError(f"Incomplete item name in countable lines of {path}; move it to item_fragments")
            if status not in VALID_STATUS:
                raise ValueError(f"Invalid status in {path}: {status}")
            if status == "double_checked" and not record["second_reviewer"].strip():
                raise ValueError(f"Missing second reviewer in {path}")
            status_counts[status] += 1
            if section == "item_names" and status == "partial_unreadable" and record.get("partial_line_reviewed", False):
                partial_line_reviewed_count += 1
            if section == "item_names" and status in {"transcribed_once", "double_checked"}:
                first_pass.append((row["doc_id"], *script_counts(record["item_names"])))
                complete_line_count += len(record["item_names"])
            if section == "item_names" and status == "partial_unreadable" and record["item_names"]:
                readable_partial.append((row["doc_id"], *script_counts(record["item_names"])))
                readable_line_count += len(record["item_names"])
            if status != "double_checked":
                continue
            if section == "item_names":
                lines = record["item_names"]
            else:
                if record["item_names_status"] != "double_checked":
                    continue
                lines = record["item_names"] + record["other_text_lines"]
            thai, latin = script_counts(lines)
            ready.append((row["doc_id"], thai, latin))
        thai_total = sum(r[1] for r in ready)
        latin_total = sum(r[2] for r in ready)
        first_thai = sum(r[1] for r in first_pass)
        first_latin = sum(r[2] for r in first_pass)
        first_shares = [t / (t + l) for _, t, l in first_pass if t + l]
        partial_thai = sum(r[1] for r in readable_partial)
        partial_latin = sum(r[2] for r in readable_partial)
        observed_thai = first_thai + partial_thai
        observed_latin = first_latin + partial_latin
        results[section] = {
            "status_counts": status_counts,
            "first_pass_complete_usable": len(first_pass) if section == "item_names" else None,
            "first_pass_complete_line_count": complete_line_count if section == "item_names" else None,
            "first_pass_thai_script_codepoints": first_thai if section == "item_names" else None,
            "first_pass_latin_letters": first_latin if section == "item_names" else None,
            "first_pass_pooled_thai_share": round(first_thai / (first_thai + first_latin), 4) if first_thai + first_latin else None,
            "first_pass_median_image_thai_share": round(statistics.median(first_shares), 4) if first_shares else None,
            "first_pass_per_image": [
                {"doc_id": doc_id, "thai": t, "latin": l,
                 "thai_share": round(t / (t + l), 4) if t + l else None}
                for doc_id, t, l in first_pass
            ] if section == "item_names" else None,
            "partial_images_with_readable_lines": len(readable_partial) if section == "item_names" else None,
            "partial_images_line_reviewed": partial_line_reviewed_count if section == "item_names" else None,
            "partial_readable_line_count": readable_line_count if section == "item_names" else None,
            "partial_readable_thai_script_codepoints": partial_thai if section == "item_names" else None,
            "partial_readable_latin_letters": partial_latin if section == "item_names" else None,
            "partial_readable_pooled_thai_share": round(partial_thai / (partial_thai + partial_latin), 4) if section == "item_names" and partial_thai + partial_latin else None,
            "observed_readable_image_count": len(first_pass) + len(readable_partial) if section == "item_names" else None,
            "observed_readable_line_count": complete_line_count + readable_line_count if section == "item_names" else None,
            "observed_thai_script_codepoints": observed_thai if section == "item_names" else None,
            "observed_latin_letters": observed_latin if section == "item_names" else None,
            "observed_pooled_thai_share_not_59_estimate": round(observed_thai / (observed_thai + observed_latin), 4) if section == "item_names" and observed_thai + observed_latin else None,
            "double_checked_usable": len(ready),
            "thai_script_codepoints": thai_total,
            "latin_letters": latin_total,
            "thai_share": round(thai_total / (thai_total + latin_total), 4) if thai_total + latin_total else None,
            "complete_59": len(ready) == 59,
        }
    print(json.dumps(results, ensure_ascii=False, indent=2))


def write_queue():
    rows = json.loads(AUDIT.read_text(encoding="utf-8"))
    ROOT.mkdir(parents=True, exist_ok=True)
    target = ROOT / "review_queue.csv"
    with target.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "index", "doc_id", "original_filename", "width", "height",
            "condition", "item_names_status", "partial_line_reviewed", "readable_item_lines", "unreadable_notes",
        ])
        writer.writeheader()
        for row in rows:
            record = json.loads((RECORDS / f"{row['doc_id']}.json").read_text(encoding="utf-8"))
            original = LAB / "incoming" / row["filename"]
            with Image.open(original) as photo:
                width, height = photo.size
            writer.writerow({
                "index": row["index"],
                "doc_id": row["doc_id"],
                "original_filename": row["filename"],
                "width": width,
                "height": height,
                "condition": row["condition"],
                "item_names_status": record["item_names_status"],
                "partial_line_reviewed": record.get("partial_line_reviewed", False),
                "readable_item_lines": len(record["item_names"]),
                "unreadable_notes": " | ".join(record["unreadable_notes"]),
            })
    print(f"queue={target} rows={len(rows)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "summarize", "queue"])
    args = parser.parse_args()
    if args.action == "init":
        initialize()
    elif args.action == "summarize":
        summarize()
    else:
        write_queue()


if __name__ == "__main__":
    main()
