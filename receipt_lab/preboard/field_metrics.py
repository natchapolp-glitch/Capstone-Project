"""Exact field accuracy conditional on a fixed OCR-to-JSON extractor."""
import math
from decimal import Decimal, localcontext
from json_extraction_scorer import ITEM_FIELDS, TOP_LEVEL_FIELDS, match_items, normalize, schema_errors, is_present


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
        if is_present(truth[key]):
            counts[key]["defined_reference"] += 1
            counts[key]["correct"] += int(valid and normalize(truth[key])==normalize(prediction[key]))
    pairs, missing, extra = match_items(truth["items"], prediction["items"])
    matching = dict(pairs)
    for i, row in enumerate(truth["items"]):
        for key in ITEM_FIELDS:
            if is_present(row[key]):
                counts["items."+key]["defined_reference"] += 1
                counts["items."+key]["correct"] += int(i in matching and normalize(row[key])==normalize(prediction["items"][matching[i]][key]))
    amount_errors = []
    for key in ["grand_total"]:
        if truth[key] is not None and prediction[key] is not None:
            amount_errors.append(amount_error(key,truth[key],prediction[key]))
    for i, j in pairs:
        for key in ["unit_price", "line_total"]:
            a,b = truth["items"][i][key],prediction["items"][j][key]
            if a is not None and b is not None:
                amount_errors.append(amount_error('items.'+key,a,b))
    return {"counts": counts, "missing_items": len(missing), "extra_unmatched_items": len(extra),
            "numeric_absolute_errors_on_present_matched_fields": amount_errors,
            "numeric_error_coverage_limitation": "Missing or invalid numeric predictions are counted in field failures, not assigned zero monetary error"}


def amount_error(field,reference,prediction):
    a,b=Decimal(str(reference)),Decimal(str(prediction))
    with localcontext() as context:
        context.prec=max(28,max(a.adjusted(),b.adjusted())-min(a.as_tuple().exponent,b.as_tuple().exponent)+4)
        error=abs(a-b)
    approx=float(error)
    return {'field':field,'absolute_error':approx if math.isfinite(approx) else None,
            'absolute_error_decimal':str(error),'outside_float_range':not math.isfinite(approx)}
