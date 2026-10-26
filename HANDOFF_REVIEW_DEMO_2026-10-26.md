# Handoff: ตรวจสไลด์ บทพูด และเดโม — 26 ตุลาคม 2569

> **มีงานตรวจต่อแล้ว:** ใช้ [HANDOFF_PRESENTATION_REVIEW_2026-10-26.md](HANDOFF_PRESENTATION_REVIEW_2026-10-26.md) สำหรับสถานะล่าสุด Robot รอบใหม่ผ่าน 7/7 แล้วหลังคืน runtime และแก้ HTTP ส่วนเนื้อหาด้านล่างเก็บสถานะก่อนตรวจต่อเพื่อรักษาประวัติ

## สถานะก่อนหยุด

ผู้ใช้ขอให้ตรวจสไลด์ บทพูด และขั้นตอนเดโม โดยทดลองด้วย Robot Framework และ Selenium ก่อน แล้วสั่งให้ทำ handoff ระหว่างดำเนินงาน

**ยังไม่จบงานตรวจรอบนี้ และห้ามรายงานว่าเดโมผ่านแล้ว** แก้สไลด์และร่างบทพูดใหม่แล้ว แต่ Robot รอบใหม่ยังไม่ผ่าน พบไฟล์ `llama-server.exe` หายหลังรัน ต้องตรวจสาเหตุต่อ ไม่ได้ยืนยันว่าโปรแกรมป้องกันไวรัสเป็นผู้ลบ

Repository: `C:\Users\NATCHAPOL\OneDrive\เดสก์ท็อป\Seminar`

Branch: `pc-preboard-implementation` ล่าสุดที่ commit/push ไว้ก่อนงานรอบนี้คือ `e1c619d` งาน 26 ต.ค. และ handoff นี้ **ยังไม่ได้ commit/push**

## เงื่อนไขผู้ใช้ที่ต้องรักษา

- พรีสองคน **10 นาทีรวมเดโม** อาจารย์อนุญาตเปิดคลิปได้
- ทั้งสองคนต้องตอบได้ทุกสไลด์ ไม่ใช่รู้เฉพาะหน้าที่ตัวเองพูด
- ธนบดี เริ่มรักสกุลพูดหน้า 1–13; ณัชพล เพ็งพลพูดหน้า 14–21 พร้อมเปิดคลิปหน้า 18
- แผนเวลา: พูด/เปิดคลิปรวม 9 นาที เผื่อ 1 นาที คลิปไม่เกิน 2 นาที เวลาเป็นแผน ยังไม่จับเวลาซ้อมมนุษย์จริง
- คงฐาน Ass4 และ Ass5 เดิม e-Senses เป็นกรอบรวม ส่วนที่ทดลองคือ e-Eye ห้ามอ้างว่าทำ e-Nose/e-Skin แล้ว
- ไม่แก้ตัวเลขผลวิจัยให้ดูดี ไม่ใช้ข้อมูล Robot เป็นเฉลยจริง ไม่อ้างว่าคะแนน schema คือคะแนนความถูกต้องเนื้อหา JSON
- Ass6 ล่าสุดที่ผู้ใช้บันทึกมีช่องวันที่เพิ่มหลังรอบตรวจ 25 หน้า ห้ามย้อนทับหรือรับรอง PDF เก่าว่าตรง Word ปัจจุบัน งานรอบนี้ไม่ได้แก้ Ass6

## ไฟล์ที่ทำแล้ว

ในโฟลเดอร์ [PRESENTATION_READY_2026-10-26](PRESENTATION_READY_2026-10-26):

1. [Ass5_REVIEWED_2026-10-26.pptx](PRESENTATION_READY_2026-10-26/Ass5_REVIEWED_2026-10-26.pptx) — 21 สไลด์ สำเนาแก้จากชุดที่ใช้พรี ไม่ทับต้นฉบับ
2. [Ass5_REVIEWED_2026-10-26.pdf](PRESENTATION_READY_2026-10-26/Ass5_REVIEWED_2026-10-26.pdf) — เปิดและส่งออกผ่าน PowerPoint สำเร็จ 21 หน้า
3. [SCRIPT_10_MIN_2_SPEAKERS.md](PRESENTATION_READY_2026-10-26/SCRIPT_10_MIN_2_SPEAKERS.md) — บทพูดแยกสองคนครบ 21 หน้า พร้อมเวลาแต่ละช่วง ประโยคส่งต่อ และแผนคลิป 2 นาที ยังต้องซ้อมจับเวลาจริง

