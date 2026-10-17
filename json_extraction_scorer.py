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
  "store_name": "...", "date": "YYYY-MM-DD",
  "items": [{"name": "...", "quantity": N, "unit_price": N, "category": "..."}],
  "total": N
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

TOP_LEVEL_FIELDS = ["store_name", "date", "total"]
ITEM_FIELDS = ["name", "quantity", "unit_price", "category"]
NAME_MATCH_THRESHOLD = 0.6  # ความคล้ายขั้นต่ำของชื่อสินค้าที่ถือว่า "match กัน" (fuzzy)


def name_similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).strip().lower(), str(b).strip().lower()).ratio()


def match_items(gt_items, hyp_items):
    """จับคู่ item ระหว่าง GT กับ output ด้วย fuzzy name matching (greedy, ไม่ซ้ำคู่)"""
    matched_pairs = []
    used_hyp = set()
    for gi, gt_item in enumerate(gt_items):
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
    tp, fp, fn = 0, 0, 0
    field_matches = []

    # --- Top-level fields ---
    for field in TOP_LEVEL_FIELDS:
        gt_val = gt.get(field)
        hyp_val = hyp.get(field)
        gt_present = gt_val is not None and str(gt_val).strip() != ""
        hyp_present = hyp_val is not None and str(hyp_val).strip() != ""
        is_match = gt_present and hyp_present and str(gt_val).strip() == str(hyp_val).strip()
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
            gt_present = gt_val is not None and str(gt_val).strip() != ""
            hyp_present = hyp_val is not None and str(hyp_val).strip() != ""
            is_match = gt_present and hyp_present and str(gt_val).strip() == str(hyp_val).strip()
            if gt_present and is_match:
                tp += 1
            elif gt_present:
                fn += 1
            if hyp_present and not is_match:
                fp += 1

    # item ที่หาย (unmatched_gt) = FN สำหรับทุก field ของ item นั้น
    fn += len(unmatched_gt) * len(ITEM_FIELDS)
    # item ที่หลอน (unmatched_hyp) = hallucination, ไม่นับเป็น FP ของ field-matching
    # (เพราะเป็นปัญหาคนละมิติ — item ที่ไม่มีตัวตนใน GT เลย)
    hallucination_count = len(unmatched_hyp)

    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision is not None and recall is not None and (precision + recall) > 0
          else None)

    exact_match = (fp == 0 and fn == 0 and hallucination_count == 0)

    return {
        "json_valid": 1,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "f1": round(f1, 4) if f1 is not None else None,
        "exact_match": 1 if exact_match else 0,
        "hallucination_count": hallucination_count,
    }


def load_json_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), True
    except (json.JSONDecodeError, FileNotFoundError):
        return None, False


def process_pair(gt_path, hyp_path):
    gt, gt_ok = load_json_safe(gt_path)
    hyp, hyp_ok = load_json_safe(hyp_path)
    if not gt_ok:
        raise ValueError(f"อ่าน ground truth ไม่ได้: {gt_path}")
    if not hyp_ok:
        return {"json_valid": 0, "precision": None, "recall": None, "f1": None,
                "exact_match": 0, "hallucination_count": None}
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
            if not os.path.exists(hyp_path):
                print(f"⚠️  ข้าม {fname} — ไม่พบไฟล์ที่ตรงกันใน hyp-dir", file=sys.stderr)
                continue
            result = process_pair(gt_path, hyp_path)
            result["filename"] = fname
            rows.append(result)
            print(f"{fname}: {result}")

        fieldnames = ["filename", "json_valid", "precision", "recall", "f1",
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
