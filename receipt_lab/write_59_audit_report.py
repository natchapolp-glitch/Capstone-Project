"""Public methods/status report for all 59 unique purchase-photo candidates."""

import json
import statistics
from pathlib import Path


LAB = Path.home() / "SeminarLab"
WORKSPACE = Path(__file__).resolve().parents[1]
BASE = LAB / "reports" / "orientation_skew_59"
OUT = WORKSPACE / "ass5_output" / "Orientation_and_Language_All_59_2026-10-17.md"


def main():
    rows = json.loads((BASE / "results.json").read_text(encoding="utf-8"))
    summary = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
    assert len(rows) == 59
    body = [
        "# ตรวจทิศทางภาพและมุมเอียงในชุดใบซื้อสินค้า 59 ภาพ",
        "",
        "วันที่ 17 ตุลาคม 2569 ขอบเขตคือ `doc_type=itemized_purchase` ที่ SHA-256 ไม่ซ้ำ "
        "และมีไฟล์ภาพอยู่จริงใน `SeminarLab/incoming` ทั้ง 59 ภาพ จำนวนนี้เป็น **ภาพผู้สมัคร** "
        "ไม่ใช่ 59 ธุรกรรมอิสระ ชุดนี้มี 59 ภาพตาม manifest ปัจจุบัน; ไม่มีเกณฑ์ตัดหนึ่งภาพที่ทำให้เหลือ 58",
        "",
        "## ผลตรวจครบชุด",
        "",
        f"- ตรวจการวางตัวหนังสือด้วยภาพรวมส่วนตัวทั้ง 59 ภาพ: อ่านตรงเดิม {summary['orientation_readable_none']} ภาพ "
        f"ต้องหมุนตามเข็ม 90° {summary['orientation_readable_cw']} ภาพ และทวนเข็ม 90° {summary['orientation_readable_ccw']} ภาพ "
        "ได้ตรวจแผ่นภาพหลังหมุนซ้ำว่าอ่านตรง",
        f"- มีกรอบเอกสารสำหรับประเมินมุมย่อย {summary['skew_estimated_single_label']} ภาพ "
        f"อีก {summary['skew_not_estimated_complex_photo']} ภาพไม่มีกรอบเดี่ยวที่ใช้เทียบกันได้ "
        "เพราะเคยกันออกจากชุด YOLO เนื่องจากหลายเอกสารในภาพหรือความเสี่ยงเอกสารคู่",
        f"- ใบพิมพ์ที่มีกรอบ 40 ภาพได้มัธยฐานค่าสัมบูรณ์ของมุมจัดแนวอัตโนมัติ "
        f"{summary['printed_median_absolute_alignment_deg']:.2f}°; "
        "15 ภาพมีการเพิ่มคะแนนการจัดแนวต่ำกว่า 2% จึงเป็นสัญญาณมุมอ่อน "
        "ใบเขียนมือที่มีกรอบ 14 ภาพมีเส้นตาราง ซึ่งค่ามุมอัตโนมัติสะท้อนแนวเส้นฟอร์มเป็นหลัก",
        "",
        "## วิธีและขอบเขตการตีความ",
        "",
        "ครอปตามกรอบอ้างอิงของชุด YOLO แล้วหมุน 90° ตามผลตรวจภาพ "
        "จากนั้นแปลงภาพเป็นขาวดำแบบ adaptive threshold และค้นหามุม -12° ถึง +12° ทีละ 0.25° "
        "โดยเลือกมุมที่พิกเซลหมึกกระจุกตามแถวมากสุด ค่าในตารางคือ **องศาที่โปรแกรมแนะนำให้หมุนเพื่อจัดแนว** "
        "ไม่ใช่มุมขอบกระดาษหรือมุมบรรทัดที่คนทำเฉลย ภาพจาง ภาพยับ และเอกสารสองหน้าอาจให้ค่าเฉลี่ยที่ไม่แทนทุกบรรทัด",
        "",
        "| ลำดับ | รหัสภาพ | หมุนเพื่ออ่านตรง | มุมจัดแนวอัตโนมัติ | ข้อจำกัด |",
        "|---:|---|---|---:|---|",
    ]
    for r in rows:
        turn = {"none": "เดิม", "cw": "90° ตามเข็ม", "ccw": "90° ทวนเข็ม"}[r["rotation_to_read"]]
        if not r["single_document_label"]:
            angle, note = "—", "ไม่มีกรอบเดี่ยว; ไม่คำนวณมุมย่อย"
        else:
            angle = f"{r['rotation_to_align_text_deg']:+.2f}°"
            if r["condition"] == "handwritten":
                note = "ฟอร์มเขียนมือ; มุมเส้นตาราง"
            elif r["score_improvement_vs_0_pct"] < 2:
                note = "ใบพิมพ์; สัญญาณมุมอ่อน"
            else:
                note = "ใบพิมพ์; ค่าประมาณ EDA"
        body.append(f"| {r['index']} | {r['doc_id']} | {turn} | {angle} | {note} |")
    body += [
        "",
        "## ภาษาไทยและ Latin",
        "",
        "การตรวจด้วยตาและ OCR ของชุดเปรียบเทียบ 16 ภาพทำแล้ว "
        "(ดู `Orientation_and_Language_Followup_2026-10-17.md`) "
        "สำหรับชุด 59 ภาพต้องแยก **การปรากฏของอักษรในภาพ** ออกจาก "
        "**สัดส่วนจำนวนอักษรจริง** ซึ่งต้องถอดข้อความชื่อสินค้าหรือทั้งเอกสารและตรวจซ้ำ "
        "ข้อความจางและลายมือในชุดนี้ทำให้ผล OCR เพียงอย่างเดียวใช้เป็นเฉลยไม่ได้",
    ]
    ocr_path = BASE / "ocr_summary.json"
    if ocr_path.exists():
        ocr = json.loads(ocr_path.read_text(encoding="utf-8"))
        body += [
            "",
            f"ทดลอง EasyOCR บนครอปที่หมุนให้ตรงครบ {ocr['n']} ภาพแล้ว "
            f"มีภาพที่ OCR รับรู้อักษรไทยหรือ Latin อย่างน้อยหนึ่งตัว {ocr['with_any_ocr_letters']} ภาพ "
            f"มัธยฐานจำนวนอักษรที่อ่านได้ {ocr['ocr_recognized_letters_median']} ตัวต่อภาพ "
            f"และ {ocr['ocr_recognized_letters_lt100']} ภาพอ่านได้ต่ำกว่า 100 ตัว "
            "จึงใช้ข้อมูลนี้เป็นเพียงการตรวจความครอบคลุมของ OCR ไม่ใช้คำนวณสัดส่วนภาษาแท้หรืออธิบายคะแนน YOLO",
        ]
    else:
        ocr_dir = LAB / "ocr_outputs" / "script_proxy_59"
        partial = []
        for path in ocr_dir.glob("*.json"):
            result = json.loads(path.read_text(encoding="utf-8"))
            if result.get("method") == "upright_crop_canvas960_conf0.2":
                partial.append(result)
        counts = [r["thai_letters_ocr"] + r["latin_letters_ocr"] for r in partial]
        body += [
            "",
            f"ทดลอง EasyOCR แล้ว {len(partial)}/59 ภาพก่อนหยุดการประมวลผล "
            f"OCR รับรู้อักษรไทยและ Latin รวมมัธยฐาน {statistics.median(counts):g} ตัวต่อภาพ "
            f"({sum(n < 100 for n in counts)}/{len(counts)} ภาพต่ำกว่า 100 ตัว; ช่วง {min(counts)}–{max(counts)} ตัว) "
            "แม้ภาพบางใบมีข้อความพิมพ์ยาว จึงยังใช้ผลนี้แทนข้อความจริงไม่ได้ "
            "การรัน OCR ต่อให้ครบ 59 ภาพโดยไม่มีข้อความถอดที่ตรวจด้วยคน ไม่ทำให้ได้สัดส่วนภาษาแท้ "
            "ขั้นถัดไปคือกำหนดขอบเขตข้อความที่จะนับ ถอดและตรวจซ้ำ แล้วจึงคำนวณสัดส่วนอักษร",
        ] if counts else ["", "ยังไม่มีผล OCR ครบชุดหรือข้อความถอดที่ตรวจซ้ำสำหรับคำนวณสัดส่วนภาษาแท้"]
    body += [
        "",
        "สคริปต์ทำซ้ำ: `receipt_lab/contact_itemized_59.py`, "
        "`receipt_lab/audit_orientation_skew_59.py`, `receipt_lab/ocr_script_proxy_59.py` "
        "และ `receipt_lab/write_59_audit_report.py` "
        "ข้อมูลรายภาพและแผ่นภาพตรวจเก็บเฉพาะ `C:\\Users\\NATCHAPOL\\SeminarLab` นอกโฟลเดอร์ส่งงาน",
        "",
    ]
    OUT.write_text("\n".join(body), encoding="utf-8")
    print("59-photo audit report written")


if __name__ == "__main__":
    main()
