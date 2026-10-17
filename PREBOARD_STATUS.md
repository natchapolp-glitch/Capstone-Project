# สถานะงานก่อนมีบอร์ด

อัปเดต 18 ตุลาคม 2569 — implement และรันบนเครื่องจริงแล้ว อยู่บน branch `pc-preboard-implementation` ยังไม่ครบเกณฑ์ทั้ง 5 ข้อ

แผนหลัก: [PREBOARD_IMPLEMENTATION_PLAN.md](PREBOARD_IMPLEMENTATION_PLAN.md)

Checkpoint 18 ตุลาคม 2569 เวลา 02:38: รับรอบแรกใหม่ 3 ภาพ, รอบสอง 0, เฉลยที่ตกลงแล้ว 0; Tesseract draft 59/59 และ EasyOCR draft 19/59 (งานยังรันอยู่) จำนวนนี้เป็นการรับข้อมูลและ coverage ไม่ใช่ความถูกต้อง ผลตรวจล่าสุด: tests ระบบ 30 กรณี + scorer 10 กรณีผ่าน; dataset structural validator ผ่าน; JavaScript ทั้งสามหน้าผ่าน syntax check; ยังไม่มี browser visual QA

| ข้อ | งาน | สถานะ | สิ่งที่มีแล้ว | หลักฐานที่ยังต้องทำ |
|---|---|---|---|---|
| 1 | เฉลย/กรอบ/ธุรกรรมซ้ำ | WAITING_HUMAN | structural validator ผ่าน 59 ภาพ; กรอบเดิม 54, ภาพซับซ้อน 5 แยกเหตุผล; near-duplicate proposals 28 คู่; ฟอร์มตรวจสองรอบ/ตกลงเฉลย | เจ้าของงานตรวจเต็มใบสองรอบ, ตกลงเฉลย, group/split audit สำหรับชุดที่ใช้วัด |
| 2 | OCR เปรียบเทียบ | IN_PROGRESS | EasyOCR/Tesseract รันจริงภาพเดียวกัน 3 ภาพ; Tesseract ครบ 59; runner CER/field metrics พร้อมและเก็บ failure | เฉลยตรวจครบเพื่อรัน benchmark และให้คะแนนหลัก |
| 3 | Local LLM → JSON | IN_PROGRESS | Qwen3 0.6B/1.7B × Q8/Q4 × grammar เปิด/ปิด × 3 รอบ = 24 ครั้งจาก OCR จริงหนึ่งภาพ พร้อมเวลา/RSS | matrix หลัก 16 เงื่อนไขต่อเอกสารจาก reference/OCR บนชุดที่มีเฉลย |
| 4 | เดโมครบถึง HA | PASS_IMPLEMENTATION | ภาพจริง 3 ภาพจบถึง HA สอง sensor มี event trace; ปิด broker/เปิดใหม่, retry/restart, กันยืนยันซ้ำ, กัน schema ผิด | ยังต้อง review รวมทั้งโครงงาน; engineering confirmations ไม่ใช่การตรวจเฉลยหรือ user study |
| 5 | Benchmark และต่างฉาก | WAITING_DATA | เก็บ timing/RSS จริงของ LLM/OCR/pipeline; Linux Tesseract วัด memory ฝั่ง Linux | ภาพจริงต่างฉากใหม่ 6 ภาพ/3 ธุรกรรม, เฉลย และ final benchmark หลังตรึง config |

## เปิดใช้งาน

หน้าตรวจเฉลย: http://127.0.0.1:8090/review • เดโม: http://127.0.0.1:8090/demo • เทียบสองรอบ: http://127.0.0.1:8090/adjudicate

อ่าน [PREBOARD_QUICKSTART.md](PREBOARD_QUICKSTART.md) สำหรับขั้นตอนกรอกเฉลยและคำสั่งรัน เครื่องมือตรวจเกณฑ์ล่าสุดสร้าง [completion_gates.json](reports/preboard/completion_gates.json) ซึ่งยังระบุ `overall_complete=false` ตามจริง

หลักฐานที่ commit ได้อยู่ใน [reports/preboard](reports/preboard/) ส่วน raw OCR, raw LLM responses, SQLite, ภาพครอป และข้อมูลเข้าสู่ระบบอยู่ใน `SeminarLab/preboard` นอก OneDrive

## Dependency ที่ต้องขอระหว่าง implementation

- ผู้ใช้แจ้งชื่อ **นายณัชพล เพ็งพล** และยืนยัน **ทำคนเดียว** จึงแก้เกณฑ์เป็น `single_reviewer_double_entry` โดยกรอกสองรอบจากภาพแล้วเทียบความต่าง ไม่อ้างผู้ตรวจคนที่สอง การแจ้งชื่อไม่ใช่การตรวจข้อมูลเสร็จ
- ภาพจริงต่างฉากใหม่อย่างน้อย 6 ภาพ จากอย่างน้อย 3 ธุรกรรมไม่ซ้ำ ให้ส่งคำแนะนำเก็บภาพและวิธีตรวจซ้ำที่ชัดเจน

ระหว่างรอ ได้ทำ environment, validators, runners, review UI, MQTT/HA integration และรันโมเดลจริงต่อแล้ว ยังไม่ปิด gate คะแนนความถูกต้องด้วยข้อมูลสมมติหรือ AI draft

## ปัญหาที่พบและแก้

