# Handoff หลัง review ชุดพรี 10 นาที — 26 ตุลาคม 2569

เริ่มใช้ที่ [PRESENTATION_READY_2026-10-26/START_HERE.md](PRESENTATION_READY_2026-10-26/START_HERE.md) ผลตรวจละเอียดอยู่ใน [REVIEW_RESULTS](PRESENTATION_READY_2026-10-26/REVIEW_RESULTS_2026-10-26.md)

## คำสั่งและขอบเขต

ผู้ใช้ขอ review สไลด์ บทพูด ทดสอบเดโมด้วย Robot Framework/Selenium และขั้นตอนพรีทั้งหมดภายใน 10 นาที ต่อมาผู้ใช้แจ้งว่าเพิ่งปิด antivirus และให้ลองใหม่ ผู้ช่วยไม่ได้ปิด antivirus หรือเพิ่ม exclusion เอง

ยังใช้เงื่อนไขพรีสองคน: ธนบดีหน้า 1–13 ณัชพลหน้า 14–21 ทั้งคู่ต้องเข้าใจทุกหน้า เป้าพูดรวมเดโม 9 นาที เผื่อ 1 นาที เดโมไม่เกิน 2 นาที ฐาน Ass4/Ass5 และตัวเลขวิจัยคงเดิม

## ผลที่ทำเสร็จ

- ตรวจภาพ native PDF ครบ 21 หน้า เทียบ OCR/LLM/timing กับรายงานเดิม
- สร้าง `Ass5_10MIN_REVIEWED_v2_2026-10-26.pptx` และ PDF ใส่บทพูดหลักใน notes ครบ 21 หน้า โดยเก็บ details/แหล่งเดิมไว้ในส่วนเตรียม Q&A
- แก้เฉพาะหน้าสไลด์ 18 ให้ไม่อ้างว่ามีคลิปตรวจจริงแล้ว ทั้ง 20 หน้าอื่นเหมือน native PDF เดิมทุกพิกเซล
- เพิ่ม `SCRIPT_10_MIN_REVIEWED_v2.md`, `DEMO_2_MIN_RUNBOOK.md`, `QA_ALL_21_SLIDES.md`, `REVIEW_RESULTS_2026-10-26.md` และอัปเดต START_HERE/README
- finalizer ผ่าน package/layout/font มี native tables หน้า 17–19 PowerPoint เปิดและ SaveAs PDF สำเร็จ 21 หน้า
- Notes ทั้ง 21 ส่วนและตาราง LLM ทั้ง 16 ช่องตรงแหล่งข้อมูล `content_verification.json` บันทึกใน `.codex-finalizer/review-complete-2026-10-26/`

PPTX SHA256 `0c6e6329b58f7fdc40a1fed112bb23b4a4ab496a6a84929542986a39f24cb6d2`

PDF SHA256 `c996bae4127a1dfcd4992d01bc36b1def40e5d521715a9eb077577a699b3ca6b`

Artifact builder exit 1 หลังพิมพ์ว่าสร้างเสร็จและได้ candidate จริง (เหมือนรอบก่อน) ไม่อ้างว่า builder exit 0 ตัว finalizer exit 0 เป็นคนละขั้น PowerPoint ExportAsFixedFormat ผ่าน COM ไม่รับ argument จึงใช้ SaveAs ชนิด PDF ซึ่งสำเร็จ

## Runtime และปัญหาเดโม

