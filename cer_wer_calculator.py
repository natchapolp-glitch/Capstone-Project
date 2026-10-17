"""
CER/WER Calculator สำหรับ Pilot 1 (OCR Accuracy)
=================================================
คำนวณ Character Error Rate (CER) และ Word Error Rate (WER) ระหว่างไฟล์ ground truth
กับไฟล์ผลลัพธ์ OCR (PaddleOCR / EasyOCR)

การใช้งาน (แบบเดี่ยว):
    python cer_wer_calculator.py --gt gt/r001.txt --hyp ocr_paddle/r001.txt

การใช้งาน (แบบ batch จากโฟลเดอร์ ground truth + โฟลเดอร์ OCR output ที่ชื่อไฟล์ตรงกัน):
    python cer_wer_calculator.py --gt-dir gt/ --hyp-dir ocr_paddle/ --out results_paddle.csv

หมายเหตุสำคัญเรื่อง WER ภาษาไทย:
    ภาษาไทยไม่มีช่องว่างระหว่างคำ ฉะนั้น WER ที่คำนวณด้วยการ split() ตามช่องว่างธรรมดา
    จะนับ "วรรค" ไม่ใช่ "คำ" จริง ๆ (ใกล้เคียง phrase-level มากกว่า word-level)
    ถ้าต้องการ WER ระดับคำที่แม่นยำ ให้ติดตั้ง pythainlp แล้วสคริปต์นี้จะใช้ระบบตัดคำ
    ภาษาไทย (newmm) โดยอัตโนมัติ:
        pip install pythainlp
    ถ้าไม่มี pythainlp สคริปต์จะ fallback ไปใช้ whitespace split และแจ้งเตือนใน output
"""

import argparse
import csv
import os
import sys

try:
    from pythainlp.tokenize import word_tokenize as _thai_tokenize
    HAS_PYTHAINLP = True
except ImportError:
    HAS_PYTHAINLP = False


def levenshtein(a, b):
    """คำนวณ Levenshtein edit distance ระหว่าง sequence สองอัน (list หรือ str)"""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,       # deletion
                curr[j - 1] + 1,   # insertion
                prev[j - 1] + cost # substitution
            )
        prev = curr
    return prev[m]


def tokenize_words(text):
    if HAS_PYTHAINLP:
        return _thai_tokenize(text, engine="newmm")
    return text.split()


def compute_cer(gt_text, hyp_text):
    gt_chars = list(gt_text)
    if len(gt_chars) == 0:
        return None
    dist = levenshtein(gt_chars, list(hyp_text))
    return dist / len(gt_chars)


def compute_wer(gt_text, hyp_text):
    gt_words = tokenize_words(gt_text)
    hyp_words = tokenize_words(hyp_text)
    if len(gt_words) == 0:
        return None
    dist = levenshtein(gt_words, hyp_words)
    return dist / len(gt_words)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def process_pair(gt_path, hyp_path):
    gt_text = read_text(gt_path)
    hyp_text = read_text(hyp_path)
    return {
        "cer": compute_cer(gt_text, hyp_text),
        "wer": compute_wer(gt_text, hyp_text),
    }


def main():
    parser = argparse.ArgumentParser(description="คำนวณ CER/WER สำหรับ Pilot 1")
    parser.add_argument("--gt", help="ไฟล์ ground truth เดี่ยว (.txt)")
    parser.add_argument("--hyp", help="ไฟล์ OCR output เดี่ยว (.txt)")
    parser.add_argument("--gt-dir", help="โฟลเดอร์ ground truth (batch mode)")
    parser.add_argument("--hyp-dir", help="โฟลเดอร์ OCR output (batch mode, ชื่อไฟล์ต้องตรงกับ gt-dir)")
    parser.add_argument("--out", help="ไฟล์ CSV สำหรับบันทึกผล batch mode", default="cer_wer_results.csv")
    args = parser.parse_args()

    if not HAS_PYTHAINLP:
        print("⚠️  ไม่พบ pythainlp — WER จะคำนวณแบบ whitespace-split (ใกล้เคียง phrase-level "
              "ไม่ใช่ word-level ที่แม่นยำสำหรับภาษาไทย) ติดตั้งด้วย `pip install pythainlp` "
              "เพื่อความแม่นยำที่สูงขึ้น\n", file=sys.stderr)

    if args.gt and args.hyp:
        result = process_pair(args.gt, args.hyp)
        print(f"CER: {result['cer']:.4f}")
        print(f"WER: {result['wer']:.4f}")
        return

    if args.gt_dir and args.hyp_dir:
        rows = []
        gt_files = sorted(f for f in os.listdir(args.gt_dir) if f.endswith(".txt"))
        for fname in gt_files:
            gt_path = os.path.join(args.gt_dir, fname)
            hyp_path = os.path.join(args.hyp_dir, fname)
            if not os.path.exists(hyp_path):
                print(f"⚠️  ข้าม {fname} — ไม่พบไฟล์ที่ตรงกันใน hyp-dir", file=sys.stderr)
                continue
            result = process_pair(gt_path, hyp_path)
            rows.append({"filename": fname, "cer": result["cer"], "wer": result["wer"]})
            print(f"{fname}: CER={result['cer']:.4f} WER={result['wer']:.4f}")

        with open(args.out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["filename", "cer", "wer"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nบันทึกผลลัพธ์ทั้งหมด ({len(rows)} ไฟล์) ไปที่ {args.out}")
        print("นำค่า cer/wer จากไฟล์นี้ไปวางในคอลัมน์ PaddleOCR_CER / PaddleOCR_WER "
              "(หรือ EasyOCR_...) ของ pilot1_ocr_data_log.xlsx ตาม Doc_ID ที่ตรงกัน")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