- หน้าที่เปิดค้างส่ง POST หลัง server restart แล้วได้ 403: เก็บ token นอก repo ให้คงเดิม, รองรับ browser same-origin ที่ตรวจ Host/Origin/Fetch Metadata, หน้าใหม่ refresh token และแสดงข้อความใกล้ปุ่ม มี regression tests ครอบคลุม
- ให้คนเดียวกรอกสองรอบและบันทึกซ้ำข้อมูลเดิมได้โดยไม่สร้าง entry ซ้ำ; หากแก้ข้อมูลแล้วบันทึกอีกครั้ง จะเก็บ revision ใหม่พร้อมประวัติเดิม และใช้ revision ล่าสุดของแต่ละรอบตอนตกลงเฉลย
- แยกหน้าตรวจเฉลยออกจากเดโมเพื่อให้บันทึกจากภาพได้ทันที ไม่ต้องประมวลผลโมเดลก่อน ผู้ใช้ให้ล้างการกรอกเดิมเพื่อเริ่มใหม่แล้ว: สำรอง revision เดิม 2 ไฟล์ไว้ใน `SeminarLab/preboard/review_reset_backups` ไม่นับไฟล์สำรองเป็นเฉลยปัจจุบัน แยก session ของร่างในเบราว์เซอร์และป้องกันหน้าเก่าบันทึกกลับหลังล้าง
- OCR benchmark รันต่อด้วย run ID เดิมได้โดยไม่ลบ failure; การทดลอง LLM/ฟิลด์อ้างไฟล์ผล OCR จาก benchmark โดยตรง พร้อม hash และตรวจเฉลย/split ที่ตรงกัน
- แยกเวลาโหลดกับ warm pipeline โดยเก็บโมเดลใน RAM ระหว่าง warm-up และรอบวัด ไม่เรียกเดโมที่โหลดโมเดลใหม่ทุกคำขอว่า warm inference
- หมุนภาพก่อนตรวจจับตามทิศที่ผู้ใช้เลือก แล้วแปลงกรอบกลับพิกัดต้นฉบับ ไม่ fallback ไปกรอบเฉลยเมื่อโมเดลตรวจไม่พบ
- พบ OCR ยาวเกิน context และตรวจไม่พบเอกสารใน run แรก เก็บ failure ไว้ ไม่ลบออกจากหลักฐาน
- Home Assistant HTTP configuration ต้อง promote หลังตรวจว่าเปิดใช้งานได้ มิฉะนั้นรุ่นนี้ย้อน config และ restart หลังห้านาที; เพิ่มการยืนยันผ่าน API แล้ว

ข้อจำกัด: Q4_K_M สร้างจาก publisher Q8_0 อีกทอด ไม่ใช่ quantize โดยตรงจาก FP16; ผล 24 ครั้งเป็น engineering จากหนึ่ง OCR transcript ไม่ใช่คะแนนสกัดข้อมูล ผล OCR engineering ชุดแรกไม่ได้ควบคุม background workload จึงไม่สรุปเปรียบเทียบความเร็วสอง engine จากตัวเลขนั้น

เดโม warm แบบโมเดลอยู่ใน RAM รันจริงเพิ่มสองภาพ (หนึ่ง warm-up และหนึ่งรอบถัดมา) หลักฐานอยู่ใน `reports/preboard/warm_pipeline_smoke.json` มี EasyOCR batch ทำงานพร้อมกัน จึงใช้ยืนยันเส้นทางการทำงาน ไม่ใช้เป็นตารางเปรียบเทียบความเร็วขั้นสุดท้าย

## งานต่อหลัง checkpoint แรก

Checkpoint ถัดมา 18 ตุลาคม 2569 เวลา 03:13: รับรอบแรก 14 ภาพ, รอบสอง 0, adjudicated 0; EasyOCR draft 31/59 และยังทำงานอยู่ ตรวจ tests ระบบ 36 กรณีและ scorer 13 กรณีผ่าน รวม 49 กรณี มี integration test ของตัวสรุปผลใน repo ชั่วคราวแยก ไม่ได้เผยแพร่คะแนนจาก fixture เป็นผลโครงงาน

- เพิ่มตัวสรุป scored runs เป็น JSON/CSV/Markdown พร้อมตัวหาร, จำนวนธุรกรรม, failure, median/range/p95, RAM แยก metric และ MAE คู่ coverage เงื่อนไขรับงานตรวจ hash ของตารางเทียบ raw output ปัจจุบันด้วย แต่ยังไม่มีคะแนนความถูกต้องจริงให้สร้างตาราง
- แก้ `OverflowError` ของจำนวนเต็มยาวใน validator, ใช้กติกา empty string เดียวกันทั้งแถวที่จับคู่/ไม่จับคู่ และปฏิเสธ key ซ้ำ/NaN/Infinity ใน raw JSON ทดสอบย้อน raw engineering เดิม 24 ครั้งได้ parse-valid 21 และ schema-valid 18 เหมือนเดิม ไม่ใช่การรันโมเดลใหม่
- ตัวเปรียบเทียบฟิลด์ครอบคลุม OCR สองตัว × crop สองแบบ × สามรอบ พร้อม warm-up และ resume โดยใช้ extractor เดียวกัน ยังต้องรัน inference จริงหลังมีเฉลยที่ตกลงแล้ว
- สถานะการกรอกเดิมที่ยังค้าง label `draft_ai` ถูกปรับจากหลักฐานคนกรอกที่มีอยู่เท่านั้น ไม่แก้ transcript และไม่เลื่อนเป็น adjudicated
- งานฝั่งโค้ดที่ต้องต่อ: fingerprint ของ OCR/YOLO assets ให้ครบ และวัดการส่ง MQTT/การสังเกต state ใน HA แยกจากเวลาคนตรวจ ส่วนการวิเคราะห์ข้อผิดพลาดและ review packet ขั้นสุดท้ายยังต้องรอผล scored runs