1. อ่าน `C:/ProgramData/AVG/Antivirus/chest/index.xml` พบรายการต้นทาง `SeminarLab/tools/llama-b11714/llama-server.exe` และ detection `IDP.Generic` ขณะอ่าน exe ไม่มีอยู่ จึงมีหลักฐานการกักกันแล้ว ต่างจาก handoff ก่อนที่เป็นข้อสงสัย
2. หลังผู้ใช้แจ้งปิด antivirus ตรวจ archive เดิม SHA256 `f78eded047061a3f86372db426797400a2f1bb0ec37868d5927dd820eb3386c0` ตรง GitHub release API ของ `ggml-org/llama.cpp`, asset `llama-b11714-bin-win-cpu-x64.zip` แล้วคืนเฉพาะ exe ที่ขาด ไม่มีการเปลี่ยนรุ่น/DLL/โมเดล
3. exe SHA256 `12c015512d280661fc53ed59f2d8f5cdba3ca9b6948a891eab3087cd93b1154d` การตรง hash ไม่พิสูจน์ว่า detection เป็น false positive
4. เพิ่ม `receipt_lab/preboard/demo_preflight.py` ให้ตรวจ exe/ไฟล์โมเดลก่อนเปิด live mode เปลี่ยน StopIteration ใน llm.py เป็นข้อความชัดเจน และ Start-Demo.ps1 มี `-SavedResultsOnly` ที่ประกาศโหมดชัด
5. ไม่มี `SeminarLab/preboard/selection.json` ในตอนแก้ driver จึงไม่แก้ frozen selection หรือหลักฐานเก่า driver hash ใหม่จะต่างจากรอบทดลองเดิมตามจริง
6. พบภาพโหลดถูก reset ทั้ง Selenium และการดาวน์โหลดวินิจฉัย แก้ `Handler.protocol_version='HTTP/1.1'` แล้ว Chrome โหลดครบและ suite ผ่าน แต่ urllib ที่ปิด connection ยังพบ reset ใน probe จึงไม่สรุปว่าแก้ระบบเครือข่ายทุก client หรือกล่าวโทษ AVG สำหรับปัญหาภาพโดยไม่มีหลักฐาน
7. restart เฉพาะ process ที่ฟัง 8090 และยืนยัน command line ว่าเป็น `receipt_lab.demo_pc.server` บริการ HA/MQTT เดิมไม่ถูกลบ/ตั้งใหม่ log ล่าสุด `SeminarLab/preboard/services/demo-review-http11.stdout.log` และ `.stderr.log`
8. หลังดู screenshots พบชื่อผู้ตรวจเติมชื่อคนเมื่อเปิดผล Robot ย้อนหลัง จึงเพิ่ม `last_confirmed_by` จาก revision ล่าสุดใน Store.get และให้ UI แสดง/เติมชื่อผู้ยืนยันที่บันทึกไว้แทนค่า default พร้อมลดคำขอภาพซ้ำใน saved-result handler รัน core tests 13 กรณีผ่านและ Robot ใหม่ครบ 7/7 log บริการรอบสุดท้าย `demo-review-final.stdout.log` / `demo-review-final.stderr.log`

## ผลการทดสอบ

- ชุด unit preboard 50 กรณีผ่านก่อนปรับ HTTP; หลังปรับ HTTP รัน request protection 7 กรณีผ่าน และเพิ่มทดสอบ large binary สองคำขอบน connection เดียวอีก 1 กรณีผ่าน
- `run-20261026-183411`: 4 ผ่าน / 3 ไม่ผ่าน (ภาพ/fallback/viewport) LLM และ transport ผ่านแล้ว ไม่ลบหรือผสานกับรอบใหม่
- `run-20261026-184455`: 7 ผ่านในรอบหลังแก้ HTTP ก่อนแก้ชื่อผู้ยืนยันเดิม
- `run-20261026-185448`: **7 ผ่าน / 0 ไม่ผ่าน / 0 skip ในการรันครั้งเดียว** รวม inference จริง LLM/schema ภาพ/กรอบ/OCR/JSON การแก้ฟอร์ม ส่ง HA ส่งซ้ำ เปิด HA UI fallback read-only และสอง viewport
- เพิ่มการ skip ตาม prerequisite อย่างชัดเจน และตรวจ fallback ไม่สร้าง inference/ไม่เปลี่ยน record แยก expected HTTP 400 สำหรับชื่อผู้ตรวจว่างจาก browser errors อื่น
- ภาพจอ 1366×768 ต้องเลื่อนหลายช่วง ไม่มี horizontal page overflow จอ 1920×1080 เห็นมากกว่า ควรซ้อมการเลื่อนตาม runbook

ผลผ่านหลัง antivirus change ของผู้ใช้เท่านั้น **ยังไม่ได้ทดสอบเมื่อเปิด antivirus กลับ** ไม่แนะนำให้ปิดค้างเป็นวิธีใช้ปกติ

