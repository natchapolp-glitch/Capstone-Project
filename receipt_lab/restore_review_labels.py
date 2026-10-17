"""Restore visual review labels after duplicate-row intake overwrite; idempotent."""

import csv
from pathlib import Path


REPORTS = Path.home() / "SeminarLab/reports"
MANIFEST = REPORTS / "manifest.csv"


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    rows = read(MANIFEST)
    review = {row["doc_id"]: row for row in read(REPORTS / "classification_review_69.csv")}
    pilot = {row["doc_id"]: row for row in read(REPORTS / "pilot_itemized_20.csv")}
    restored = 0
    for row in rows:
        if row["duplicate_of"] or row["doc_type"]:
            continue
        doc_id = row["doc_id"]
        if doc_id in review:
            source = review[doc_id]
            row["doc_type"] = source["doc_type"]
            if source["print_type"] == "handwritten":
                row["condition"] = "handwritten"
            row["notes"] = row["notes"] or source["flags"]
            restored += 1
        elif doc_id in pilot:
            row["doc_type"] = "itemized_purchase"
            row["store_or_source"] = row["store_or_source"] or pilot[doc_id]["store_or_source"]
            restored += 1
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Restored {restored} unique-photo labels")


if __name__ == "__main__":
    main()
