"""Record visual document-type review for all 69 previously unclassified photos."""

import csv
import json
from collections import Counter
from pathlib import Path


LAB = Path.home() / "SeminarLab"
PRINTED_PURCHASE = {198, 199, 200, 222, 224, 227, 252, 254, 255, 256,
                    259, 260, 261, 265, 266}
HANDWRITTEN_PURCHASE = {223, 226, 235, 236, 237, 238, 239, 243, 245,
                        246, 247, 249, 250, 281, 289, 290, 292, 293}
PAYMENT_ONLY = {197, 202, 203, 204, 211, 228, 230, 231, 232, 233, 234,
                267, 268, 269, 270, 271, 274, 277, 278, 279, 280,
                283, 286, 287, 288, 291}
DELIVERY_NOTE = {241, 244}
OTHER = {225, 242, 272, 276, 282, 285}
INCOMPLETE = {248}
NEEDS_REVIEW = {275}
MULTIPLE_PURCHASES = {200, 245, 246}
NEAR_DUPLICATE_CANDIDATE = {289, 293}


def code(row):
    return int(row["filename"].split("__")[1].split("_")[0][-3:])


def main():
    groups = [PRINTED_PURCHASE, HANDWRITTEN_PURCHASE, PAYMENT_ONLY,
              DELIVERY_NOTE, OTHER, INCOMPLETE, NEEDS_REVIEW]
    flat = [item for group in groups for item in group]
    if len(flat) != len(set(flat)):
        raise RuntimeError("Overlapping classification sets")
    manifest = LAB / "reports" / "manifest.csv"
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    assert fields is not None
    targets = [row for row in rows if not row["duplicate_of"] and not row["doc_type"]]
    actual = {code(row) for row in targets}
    if actual != set(flat):
        raise RuntimeError(f"Classification list mismatch; missing={sorted(actual-set(flat))}, extra={sorted(set(flat)-actual)}")
    reviewed = []
    for row in targets:
        number = code(row)
        if number in PRINTED_PURCHASE or number in HANDWRITTEN_PURCHASE:
            doc_type = "itemized_purchase"
        elif number in PAYMENT_ONLY:
            doc_type = "payment_receipt"
        elif number in DELIVERY_NOTE:
            doc_type = "delivery_note"
        elif number in INCOMPLETE:
            doc_type = "itemized_purchase_incomplete"
        elif number in NEEDS_REVIEW:
            doc_type = "needs_detail_review"
        else:
            doc_type = "other"
        row["doc_type"] = doc_type
        print_type = "printed" if number in PRINTED_PURCHASE else (
            "handwritten" if number in HANDWRITTEN_PURCHASE else "not_applicable")
        if print_type == "handwritten" and not row["condition"]:
            row["condition"] = "handwritten"
        if number in {198, 199, 200, 261, 265}:
            row["store_or_source"] = "Thai Watsadu"
        elif number in {224, 252, 254, 255, 256, 259, 260}:
            row["store_or_source"] = "Makro"
        elif number in {222, 227, 266}:
            row["store_or_source"] = "Global House"
        flags = []
        if number in MULTIPLE_PURCHASES:
            flags.append("multiple_documents_or_transactions_in_one_photo")
        if number in NEAR_DUPLICATE_CANDIDATE:
            flags.append("possible_same_preprinted_receipt_number_needs_transaction_check")
        if number in INCOMPLETE:
            flags.append("visible_page_1_of_2_without_confirmed_pair")
        if number in NEEDS_REVIEW:
            flags.append("item_qty_price_not_yet_confirmed")
        if flags:
            row["notes"] = "; ".join(filter(None, (row["notes"], *flags)))
        reviewed.append({"doc_id": row["doc_id"], "filename": row["filename"],
                         "doc_type": doc_type, "print_type": print_type,
                         "flags": "; ".join(flags),
                         "review_status": "visual_contact_sheet_only"})
    with manifest.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    out = LAB / "reports" / "classification_review_69.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(reviewed[0]))
        writer.writeheader()
        writer.writerows(reviewed)
    unique = [row for row in rows if not row["duplicate_of"]]
    summary = {"unique_photos": len(unique),
               "unique_document_type_counts": dict(Counter(row["doc_type"] for row in unique)),
               "new_printed_purchase_candidates": len(PRINTED_PURCHASE),
               "new_handwritten_purchase_candidates": len(HANDWRITTEN_PURCHASE),
               "multiple_purchase_document_photos": sorted(MULTIPLE_PURCHASES),
               "note": "Visual photo-level classification; some images have multiple transactions and some may be near-duplicate transactions."}
    (LAB / "reports" / "classification_summary_103.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