ค่า HA ล่าสุดเป็น Robot synthetic: 45/1, merchant `ROBOT FRAMEWORK TRANSPORT TEST - NOT HUMAN TRUTH`, item `AUTOMATED UI TEST ITEM`, date `2026-10-21` ไม่ใช่การตรวจจริงจากเจ้าของงาน

- receipt `f63be3b7-e6e5-4178-b79e-46b1b7cc0c3c`
- pipeline `5c4ba623-b27a-44b7-b7ce-90ae63edb8a1`
- event `f63be3b7-e6e5-4178-b79e-46b1b7cc0c3c:1`
- URL ผลย้อนหลังสำหรับตรวจทางเทคนิค: `http://127.0.0.1:8090/demo?receipt=f63be3b7-e6e5-4178-b79e-46b1b7cc0c3c` ต้องเปิดเผยว่าเป็นรอบ Robot

## ค้างก่อนขึ้นพรี

1. ยังไม่มี `DEMO_2_MIN.mp4` และไม่มีการฝังคลิป ผู้ใช้ต้องตรวจข้อมูลจริงก่อนอัดคลิป human-review หรือเลือกผลย้อนหลังพร้อมเปิดเผยที่มา Runbook ให้ทั้งสองเส้นทางแล้ว
2. ยังไม่จับเวลาคนพูดจริง เป้า 9 นาทีเป็นแผน ต้องซ้อมทั้งสองคนรวมคลิกและเปลี่ยนหน้าต่าง ไม่เกิน 9:30
3. ยังไม่ยืนยัน Presenter View/การเล่นคลิปใน Slide Show ตรวจ PDF แล้วแต่ไม่ใช้แทนการตรวจคลิป
   พยายามเริ่ม Computer Use ผ่าน node_repl สองครั้งแล้วล้มจาก Windows sandbox helper: `helper_sandbox_lock_failed`, `SetNamedSecurityInfoW ... 5` ไม่มีการกด UI PowerPoint ผ่านเครื่องมือนี้
4. ควรเปิดการป้องกันเครื่องกลับและลองเดโมในสภาพที่จะใช้พรี หากถูกกักอีกต้องให้ผู้ใช้ตัดสินใจจากหลักฐาน ไม่เพิ่ม exclusion หรือเปลี่ยนรุ่นโดยไม่บันทึก
5. Ass6 ไม่แก้ และไม่รับรอง PDF รุ่นก่อนว่าตรง Word ที่ผู้ใช้บันทึกล่าสุด

## Git และการทำต่อ

ผู้ใช้สั่ง push ชุดรีวิวแล้ว ขอบเขต commit คือชุดพรีวันที่ 26 ต.ค. โค้ดเดโม/ตัวทดสอบที่เกี่ยวข้อง ผล Robot ทั้งรอบล้มและรอบผ่าน และ handoff ส่วนงาน Ass6/ไฟล์ลบ/งานเก่าอื่นยังแยกค้างไว้ในเครื่อง ตรวจสถานะเผยแพร่จาก commit ของ branch `pc-preboard-implementation` ห้าม git add -A หรือ reset/restore ทั้ง repo

โค้ดใหม่/แก้รอบนี้: demo_preflight.py, llm.py, demo_pc/server.py, Start-Demo.ps1, Robot suite/library, test_demo_preflight.py, test_http_transfer.py, สคริปต์ probe ใน tests/robot และสคริปต์ build/audit/finalize ใน ass5_build ที่มี complete_review/review_2026_10_26 ในชื่อ

services.py เป็นงานแก้จากรอบก่อน มีอยู่แล้วก่อนเริ่ม turn นี้ อย่าเหมารวมเป็นการแก้ใหม่ทั้งหมด

เพิ่มเติมจากรายการ paths ด้านบน: `receipt_lab/demo_pc/store.py`, `receipt_lab/demo_pc/index.html`, `tests/preboard/test_core.py` แก้เรื่องผู้ยืนยันเดิม; ผล review ที่อ่านด้วยโปรแกรมอยู่ `reports/preboard/presentation_review_2026-10-26.json`