### สิ่งที่แก้ในสไลด์

- หน้า 11: เปลี่ยนคำว่า “คะแนน YOLO หน้าถัดไป” ให้ชี้ไปสไลด์ 14 และย่อข้อความให้พอดี
- หน้า 18: ระบุว่าตารางเป็นการทดสอบส่งค่าดิบก่อนผู้ใช้ตรวจแก้ ไม่ใช่ความถูกต้องของยอดซื้อ และแยกจากคลิปที่จะสาธิตการตรวจแก้
- หน้า 19: ระบุคงโมเดลในหน่วยความจำ ยืนยันอัตโนมัติ ไม่รวมเวลาคนตรวจแก้
- คงตัวเลข ตาราง ลำดับหน้า และรูปแบบเดิม วันที่ใน footer คือวันที่ผลความก้าวหน้าชุดเดิม 18 ต.ค. ไม่ใช่วันทดสอบใหม่
- ยังไม่ได้อัดคลิป ยังไม่ได้ฝังคลิปหรือทำลิงก์เล่นคลิปใน PowerPoint
- speaker notes ใน PPTX ยังเป็นฐานเดิม ไม่ได้แทนด้วยบทพูด 10 นาที ให้ใช้ไฟล์ SCRIPT ใหม่เป็นบทซ้อมหลักระหว่างรอปรับ notes

### การตรวจสไลด์ที่ทำแล้วและยังค้าง

- ก่อนแก้ ตรวจ OCR 59/24/35 ภาพ, CER 82.36%/94.57%, ตาราง LLM ทั้ง 16 ช่องและ 288 รอบ, PC 9 รอบและค่ามัธยฐาน 10.758 เทียบไฟล์ผลทดลองแล้วตรง
- สไลด์ต้นทาง PPTX/PDF hash ตรงชุดที่เคยตรวจ ไม่ใช่ไฟล์ไม่ทราบที่มา
- ใช้ Artifact Tool import/edit/export และ finalizer ผ่าน: package/layout/font ไม่มี findings, มี native tables หน้า 17–19
- Final PPTX SHA256: `e6698c2874702a3568142f820b0745306681686190107717191533293a0ccb50`
- เปิด PowerPoint และ export PDF สำเร็จ แต่ยังไม่ได้ตรวจ slideshow/การเล่นคลิป
- Render ทุกหน้าแล้ว ทั้งจาก Artifact Tool และ PDF ที่ PowerPoint ส่งออก
- ตรวจภาพ Artifact Tool หน้า 1–19 แล้ว (หน้า 11 หลังย่อข้อความรอบสุดท้ายยังควรตรวจซ้ำ) หน้า 20–21 ยังไม่ได้เปิดดูในรอบนี้
- ตรวจภาพจาก PDF PowerPoint หน้า 13–17 แล้ว; รอบสุดท้ายต้องตรวจทุกหน้าจาก PDF โดยเฉพาะ 11/18/19/20/21
- ชื่อโฟลเดอร์ READY ไม่ใช่หลักฐานว่าเดโมผ่าน ต้องอ่านสถานะนี้ด้วย

### ไฟล์สำหรับทำสไลด์ต่อ

- `ass5_build/review_presentation_2026_10_26.mjs` — import source และแก้เฉพาะข้อความ Render PNG + candidate
- `ass5_build/finalize_review_2026_10_26.mjs` — finalizer ตัวปัจจุบัน ผ่านแล้ว
- `.codex-finalizer/review-2026-10-26/inspection.json`, `candidate.pptx`, `validation.json`
- ในโฟลเดอร์เดียวกัน: `slide-1.png` ถึง `slide-21.png`, `native-01.png` ถึง `native-21.png` และภาพ before/after
- authoring marker ถูกเรียกสำเร็จแล้วหนึ่งครั้งสำหรับ edit 1 PPTX ไม่ต้องเรียกซ้ำระหว่างงานเดียวกัน
- คำสั่ง builder จบพร้อม “Edited and rendered 21 slides” แต่ Node exit 1 โดยไม่มีข้อความ error หลัง render; finalizer และ PowerPoint เปิดผลสำเร็จ ต้องไม่อ้างว่า exit ของ builder เป็น 0
- finalizer ไม่ overwrite output เดิม หากแก้ต่อให้ใช้ชื่อ revision ใหม่

