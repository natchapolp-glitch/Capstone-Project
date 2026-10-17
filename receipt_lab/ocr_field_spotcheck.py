"""Score six manually aligned numeric fields in three OCR smoke-test photos."""

import csv
import json
import re
from pathlib import Path


LAB = Path.home() / "SeminarLab"
CASES = [
    ("RC4859AC7A019", "date", "06-04-2025", "95=04=2025"),
    ("RC4859AC7A019", "total", "13990.00", "13990.00"),
    ("RDB5A64848417", "date", "03.10.2026", "03 10 2026 16 15"),
    ("RDB5A64848417", "total", "313.00", "313 00"),
    ("R167E1A213080", "date", "20.09.2026", "20 09 2026 1 : 1:1"),
    ("R167E1A213080", "total", "760.00", None),
]


def digits(value):
    return "".join(re.findall(r"\d", value))


def main():
    rows = []
    for doc_id, field, printed, selected_ocr in CASES:
        record = json.loads((LAB / "ocr_outputs" / "easyocr_th_en" /
                             f"{doc_id}.json").read_text(encoding="utf-8"))
        available = [line["text"] for line in record["lines"]]
        if selected_ocr is not None and selected_ocr not in available:
            raise RuntimeError(f"Selected OCR segment not found: {doc_id} {field}")
        gt_digits = digits(printed)
        ocr_digits = digits(selected_ocr or "")
        if field == "date":
            ocr_digits = ocr_digits[:8]  # OCR line may include the purchase time.
        correct = int(ocr_digits == gt_digits)
        rows.append({"doc_id": doc_id, "field": field, "printed_value": printed,
                     "ocr_selected_line": selected_ocr or "[no corresponding OCR line]",
                     "digits_exact": correct,
                     "review_status": "one_pass_manual_alignment_needs_second_check"})
    out = LAB / "reports" / "ocr_field_spotcheck_3.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {"photos": 3, "fields": 6,
               "digit_exact_after_manual_alignment": sum(row["digits_exact"] for row in rows),
               "date_exact": sum(row["digits_exact"] for row in rows if row["field"] == "date"),
               "total_exact": sum(row["digits_exact"] for row in rows if row["field"] == "total"),
               "note": "One-pass manual transcription/alignment; not end-to-end field extraction accuracy."}
    (LAB / "reports" / "ocr_field_spotcheck_3.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
