"""Classify 10 new retail receipts and reserve them as an external-scene test."""

import csv
import json
from pathlib import Path


LAB = Path.home() / "SeminarLab"
MANIFEST = LAB / "reports/manifest.csv"
PRIMARY = {"132729", "132750", "132757", "132815", "132845", "132950"}
PAYMENT = {"132911", "132931"}


def main():
    with MANIFEST.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    new = [row for row in rows if row["filename"].startswith("IMG_20261017_")]
    assert len(new) == 10 and all(not row["duplicate_of"] for row in new)
    for row in new:
        code = row["filename"].split("_")[2].split(".")[0]
        row["doc_type"] = ("itemized_purchase" if code in PRIMARY else
                           "payment_receipt" if code in PAYMENT else "other")
        row["condition"] = "wrinkled_print" if row["filename"] not in {
            "IMG_20261017_132729.jpg", "IMG_20261017_132757.jpg",
            "IMG_20261017_132845.jpg", "IMG_20261017_132950.jpg"} else ""
        row["notes"] = ("Assistant full-image review: itemized retail purchase; external scene test only, no training."
                        if code in PRIMARY else
                        "Assistant full-image review: loyalty/bank/payment transaction without itemized goods; supplementary only.")
        if row["filename"] == "IMG_20261017_132911.jpg":
            row["store_or_source"] = "B2S"
        elif row["filename"] in {"IMG_20261017_132729.jpg",
                                 "IMG_20261017_132750.jpg",
                                 "IMG_20261017_132757.jpg",
                                 "IMG_20261017_132845.jpg",
                                 "IMG_20261017_132931.jpg",
                                 "IMG_20261017_132950.jpg"}:
            row["store_or_source"] = "7-Eleven"
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = {"new_photos": 10, "classified_itemized_purchase": 6,
              "payment_receipt": 2, "other": 2,
              "split": "six_purchases_external_scene_test_only",
              "note": "Full-image visual review corrected preliminary contact-sheet classification. Verify item content and possible transaction duplicates before final research reporting."}
    (LAB / "reports/new_10_review.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