## เดโม: พบปัญหาและผลรันทดสอบจริง

ระบบเดิมมี Robot Framework + SeleniumLibrary + Selenium อยู่แล้ว ไม่ต้องติดตั้งเพิ่มเพื่อใช้ Chrome

### ปัญหาตัวเปิดบริการ — แก้แล้วและเปิดผ่าน

ไฟล์ `receipt_lab/preboard/services.py` เดิม configure รอ `/api/onboarding` เสมอ หลัง onboarding เสร็จ endpoint นี้ตอบ 404 ทำให้รอจนหมดเวลา ทั้งที่บริการทำงาน

แก้เป็น: ถ้ามี private credentials เดิมแล้ว ให้ refresh token และตรวจชื่อ instance ตามเดิมแทน onboarding; ถ้าไม่มี credentials จึงใช้ onboarding; HTTP 400/401/403/404 หยุดด้วย error ชัดเจน ไม่วนรอ ไม่สร้างบัญชีทับ

หลังแก้ ตัวเปิดขึ้น READY และ WebSocket checks ทั้ง 6 ผ่าน HA version 2026.10.2, instance Seminar Preboard Local

### Robot รอบที่ 1 หลังแก้ startup

รายงาน `DEMO_PRESENTATION_2026-10-21/robot_results/run-20261026-145851/`

- ผ่าน 1, ไม่ผ่าน 4
- Test 01 หน้าเดโมและเงื่อนไขก่อนเลือกผล: ผ่าน
- Test 02 รันภาพจริงรอ pending_review เกิน 180 วินาที
- Test 03–05 ล้มต่อเนื่องเพราะยังไม่มีรอบที่ผ่าน ไม่ใช่หลักฐานว่าแต่ละส่วนมีปัญหาอิสระทั้งหมด
- pipeline run `506518a0-4cce-4931-992f-dc707ba8ffbc`: LLM request_failed / TimeoutError, schema_valid false; ทั้งคำขอประมาณ 327.217 วินาที
- pipeline จัดเป็น pending_review พร้อมคำเตือนเมื่อ LLM ไม่สมบูรณ์ จึงต้องตรวจ `raw_result.llm.status` และ schema ไม่ใช่ดู pending_review อย่างเดียว

### Robot รอบที่ 2

รายงาน `DEMO_PRESENTATION_2026-10-21/robot_results/run-20261026-181432/`

- ผ่าน Test 01 และ Test 05; Test 02–04 ไม่ผ่าน (2 ผ่าน / 3 ไม่ผ่าน)
- pipeline run `fc2da996-0072-4e2c-985d-933a8bbffbe2`: LLM request_failed / ConnectionResetError 10054; schema_valid false; ทั้งคำขอประมาณ 75.545 วินาที
- Test 02 หยุดที่ assert schema/LLM ไม่ผ่าน ทำให้ raw_before ยังไม่ตั้ง
- Test 03 ส่งข้อมูลทดสอบได้ แต่การเทียบ raw_before ล้มเพราะ prerequisite จาก Test 02 ไม่สำเร็จ
- Test 04 ไม่มี EVENT เพราะ Test 03 หยุดก่อนตั้งตัวแปร
- Test 05 เข้าหน้า HA และเห็น event รอบทดสอบได้จริง แต่ไม่ทำให้ต้นทาง LLM กลายเป็นผ่าน
- ค่าล่าสุดใน HA อาจเป็น `ROBOT FRAMEWORK TRANSPORT TEST - NOT HUMAN TRUTH` / `AUTOMATED UI TEST ITEM` ยอด 45 จำนวน 1 ห้ามใช้เป็นเฉลยหรือข้อมูลที่มนุษย์ตรวจแล้ว

### จุดติดขัดล่าสุด: executable หาย

ก่อนทดสอบมี process `llama-server.exe` เริ่มได้ และ log ระบุโหลดโมเดลสำเร็จ/เริ่มสร้างประมาณ 116–120 tokens แล้วคำขอล้ม

