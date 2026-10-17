"""Exact field accuracy conditional on a fixed OCR-to-JSON extractor."""
from json_extraction_scorer import ITEM_FIELDS, TOP_LEVEL_FIELDS, match_items, normalize, schema_errors, score


def field_metrics(truth, prediction):
    if schema_errors(truth):
        raise ValueError("Invalid ground truth")
    valid = not schema_errors(prediction)
    if not valid:
        prediction = {k: None for k in TOP_LEVEL_FIELDS}
        prediction["items"] = []
    counts = {k: {"correct": 0, "defined_reference": 0} for k in TOP_LEVEL_FIELDS}
    counts.update({"items."+k: {"correct": 0, "defined_reference": 0} for k in ITEM_FIELDS})
    for key in TOP_LEVEL_FIELDS:
        if truth[key] is not None:
            counts[key]["defined_reference"] += 1
            counts[key]["correct"] += int(valid and normalize(truth[key])==normalize(prediction[key]))
    pairs, missing, extra = match_items(truth["items"], prediction["items"])
    matching = dict(pairs)
    for i, row in enumerate(truth["items"]):
        for key in ITEM_FIELDS:
            if row[key] is not None:
                counts["items."+key]["defined_reference"] += 1
                counts["items."+key]["correct"] += int(i in matching and normalize(row[key])==normalize(prediction["items"][matching[i]][key]))
    amount_errors = []
    for key in ["grand_total"]:
        if truth[key] is not None and prediction[key] is not None:
            amount_errors.append({"field": key, "absolute_error": abs(float(truth[key])-float(prediction[key]))})
    for i, j in pairs:
        for key in ["unit_price", "line_total"]:
            a,b = truth["items"][i][key],prediction["items"][j][key]
            if a is not None and b is not None:
                amount_errors.append({"field": "items."+key, "absolute_error": abs(float(a)-float(b))})
    return {"counts": counts, "missing_items": len(missing), "extra_unmatched_items": len(extra),
            "numeric_absolute_errors_on_present_matched_fields": amount_errors,
            "numeric_error_coverage_limitation": "Missing or invalid numeric predictions are counted in field failures, not assigned zero monetary error"}
