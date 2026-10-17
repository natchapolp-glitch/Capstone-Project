"""Private current counts for Ass5, excluding exact duplicate image files."""

import csv
import json
from collections import Counter
from pathlib import Path


LAB = Path.home() / "SeminarLab"


def main():
    with (LAB / "reports/manifest.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    unique = [row for row in rows if not row["duplicate_of"]]
    counts = dict(Counter(row["doc_type"] or "unclassified" for row in unique))
    assert len(rows) == 124 and len(unique) == 113 and counts.get("itemized_purchase") == 59
    result = {
        "all_files": len(rows), "sha256_unique_photos": len(unique),
        "exact_duplicate_files": len(rows)-len(unique),
        "unique_photo_type_counts": counts,
        "purchase_candidate_note": "Photo candidates, not verified independent transactions.",
        "same_scene_detector_split": {"train": 38, "validation": 10},
        "external_scene_holdout": 6,
    }
    (LAB / "reports/classification_summary_113.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
