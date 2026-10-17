"""Record a visually reviewed, itemized-purchase pilot without copying source images."""

import csv
import json
from collections import Counter
from pathlib import Path


LAB = Path.home() / "SeminarLab"
SELECTED = {
    "S__18440201_0.jpg": ("Advice", "single_page", "long electronics receipt"),
    "S__18440205_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440206_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440208_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440209_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440210_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440212_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440213_0.jpg": ("Makro", "single_page", ""),
    "S__18440214_0.jpg": ("Makro", "single_page", ""),
    "S__18440215_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440216_0.jpg": ("Makro", "single_page", ""),
    "S__18440217_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440219_0.jpg": ("Makro", "single_page", "one product; OCR smoke test completed"),
    "S__18440220_0.jpg": ("Makro", "two_pages_one_photo", "one purchase across two pages"),
    "S__18440221_0.jpg": ("Makro", "single_page", ""),
    "S__18440253_0.jpg": ("Makro", "single_page", ""),
    "S__18440257_0.jpg": ("Thai Watsadu", "single_page", ""),
    "S__18440258_0.jpg": ("Thai Watsadu", "single_page", "faded print; hard case"),
    "S__18440263_0.jpg": ("Thai Watsadu", "single_page", ""),
    "S__18440264_0.jpg": ("Thai Watsadu", "single_page", ""),
}


def main() -> None:
    manifest = LAB / "reports" / "manifest.csv"
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    assert fields is not None
    by_name = {row["filename"]: row for row in rows}
    missing = set(SELECTED) - set(by_name)
    if missing:
        raise RuntimeError(f"Missing selected images: {sorted(missing)}")
    out = LAB / "reports" / "pilot_itemized_20.csv"
    previous_pilot = {}
    if out.exists():
        with out.open(encoding="utf-8-sig", newline="") as stream:
            previous_pilot = {row["doc_id"]: row for row in csv.DictReader(stream)}
    selected_rows = []
    hashes = set()
    for filename, (store, page_form, note) in SELECTED.items():
        row = by_name[filename]
        if row["duplicate_of"] or row["sha256"] in hashes:
            raise RuntimeError(f"Duplicate selected image: {filename}")
        hashes.add(row["sha256"])
        if row["doc_type"] not in ("", "itemized_purchase"):
            raise RuntimeError(f"Conflicting document type: {filename}")
        row["doc_type"] = "itemized_purchase"
        if row["store_or_source"] not in ("", store):
            raise RuntimeError(f"Conflicting store label: {filename}")
        row["store_or_source"] = store
        if page_form == "two_pages_one_photo":
            marker = "one purchase across two pages in one photo"
            if marker not in row["notes"]:
                row["notes"] = "; ".join(filter(None, (row["notes"], marker)))
        if "faded" in note and not row["condition"]:
            row["condition"] = "faded_print"
        prior = previous_pilot.get(row["doc_id"], {})
        selected_rows.append({
            "doc_id": row["doc_id"],
            "filename": filename,
            "store_or_source": store,
            "page_form": page_form,
            "review_status": prior.get("review_status", "visually_reviewed_type_only"),
            "ground_truth_status": prior.get("ground_truth_status", "not_annotated"),
            "split": prior.get("split", "unassigned"),
            "notes": note,
        })
    if len(selected_rows) != 20:
        raise RuntimeError("Pilot must contain exactly 20 photos")
    with manifest.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with out.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(selected_rows[0]))
        writer.writeheader()
        writer.writerows(selected_rows)
    summary_path = LAB / "reports" / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["document_types"] = dict(Counter(row["doc_type"] or "Unclassified" for row in rows))
        summary["pilot_itemized_photos"] = len(selected_rows)
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "pilot_photos": len(selected_rows),
        "stores": dict(Counter(row["store_or_source"] for row in selected_rows)),
        "two_pages_one_photo": sum(row["page_form"] == "two_pages_one_photo" for row in selected_rows),
        "pilot_csv": str(out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
