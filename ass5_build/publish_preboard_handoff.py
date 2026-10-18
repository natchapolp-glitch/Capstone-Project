"""Publish concise handoff text only after the final artifacts pass their audit."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(name):return json.loads((ROOT/'reports/preboard'/name).read_text(encoding='utf-8'))
def write(name,text):(ROOT/name).write_text(text.strip()+'\n',encoding='utf-8')

def main():
    audit=read('deliverable_audit.json'); assert audit['status']=='pass'
    for name,value in audit['artifacts'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value,name
    ocr=read('single_pass_ocr.json'); llm=read('single_pass_llm.json'); pc=read('pc_transport_profile.json')
    run_audit=read('completed_run_audit.json'); assert run_audit['status']=='pass'
    assert llm['complete'] and pc['failures']==0
    ppt='ass5_output/Residential_Intelligence_Project_Progress_REVIEWED_2026-10-18'
    doc='ass6_output/Residential_Intelligence_Computer_Project_Proposal_REVIEWED_2026-10-18'
    script='ass5_output/Residential_Intelligence_Presentation_Script_REVIEWED_2026-10-18.md'
    pages=audit['pdf_pages'][Path(doc).name+'.pdf']
    easy=100*ocr['summaries']['all_eligible']['easyocr']['micro_cer']
    tess=100*ocr['summaries']['all_eligible']['tesseract']['micro_cer']
    seconds=pc['summaries']['automated_window_to_ha_observed_seconds']['median']
    files=f'''| งาน | ไฟล์แก้ไขได้ | ไฟล์อ่าน/พิมพ์ |
|---|---|---|
| Ass5 สไลด์ 21 หน้า | [PowerPoint]({ppt}.pptx) | [PDF]({ppt}.pdf) |
| Ass6 รายงาน {pages} หน้า | [Word]({doc}.docx) | [PDF]({doc}.pdf) |

บทพูด 21 สไลด์: [{Path(script).name}]({script})'''
    evidence=f'''- ภาพที่รวบรวม 59 ภาพ ข้อความหนึ่งรอบ **59/59 ภาพ** ผู้บันทึกนายณัชพล เพ็งพล ไม่ต้องกรอกซ้ำรอบสอง
- CER ใช้ข้อความผ่านเกณฑ์ **24 ภาพ / 28,011 ตัวอักษร** อีก **35 ภาพ** เก็บพร้อมเหตุผลคัดออก ไม่ได้ลบข้อมูล
- EasyOCR micro CER **{easy:.2f}%**; Tesseract **{tess:.2f}%** จากพิกเซลภาพเดียวกัน Tesseract ใช้ตัวอ่าน TSV ที่แก้แล้ว CER ต่ำกว่าหมายถึงผิดน้อย ไม่ใช่เปอร์เซ็นต์ความแม่นยำ
- Local LLM รันจริง **{llm['attempts']}/{llm['expected_attempts']} ครั้ง**: 6 ภาพ × ข้อความสองแหล่ง × โมเดลสองขนาด × quantization สองระดับ × grammar สองโหมด × 3 รอบ รันซ้ำไม่เพิ่มจำนวนภาพ
- คำตอบถูกตัดเมื่อครบเพดาน tokens {run_audit['llm_status_counts'].get('truncated',0)} ครั้ง และคำขอล้มเหลว {run_audit['llm_status_counts'].get('request_failed',0)} ครั้ง รวมไว้ในตัวหารทั้งหมด ดู [ผลตรวจสถานะคำตอบดิบ](reports/preboard/completed_run_audit.json)
- เดโม PC ถึง Home Assistant วัดจริง **3 ภาพ × 3 รอบ = {pc['attempts']} ครั้ง** ล้มเหลว {pc['failures']} ครั้ง มัธยฐานตั้งแต่ภาพถึงสังเกตค่า HA **{seconds:.3f} วินาที** ไม่รวมเวลาตรวจของมนุษย์
- หลักฐาน: [OCR](reports/preboard/single_pass_ocr.json), [LLM](reports/preboard/single_pass_llm.json), [เวลา/RAM แต่ละขั้น](reports/preboard/pc_transport_profile.json), [การทดสอบโค้ด](reports/preboard/verification.json), [ตรวจไฟล์ส่งมอบ](reports/preboard/deliverable_audit.json)'''
    deferred='''**ยังไม่ได้ทดลองตามขอบเขตที่ผู้จัดทำให้พักไว้:** (1) ความถูกต้องเชิงเนื้อหาของฟิลด์ JSON เพราะยังไม่มีเฉลยฟิลด์ที่ตรวจครบ (2) ภาพต่างฉากใหม่ที่แยกจากการพัฒนา

กรอบและกลุ่มธุรกรรมยังไม่รับรองครบทุกภาพ จึงไม่ถือว่า 59 ภาพเป็น 59 ธุรกรรมอิสระ คะแนน NPU และพลังงานต้องรอบอร์ด การพยากรณ์อัตราการใช้สินค้าต้องมีข้อมูลคงเหลือ/การใช้ตามเวลาเพิ่มเติม'''
    write('HANDOFF_ASS5_ASS6_FOR_TEAM_2026-10-18.md',f'''# Handoff ฉบับเพิ่มผลทดลองก่อนมีบอร์ด

หมายเลขโครงงาน **SCS3-4** กลุ่มสอบ **SCS3** อัปเดต 18 ตุลาคม 2569

## ไฟล์ที่ใช้ต่อ

ใช้ชุด **REVIEWED_2026-10-18** ด้านล่าง ชุด READY เดิมเก็บไว้เป็นประวัติและไม่ได้รวมผลรอบนี้ครบ

{files}

## สิ่งที่คงจากฐานเดิม

Ass5 ต่อจาก `ass 5ก่อนได้รับfeedback/assignment5 (1).pptx` ผ่านฉบับ READY วันที่ 18 ตุลาคม คงเหตุผล วรรณกรรม 57→37→35→12 กรอบ trade-off สามมิติ จุดร่วม/ความต่าง ช่องว่างวิจัย สถาปัตยกรรม และแผนงาน แล้วเพิ่มผล PC

Ass6 คงฐานจาก `Assignment4_รายงานทางวิชาการ _แก้ไข(2) (2).pdf` งานวิจัย 12 ฉบับ (11 ในกรอบสามมิติและหนึ่งงานสนับสนุนข้ามศาสตร์) หัวข้อหลัก 11 หัวข้อตามแบบคณะ และเพิ่มหัวข้อ 5.9–5.12 ไม่ได้เปลี่ยนโครงงานเป็น e-Eye ทั้งหมด: e-Senses เป็นกรอบระบบ ส่วน e-Eye เป็นส่วนที่ทดลองปัจจุบัน e-Nose/e-Skin เป็นแนวคิดต่อยอด

## ผลที่นำเสนอได้

{evidence}

## ข้อจำกัดที่ต้องพูดตรงกัน

{deferred}

ข้อความผู้บันทึกเป็นการตรวจหนึ่งรอบและมี OCR draft ให้ดู จึงเป็นผลเชิงพรรณนา ไม่ใช่เฉลยอิสระที่รับรองครบทุกตัวอักษร ตัดเฉพาะป้าย `[cite: N]` ก่อนคำนวณ CER และเก็บข้อความดิบไว้ Q4_K_M แปลงต่อจาก Q8_0 มิใช่จาก BF16 โดยตรง การผ่าน schema และส่ง MQTT สำเร็จไม่พิสูจน์ว่าสินค้าหรือยอดเงินถูกต้อง

ภาพส่งเพิ่มเดิม 6 ภาพที่ใช้ทดลอง YOLO เป็นหลักฐานย้อนหลัง ไม่ใช่ชุดภาพต่างฉากใหม่ที่พักไว้ คะแนนเดิม 0.928 (10 ภาพ) และ 0.237 (6 ภาพ) ไม่ใช่คะแนนจากทั้ง 59 ภาพ

## ลำดับนำเสนอ

1–4 แนะนำ ที่มา e-Senses และวัตถุประสงค์; 5–8 ฐานวิชาการและคำถามวิจัย; 9–10 สถาปัตยกรรมและหน้าตาระบบ; 11–13 ภาพ 59 ภาพและข้อความอ้างอิง; 14 ผล YOLO เดิม; 15 OCR; 16 เดโมกรอบ; 17 LLM/JSON; 18 เดโม MQTT/HA; 19 เวลาและ RAM; 20 งานต่อ; 21 สรุป ขอบคุณและ Q&A

ชื่อสินค้าและยอดเงินในสไลด์ 10 เป็นข้อมูลสมมติเพื่ออธิบายหน้าตาระบบ ส่วนสไลด์ 18 เป็นค่าที่ระบบรับจริงจากผลโมเดล แต่ยังไม่ได้วัดความถูกต้องของเนื้อหา ชุดวัดเวลาใช้การยืนยันอัตโนมัติเพื่อทดสอบทางเทคนิค ไม่ใช่ผู้ตรวจมนุษย์

## เปิดเดโมและหลักฐาน

บนเครื่องเจ้าของงาน: http://127.0.0.1:8090/demo และหน้าข้อความเดิม http://127.0.0.1:8090/review วิธีเปิดบริการอยู่ใน [PREBOARD_QUICKSTART.md](PREBOARD_QUICKSTART.md) ใช้ผลรันที่เตรียมไว้ประกอบการอธิบายได้ หากเดโมสดไม่พร้อมให้แสดงสไลด์และบอกว่าเป็นผลบันทึก

โมเดล เฉลยข้อความ รายละเอียดคำตอบดิบ และ SQLite อยู่ใน `C:/Users/NATCHAPOL/SeminarLab/preboard` บนเครื่องนี้ สรุปสาธารณะเก็บ SHA-256 ของหลักฐานเพื่อสอบกลับ เครื่องเพื่อนต้องเตรียม runtime และไฟล์นอก repo ตาม quickstart ก่อน localhost จึงจะใช้งานได้

## การตรวจทวน

ตรวจตัวเลขข้ามไฟล์ เปิด PPTX ด้วย PowerPoint ส่งออก PDF และตรวจทุกสไลด์ เปิด DOCX ผ่าน Word ส่งออก PDF และตรวจทุกหน้า ตารางสั้นอยู่ครบหน้า มีชื่อภาพ/ตารางและอ้างอิง ข้อความไหลต่อโดยคงหัวข้อกับเนื้อหา รายละเอียดอยู่ใน [รายการตรวจแนวปฏิบัติ](ASS5_ASS6_GUIDELINE_CHECK_2026-10-18.md)

งานส่งมอบส่วนที่ทำได้ด้วยข้อมูลปัจจุบันเสร็จตามขอบเขตที่ตกลง การทดลองที่พักไว้ยังไม่ได้ทดลอง ไม่อ้างว่าเป้าหมายวิจัยเดิมทั้งห้าข้อครบเชิงทดลอง และไม่มีหลักฐานว่าอาจารย์ที่ปรึกษาอนุมัติฉบับนี้แล้ว
''')
    write('ASS5_ASS6_GUIDELINE_CHECK_2026-10-18.md',f'''# ตรวจ Ass5 และ Ass6 ฉบับเพิ่มผลทดลอง

ใช้ชุด REVIEWED_2026-10-18 เทียบกับข้อความคำแนะนำที่ผู้จัดทำส่ง ภาพใน `ข้อมูลเพิ่มเติม` และ `แนวปฏิบัติในการจัดพิมพ์เค้าโครงโครงงาน.pdf`

## Ass5 จำนวน 21 สไลด์

| ข้อกำหนด | ผลตรวจ |
|---|---|
| ชื่อโครงงาน เลขโครงงาน กลุ่มสอบ ผู้จัดทำ ที่ปรึกษา | ปกมี SCS3-4 / SCS3 ชื่อและรหัสตรงรายงาน |
| เลขหน้า ที่มาไม่เกินหนึ่งสไลด์ | เลขหน้า 1–21; ที่มาสไลด์ 2 เป็นประเด็น |
| วัตถุประสงค์ ขอบเขต หน้าตาระบบ | สไลด์ 3–4 และ 9–10; แยกข้อมูลสมมติจากผลจริง |
| คงฐานเก่า | วรรณกรรม การคัดกรอง trade-off และช่องว่างวิจัยใน 5–8 |
| ผลจริงและเดโม | 11–19; แยกตัวหารภาพและการรันซ้ำชัดเจน |
| กระบวนงานครบหน้า ไม่มีงบประมาณ | แผนภาพใน 3, 9, 10, 18 อยู่ครบหน้า; ไม่มีสไลด์งบประมาณ |
| สรุป ขอบคุณ Q&A และบทพูด | สไลด์ 21; บทพูดตรงครบ 21 สไลด์ |

## Ass6 จำนวน {pages} หน้า

| ข้อกำหนด | ผลตรวจ |
|---|---|
| กระดาษและระยะขอบ | A4; บน/ซ้าย 1.5 นิ้ว ขวา/ล่าง 1 นิ้วตาม PDF ของคณะ |
| แบบอักษรและหัวข้อ | TH Sarabun New; หัวเรื่อง 18, หัวข้อหลัก 16, เนื้อหา/หัวข้อย่อย 14 pt; หัวข้อชิดซ้ายตามระดับและไม่ค้างท้ายหน้า |
| เลขหน้า | มุมขวาบน เว้นหน้าแรก |
| ฐานเนื้อหา | หัวข้อหลัก 11 หัวข้อ งานวิจัยฐาน 12 ฉบับ และผลเพิ่มเติม 5.9–5.12 |
| วิธีวัดและข้อจำกัด | แยก CER, parse/schema, เวลา, RSS และผลที่ยังไม่ได้ทดลอง ไม่แทนคะแนนเนื้อหาด้วย schema |
| รูปและตาราง | ภาพสถาปัตยกรรมพร้อมคำอธิบายและชื่อใต้ภาพ ตาราง 8 ตารางมีชื่อเหนือและหัวคอลัมน์ ไม่ตัดตารางสั้นข้ามหน้า |
| อ้างอิง | 23 รายการ; บรรทัดต่อเยื้อง แหล่งข้อมูลสถิติและผลรันระบุในเนื้อหา |
| ภาษา ชื่อ และงบประมาณ | ภาษารายงาน ข้อย่อย (1)–(4), นายติดชื่อ รหัสตรงสไลด์ ไม่มีช่องราคาว่างหรือราคาที่เดา |

ไม่ใส่ชื่อกรรมการอีกสองคนตามที่ผู้จัดทำยืนยันว่าไม่จำเป็น ไม่มีหลักฐานอนุมัติฉบับสุดท้ายจากอาจารย์

## หลักฐานการตรวจไฟล์

[ผลตรวจข้ามไฟล์และ hash](reports/preboard/deliverable_audit.json) บันทึกไฟล์ PPTX/PDF บทพูด DOCX/PDF และหน้าที่ตรวจจริง PPTX ผ่านตัวตรวจแพ็กเกจ ฟอนต์ ขนาดสไลด์ และตารางแก้ไขได้ รวมทั้งเปิดด้วย PowerPoint ได้ DOCX ส่งออกด้วย Word และตรวจภาพหน้าที่ได้จาก PDF ตัว renderer ที่มากับ skill ใช้ไม่ได้เพราะไม่มี LibreOffice ใน runtime จึงใช้ Word เป็นตัวส่งออก

{deferred}
''')
    write('README.md',f'''# Capstone Project — SCS3-4

Residential intelligence capstone. Examination group **SCS3**.

## Current deliverables

Use **REVIEWED_2026-10-18**. Earlier READY files are retained as history.

{files}

Start with the [team handoff](HANDOFF_ASS5_ASS6_FOR_TEAM_2026-10-18.md), [guideline review](ASS5_ASS6_GUIDELINE_CHECK_2026-10-18.md), and [evidence audit](reports/preboard/deliverable_audit.json).

## Actual PC evidence

59 photographs have saved single-pass transcripts. Descriptive OCR CER uses 24 eligible photographs; 35 retain their exclusion status. Local LLM format/cost testing completed 288 attempts on six frozen photographs. Corrected PC-to-MQTT/Home Assistant timing completed nine trials on three photographs. These are not independent-transaction semantic accuracy results.

JSON field accuracy and fresh scene testing are **not yet experimented**, as agreed with the project owner. Board NPU/energy measurements require hardware. Skipped annotation fields are unreviewed, not empty ground truth. No second annotation round is required.

See [evidence summaries](reports/preboard/), [status](PREBOARD_STATUS.md), [scope](ASS5_ASS6_COMPLETION_GOAL.md), and [local demo quickstart](PREBOARD_QUICKSTART.md). The [raw images](raw_receipts/README.md) are retained. Models, transcript revisions, raw responses and SQLite evidence remain in the owner's external SeminarLab directory; public reports record their hashes. A friend's machine needs its own runtime/assets before localhost links work.

The original Ass4 and pre-feedback Ass5 remain the foundations. e-Senses is the system concept; e-Eye is the current experimental part. Builder directories contain reproducible update scripts, not additional final submissions. Work is on `pc-preboard-implementation`.
''')
    status=(ROOT/'PREBOARD_STATUS.md').read_text(encoding='utf-8')
    history=status.split('## ประวัติ checkpoint เก่า',1)[1] if '## ประวัติ checkpoint เก่า' in status else ''
    write('PREBOARD_STATUS.md',f'''# สถานะงานก่อนมีบอร์ด

## ส่วนที่ส่งมอบแล้วตามขอบเขตล่าสุด

{evidence}

Ass5 21 สไลด์พร้อมบทพูด และ Ass6 {pages} หน้า ผ่านการตรวจเนื้อหา ตัวเลข และภาพหน้าจริงแล้ว ใช้ชุด REVIEWED ตาม [handoff](HANDOFF_ASS5_ASS6_FOR_TEAM_2026-10-18.md)

{deferred}

## ประวัติ checkpoint เก่า{history}
''')
    goal=(ROOT/'ASS5_ASS6_COMPLETION_GOAL.md').read_text(encoding='utf-8')
    goal=goal.replace('## งานกำลังดำเนินการ','## ประวัติระหว่างดำเนินการ (แทนด้วยผลส่งมอบด้านล่าง)')
    goal+='\n## ผลส่งมอบตามขอบเขตที่ปรับล่าสุด\n\nส่วนที่ทำได้ด้วยข้อมูลปัจจุบันเสร็จและตรวจทวนแล้ว: LLM 288 ครั้ง, PC profile รุ่น v3 เก้าครั้ง, Ass5 21 สไลด์/บทพูด และ Ass6 พร้อมผลจริง ดู handoff และ deliverable_audit.json สองการทดลองที่ผู้จัดทำให้พักไว้ยังระบุว่ายังไม่ได้ทดลอง ไม่ประกาศว่าเป้าหมายวิจัยเดิมครบทั้งหมด\n'
    write('ASS5_ASS6_COMPLETION_GOAL.md',goal)
    print('Handoff, README, status and guideline review updated from final evidence')

if __name__=='__main__':main()
