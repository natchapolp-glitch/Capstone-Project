"""Tag the 14 separately added dorm invoices in the local manifest."""

import csv
import os
import re
import tempfile
from pathlib import Path


manifest = Path(r"C:\Users\NATCHAPOL\SeminarLab\reports\manifest.csv")
with manifest.open(encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)
    fields = reader.fieldnames
    rows = list(reader)
if not fields or "filename" not in fields or "doc_type" not in fields:
    raise SystemExit("Unexpected manifest columns")

pattern = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\.jpg", re.I)
matches = [row for row in rows if pattern.fullmatch(row["filename"])]
if len(matches) != 14:
    raise SystemExit(f"Expected 14 newly added UUID filenames, found {len(matches)}; no changes")
changed = 0
for row in matches:
    if not row["doc_type"].strip():
        row["doc_type"] = "housing_invoice"
        changed += 1

with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", dir=manifest.parent,
                                 prefix="manifest_tagged_", suffix=".csv", delete=False) as tmp:
    writer = csv.DictWriter(tmp, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    temp_name = tmp.name
os.replace(temp_name, manifest)
print(f"Tagged {changed} housing invoices; {len(matches)} UUID files found")
