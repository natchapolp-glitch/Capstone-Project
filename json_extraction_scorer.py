"""
JSON Extraction Scorer สำหรับ Pilot 2 (LLM Extraction Accuracy)
================================================================
เทียบ JSON ที่ LLM สกัดออกมา กับ ground truth JSON แล้วคำนวณ:
- JSON_Valid: output parse เป็น JSON ได้หรือไม่
- Field-level Precision / Recall / F1 (รวม top-level fields + items array)
- Exact_Match: ทุก field ตรงกับ ground truth 100% หรือไม่
- Hallucination_Count: จำนวน item ใน output ที่ไม่ตรงกับ item ใดใน ground truth เลย

Schema ที่รองรับ (ตัวอย่าง):
{
  "merchant": "...", "transaction_date": "YYYY-MM-DD", "currency": "THB",
  "items": [{"name": "...", "quantity": N, "unit": "...",
             "unit_price": N, "line_total": N}],
  "grand_total": N
}

การใช้งาน (ไฟล์เดี่ยว):
    python json_extraction_scorer.py --gt gt_json/r001.json --hyp out/r001_llama3_gbnf.json

การใช้งาน (batch จากโฟลเดอร์):
    python json_extraction_scorer.py --gt-dir gt_json/ --hyp-dir out/ --out results.csv
"""

import argparse
import csv
import json
import os
import sys
from difflib import SequenceMatcher
from decimal import Decimal
from pathlib import Path
import math
import unicodedata

SCHEMA = json.loads(Path(__file__).with_name("receipt_schema.json").read_text(encoding="utf-8"))
TOP_LEVEL_FIELDS = [key for key in SCHEMA["required"] if key != "items"]
ITEM_SCHEMA = SCHEMA["properties"]["items"]["items"]
ITEM_FIELDS = ITEM_SCHEMA["required"]
NAME_MATCH_THRESHOLD = 0.6  # ความคล้ายขั้นต่ำของชื่อสินค้าที่ถือว่า "match กัน" (fuzzy)

def schema_errors(value, spec=SCHEMA, path="$"):
    """Validate the deliberately small, dependency-free receipt schema."""
    types = spec.get("type", [])
    types = [types] if isinstance(types, str) else types
    actual = ("null" if value is None else "boolean" if isinstance(value, bool)
              else "object" if isinstance(value, dict) else "array" if isinstance(value, list)
              else "string" if isinstance(value, str) else "number"
              if isinstance(value, int) or isinstance(value, float) and math.isfinite(value) else "invalid")
    if actual not in types:
        return [f"{path}: expected {types}, got {actual}"]
    errors = []
    if actual == "object":
        errors += [f"{path}.{key}: required" for key in spec.get("required", []) if key not in value]
        for key, item in value.items():
            if key not in spec.get("properties", {}):
                errors.append(f"{path}.{key}: unknown field")
            else:
                errors += schema_errors(item, spec["properties"][key], f"{path}.{key}")
    elif actual == "array":
        for index, item in enumerate(value):
            errors += schema_errors(item, spec["items"], f"{path}[{index}]")
    return errors

def normalize(value):
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value).strip()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return Decimal(str(value))
    return value

def is_present(value):
    return value is not None and (not isinstance(value,str) or bool(value.strip()))

def strict_json_loads(text):
    def object_pairs(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate JSON key: '+key)
            result[key]=value
        return result
    def invalid_constant(value):raise ValueError('Non-JSON constant: '+value)
    return json.loads(text,object_pairs_hook=object_pairs,parse_constant=invalid_constant)

def failed_result(json_valid, errors):
    return {"json_valid": json_valid, "schema_valid": 0,
            "schema_errors": "; ".join(errors), "precision": 0.0,
            "recall": 0.0, "f1": 0.0, "exact_match": 0,
            "hallucination_count": None}

def name_similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).strip().lower(), str(b).strip().lower()).ratio()


def match_items(gt_items, hyp_items):
    """จับคู่ item ระหว่าง GT กับ output ด้วย fuzzy name matching (greedy, ไม่ซ้ำคู่)"""
    matched_pairs = []
    used_hyp = set()
    used_gt = set()
    # Match complete equal rows first so duplicate product names and reordering
    # do not steal the correct pair from one another.
    for gi, item in enumerate(gt_items):
        for hj, candidate in enumerate(hyp_items):
            if hj not in used_hyp and all(normalize(item[k]) == normalize(candidate[k]) for k in ITEM_FIELDS):
                matched_pairs.append((gi, hj))
                used_gt.add(gi)
                used_hyp.add(hj)
                break
    for gi, gt_item in enumerate(gt_items):
        if gi in used_gt:
            continue
        best_j, best_score = None, 0.0
        for hj, hyp_item in enumerate(hyp_items):
            if hj in used_hyp:
                continue
            score = name_similarity(gt_item.get("name"), hyp_item.get("name"))
            if score > best_score:
                best_score, best_j = score, hj
        if best_j is not None and best_score >= NAME_MATCH_THRESHOLD:
            matched_pairs.append((gi, best_j))
            used_hyp.add(best_j)
    unmatched_gt = [i for i in range(len(gt_items)) if i not in [p[0] for p in matched_pairs]]
    unmatched_hyp = [j for j in range(len(hyp_items)) if j not in used_hyp]
    return matched_pairs, unmatched_gt, unmatched_hyp