ต่อมาทดลองเรียก LocalLLM แยก ได้ `StopIteration` ที่ค้นหา exe ตรวจแล้ว:

`C:\Users\NATCHAPOL\SeminarLab\tools\llama-b11714\llama-server.exe` **ไม่มีอยู่** (ตรวจซ้ำก่อนเขียน handoff ยัง False)

ในโฟลเดอร์ยังมี `llama-server-impl.dll`, CLI และ DLL อื่น; มี archive `C:\Users\NATCHAPOL\SeminarLab\tools\llama-b11714.zip`

- เครื่องติดตั้ง Windows Defender และ AVG Antivirus
- ไม่พบหลักฐาน Defender ที่ยืนยันการกักกันจากคำสั่งที่อ่านได้ ไม่มีหลักฐาน AVG quarantine ที่ตรวจแล้ว
- **สงสัยว่าเกี่ยวกับโปรแกรมป้องกันไวรัสได้ แต่ยังไม่ยืนยัน** ห้ามเขียนว่า AVG ลบแน่นอน
- ไม่ได้ปิด antivirus ไม่ได้เพิ่ม exclusion และไม่ได้คืน executable จาก archive
- urllib ไม่พบ proxy configuration จึงยังไม่มีหลักฐานว่าเกิดจาก proxy
- ยังไม่ได้แก้ `llm.py` หรือ registry โมเดล เพื่อรักษาหลักฐาน/การ pin รุ่นเดิม

## งานต่อไปตามลำดับ

1. ตรวจสาเหตุ executable หาย โดยดูประวัติ/Quarantine ของ AVG และแหล่งดาวน์โหลดเดิม ห้ามลดการป้องกันเครื่องอัตโนมัติ ถ้าจำเป็นให้ผู้ใช้ตรวจ/ตัดสินใจจากเหตุการณ์จริง
2. เมื่อได้ runtime ที่ตรวจสอบแล้วจึงรันภาพจริงใหม่ หากเปลี่ยนรุ่น/ระบบต้องบันทึกรุ่นและเงื่อนไขเดโมใหม่ ห้ามแทนคะแนนวิจัยเก่า
3. ปรับ error ของการหา executable จาก StopIteration เป็นข้อความที่ช่วยแก้ปัญหา และให้ตัวเปิดตรวจ asset พร้อมก่อน READY; ทดสอบกรณี exe หายโดยไม่ส่งข้อมูล/ลบหลักฐาน
4. ปรับ Robot ให้ test ที่พึ่งผลก่อนหน้าหยุด/skip พร้อมเหตุผลเมื่อไม่มี valid run แทนสร้าง failure ต่อเนื่อง และตรวจ fallback เลือกผลบันทึกด้วย (ยังไม่ได้ทำ)
5. รัน Robot suite ครบใหม่หนึ่งรอบหลังแก้ แล้วอ่าน log/ภาพจริง เทียบ event และค่า HA; ไม่ merge ผลเสียกับผลดีเพื่อปกปิดสาเหตุ
6. ตรวจการใช้เดโมที่ขนาดหน้าจอสำหรับอัดคลิป ตรวจภาษาไทย กรอบ OCR JSON การแก้รายการ ชื่อผู้ตรวจ ส่งและเช็ก event ระบุค่าทดสอบสังเคราะห์แยกจากข้อมูลที่เจ้าของงานตรวจจริง
7. ทำคู่มืออัดคลิป 2 นาทีพร้อมบทพากย์/ข้อความ “ตัดช่วงรอประมวลผล” และ “ย่อช่วงตรวจแก้โดยผู้ใช้” ยังไม่ได้สร้างไฟล์คู่มือเวอร์ชัน 26 ต.ค.
8. ทำ Q&A รายสไลด์ครบ 21 หน้า ทั้งสองคนต้องอธิบายศัพท์/ตัวเลข/แหล่งหลักฐานได้ ไฟล์นี้ยังไม่ได้สร้าง
9. จบ visual review ทุกหน้า ปรับ speaker notes ให้สัมพันธ์กับบทพูดใหม่ และสร้าง start-here ที่ชี้ไฟล์ล่าสุดไม่สับสนกับชุด 21 ต.ค.
10. ซ้อมจับเวลาจริงกับผู้ใช้ คลิปยังไม่มี ต้องบันทึก/ตรวจการเล่นไฟล์ก่อนรับรองว่าชุดพรีพร้อม
11. อัปเดต handoff/README และ commit/push เฉพาะงานรอบนี้เมื่อพร้อม มี authorization push งานแชร์จากบริบทก่อนหน้า แต่คำสั่งล่าสุดคือทำ handoff จึงยังไม่ push รอบนี้

## ตัวเลขที่ต้องรักษา

- รับ 124 ไฟล์ → 113 ภาพไม่ซ้ำระดับ SHA-256 → 59 ภาพผู้สมัครใบซื้อสินค้า ไม่ใช่ 59 ธุรกรรมอิสระ
- ข้อความอ้างอิงหนึ่งคนหนึ่งรอบ 59 ภาพ; CER ใช้ 24 ภาพ, อีก 35 ไม่รวม; ตัวหาร 28,011 ตัวอักษร
- EasyOCR micro CER 82.36%, Tesseract 94.57% เป็นความผิดพลาด ยิ่งต่ำยิ่งดี ไม่ใช่คะแนนชุดทดสอบอิสระ
- YOLO ฝึก 38 ตรวจฉากเดิม 10 (mAP@0.5 0.928) / ส่งเพิ่มเดิม 6 (0.237, หมุนอ่านตรง 0.714) / กันออก 5
- LLM 288 รอบ: 4 รุ่นย่อย × 2 แหล่งข้อความ × 2 grammar × 6 ภาพ × 3 รอบ; วัดโครงสร้าง ไม่ใช่ semantic accuracy; Q4_K_M แปลงต่อจาก Q8_0
- timing เดิม 3 ภาพ × 3 รอบ = 9, median 10.758 วินาที ไม่รวมคนตรวจ คงโมเดลค้าง/ยืนยันอัตโนมัติ
- ยังขาดเฉลย JSON ครบฟิลด์, fresh-scene test, การรับรองกลุ่มธุรกรรม/กรอบทั้งหมด, NPU/พลังงาน RK3588

## เครื่องมือ/ตำแหน่ง

- Demo http://127.0.0.1:8090/demo ; HA http://127.0.0.1:8123/config/tools/state
- MQTT port 18884 topic `seminar/preboard/purchases/latest`
- เริ่มระบบ/Robot: `DEMO_PRESENTATION_2026-10-21/Run-Robot-Tests.ps1` เรียก Start-Demo.ps1 ก่อน
- test source: `tests/robot/demo_presentation.robot`, `tests/robot/DemoEvidence.py`
- Python demo: `C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe`
- Python Robot: `C:\Users\NATCHAPOL\SeminarLab\.venv-robot\Scripts\python.exe`
- Artifact Node: `C:\Users\NATCHAPOL\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`
- Artifact Python: `C:\Users\NATCHAPOL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
- Private runs: `C:\Users\NATCHAPOL\SeminarLab\preboard\runs\<run-id>\pipeline.json`
- Private credentials: `C:\Users\NATCHAPOL\SeminarLab\preboard\services\ha_auth.json` ห้ามพิมพ์ค่า/ใส่ repo/รายงาน
- Linux services: `/home/natchapol/SeminarLab/preboard-services`
- Shell PowerShell; เขียนไฟล์ภาษาไทยด้วย apply_patch หลีกเลี่ยง pipe source ที่มีภาษาไทยเข้า Python เพราะอาจกลายเป็น `?`; print ภาษาไทยต้อง sys.stdout.reconfigure(encoding='utf-8')
- ยึด skills Presentations สำหรับแก้ PPTX; อ่าน implementation/template/finalization แล้วในรอบนี้ ไม่มีการ spawn agent

## ข้อควรระวัง Git

working tree มีงาน/ไฟล์ลบค้างจากก่อนงานนี้จำนวนมาก เช่น ass6_output หลายรุ่น ห้าม `git add -A` หรือ reset/restore ทั้ง repo งานรอบนี้คือ services.py, ass5_build สองไฟล์, PRESENTATION_READY_2026-10-26, ผล Robot ใหม่ และ handoff นี้ ตรวจ secrets ก่อน push รายงานทดสอบทุกครั้ง