def score(gt, hyp):
    """คืนค่า dict ผลลัพธ์การให้คะแนน 1 คู่ (gt dict, hyp dict)"""
    errors = schema_errors(gt)
    if errors:
        raise ValueError("Ground truth does not match receipt_schema.json: " + "; ".join(errors))
    errors = schema_errors(hyp)
    if errors:
        return failed_result(1, errors)
    tp, fp, fn = 0, 0, 0
    field_matches = []

    # --- Top-level fields ---
    for field in TOP_LEVEL_FIELDS:
        gt_val = gt.get(field)
        hyp_val = hyp.get(field)
        gt_present = is_present(gt_val)
        hyp_present = is_present(hyp_val)
        is_match = gt_present and hyp_present and normalize(gt_val) == normalize(hyp_val)
        field_matches.append(is_match if gt_present else None)
        if gt_present and hyp_present and is_match:
            tp += 1
        elif gt_present and (not hyp_present or not is_match):
            fn += 1
        if hyp_present and not (gt_present and is_match):
            fp += 1

    # --- Items array ---
    gt_items = gt.get("items", []) or []
    hyp_items = hyp.get("items", []) or []
    matched_pairs, unmatched_gt, unmatched_hyp = match_items(gt_items, hyp_items)

    for gi, hj in matched_pairs:
        for field in ITEM_FIELDS:
            gt_val = gt_items[gi].get(field)
            hyp_val = hyp_items[hj].get(field)
            gt_present = is_present(gt_val)
            hyp_present = is_present(hyp_val)
            is_match = gt_present and hyp_present and normalize(gt_val) == normalize(hyp_val)
            if gt_present and is_match:
                tp += 1
            elif gt_present:
                fn += 1
            if hyp_present and not is_match:
                fp += 1

    # item ที่หาย (unmatched_gt) = FN สำหรับทุก field ของ item นั้น
    fn += sum(max(1, sum(is_present(gt_items[i][k]) for k in ITEM_FIELDS)) for i in unmatched_gt)
    fp += sum(max(1, sum(is_present(hyp_items[i][k]) for k in ITEM_FIELDS)) for i in unmatched_hyp)
    hallucination_count = len(unmatched_hyp)

    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    f1 = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) else None

    exact_match = (not unmatched_gt and not unmatched_hyp
                   and all(normalize(gt[k]) == normalize(hyp[k]) for k in TOP_LEVEL_FIELDS)
                   and all(normalize(gt_items[i][k]) == normalize(hyp_items[j][k])
                           for i, j in matched_pairs for k in ITEM_FIELDS))

    return {
        "json_valid": 1,
        "schema_valid": 1,
        "schema_errors": "",
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "f1": round(f1, 4) if f1 is not None else None,
        "exact_match": 1 if exact_match else 0,
        "hallucination_count": hallucination_count,
    }


def load_json_safe(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return strict_json_loads(f.read()), True
    except (ValueError, FileNotFoundError):
        return None, False


def process_pair(gt_path, hyp_path):
    gt, gt_ok = load_json_safe(gt_path)
    hyp, hyp_ok = load_json_safe(hyp_path)
    if not gt_ok:
        raise ValueError(f"อ่าน ground truth ไม่ได้: {gt_path}")
    if schema_errors(gt):
        raise ValueError("Ground truth does not match receipt_schema.json: " + "; ".join(schema_errors(gt)))
    if not hyp_ok:
        return failed_result(0, ["Missing or invalid JSON output"])
    return score(gt, hyp)


def main():
    parser = argparse.ArgumentParser(description="ให้คะแนน JSON extraction สำหรับ Pilot 2")
    parser.add_argument("--gt", help="ground truth JSON ไฟล์เดี่ยว")
    parser.add_argument("--hyp", help="LLM output JSON ไฟล์เดี่ยว")
    parser.add_argument("--gt-dir", help="โฟลเดอร์ ground truth (batch mode)")
    parser.add_argument("--hyp-dir", help="โฟลเดอร์ output (batch mode, ชื่อไฟล์ต้องตรงกับ gt-dir)")
    parser.add_argument("--out", default="pilot2_scoring_results.csv", help="ไฟล์ CSV ผลลัพธ์ batch mode")
    args = parser.parse_args()

    if args.gt and args.hyp:
        result = process_pair(args.gt, args.hyp)
        for k, v in result.items():
            print(f"{k}: {v}")
        return

    if args.gt_dir and args.hyp_dir:
        rows = []
        gt_files = sorted(f for f in os.listdir(args.gt_dir) if f.endswith(".json"))
        for fname in gt_files:
            gt_path = os.path.join(args.gt_dir, fname)
            hyp_path = os.path.join(args.hyp_dir, fname)
            result = process_pair(gt_path, hyp_path)
            result["filename"] = fname
            rows.append(result)
            print(f"{fname}: {result}")

        fieldnames = ["filename", "json_valid", "schema_valid", "schema_errors", "precision", "recall", "f1",
                      "exact_match", "hallucination_count"]
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nบันทึกผลลัพธ์ทั้งหมด ({len(rows)} ไฟล์) ไปที่ {args.out}")
        print("นำค่าจากไฟล์นี้ไปวางในคอลัมน์ที่เกี่ยวข้องของ pilot2_llm_extraction_log.xlsx ตาม Doc_ID")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
