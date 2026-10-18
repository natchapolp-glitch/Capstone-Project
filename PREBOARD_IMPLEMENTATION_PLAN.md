# แผนส่งต่อให้ 6.1 sol ทำงานบน PC ก่อนมีบอร์ดครบ 5 ข้อ

วันที่ 18 ตุลาคม 2569 — โครงงาน SCS3-4 กลุ่มสอบ SCS3

**ขอบเขตส่งมอบล่าสุดแทนจุดหยุดในแผนเดิมด้านล่าง:** ผู้จัดทำให้ทดลองส่วนที่มีข้อมูล ตรวจทวนเอง และเพิ่มผลใน Ass5 สไลด์–บทพูดกับ Ass6 โดยคงฐานเดิม ไม่ต้องหยุดรอผู้วางแผนอีกครั้ง ความถูกต้องเชิงเนื้อหา JSON และภาพต่างฉากใหม่ให้ระบุว่า **ยังไม่ได้ทดลอง** และไม่ต้องรอเพื่อส่งมอบเอกสาร ดู [เป้าหมายล่าสุด](ASS5_ASS6_COMPLETION_GOAL.md) และ [handoff ปัจจุบัน](HANDOFF_ASS5_ASS6_FOR_TEAM_2026-10-18.md) แผนรายละเอียดและเกณฑ์วิจัยเดิมยังเก็บไว้ด้านล่างเพื่ออ้างอิง ไม่ถือว่าทุกเกณฑ์ผ่านเพียงเพราะเอกสารส่งมอบแล้ว

**คำสั่งล่าสุดของผู้ใช้ มีผลแทนข้อกำหนดการตรวจด้านล่าง:** ใช้ข้อมูลที่เพิ่งกรอกเพียงรอบเดียว (`single_reviewer_single_pass`) โดยนายณัชพล เพ็งพล ผู้ใช้ตั้งใจกรอกข้อความทุกบรรทัดเป็นหลัก ไม่ต้องให้ทำรอบสองหรือหาผู้ตรวจอีกคน ช่อง JSON และรายการสินค้าที่เว้นไว้คือยังไม่ได้ตรวจ ห้ามตีความว่าไม่มีข้อมูลจริง และห้ามนำไปเป็นเฉลยวัดความถูกต้อง JSON ข้อมูลเก่าและประวัติการแก้ต้องเก็บไว้ทั้งหมด

การเทียบ OCR ใช้สำเนาข้อความรอบเดียวที่ตรึงแล้ว รายงานจำนวนที่บันทึกจริง ภาพขาด ภาพอ่านไม่ครบ และการใช้ OCR ช่วยกรอก ผลบนชุดเดิมเป็นการเปรียบเทียบเชิงพรรณนา ไม่ใช่ผลชุดทดสอบอิสระ ส่วน Local LLM วัดการ parse/schema เวลา และ RAM ได้จริง แต่ความถูกต้องของเนื้อหา JSON ยังไม่มีเฉลยครบ จึงรายงานว่าไม่มีคะแนน ไม่ให้ผู้ใช้ต้องย้อนกรอกเพิ่มเพื่อผ่านเกณฑ์เก่า การทดสอบภาพต่างฉากใหม่ยังต้องมีภาพจริงจึงจะอ้างว่าได้ทำแล้วได้

## คำสั่งและจุดหยุด

ผู้ใช้ให้รอบนี้จัดทำแผน จากนั้นจะเปลี่ยนเป็น 6.1 sol เพื่อ implement เมื่อได้หลักฐานครบทั้ง 5 ข้อจึงส่งกลับให้โมเดลผู้วางแผน review แผนนี้ยังไม่ใช่ผลการทดลอง และการตั้ง goal ไม่ได้เปลี่ยนโมเดลให้อัตโนมัติ

ทำงานต่อเนื่องตาม dependency ไม่หยุดหลังสร้างโครงโค้ดหรือทดสอบด้วยข้อมูลสมมติ ความแม่นยำต่ำเป็นผลทดลองที่รายงานได้ ไม่ต้องแต่งคะแนนให้ผ่าน แต่ห้ามประกาศงานเสร็จเมื่อยังไม่มีผลรันจริงหรือข้อมูลอ้างอิงตามเกณฑ์ ระหว่างรอข้อมูลจากผู้ใช้ให้ทำส่วนที่ไม่ขึ้นต่อข้อมูลนั้นต่อ

งานที่ต้องมีคนจริงหรือข้อมูลใหม่ เช่น ผู้ตรวจเฉลยอีกคนและการถ่ายภาพต่างฉาก ไม่สามารถแทนด้วยการให้ AI อ่านซ้ำหรือสร้างภาพจำลองได้ ถ้ายังไม่ได้รับ ให้บันทึก `WAITING_HUMAN` / `WAITING_DATA` และถามเฉพาะสิ่งที่ขาด พร้อมทำงานอิสระอื่นต่อ ห้ามเปลี่ยนเกณฑ์ให้ครบ 5 ข้อโดยปิดบังสิ่งที่ค้าง เมื่อทุกข้อผ่านให้ใช้สถานะ `READY_FOR_REVIEW` และหยุดแก้งานเพื่อส่งหลักฐานให้ reviewer; ไม่หมายถึง reviewer อนุมัติแล้ว

## สถานะที่ตรวจจริงก่อนส่งต่อ

| รายการ | หลักฐาน/สถานะ ณ รอบวางแผน |
|---|---|
| Repository | `C:\Users\NATCHAPOL\OneDrive\เดสก์ท็อป\Seminar`; main ที่ `ab9d08b` ก่อน commit แผนนี้ |
| พื้นที่ทดลอง | `C:\Users\NATCHAPOL\SeminarLab` อยู่นอก OneDrive |
| Python เดิม | `.venv\Scripts\python.exe`, Python 3.13.7; EasyOCR 1.7.2, torch 2.14.1+cpu, ultralytics 8.4.178, psutil 7.2.2 |
| ทรัพยากร | RAM ประมาณ 16 GB; พื้นที่ C: ว่างประมาณ 18.8 GiB ต้องวัดซ้ำก่อนดาวน์โหลด |
| Runtime | พบ WSL Ubuntu; ไม่พบ docker, tesseract, ollama, llama-server ใน PATH ยังไม่ยืนยันว่าไม่มีติดตั้งที่อื่น |
| ภาพ | manifest 124 ไฟล์, 113 SHA ไม่ซ้ำ, ผู้สมัคร 59 ภาพ; ภาพไม่เท่ากับธุรกรรม |
| ชื่อสินค้า | `language_truth_59/records` 59 รายการ: ถอดชื่อครบครั้งแรก 12, ไม่ครบ 45, ไม่มีบรรทัด 2; ไม่มีผู้ตรวจคนที่สอง |
| เฉลยเต็ม | `ground_truth_text` และ `ground_truth_json` ยังว่าง; มีเพียงร่างใน `annotation_drafts` จึงห้ามนำ 12 ภาพที่อ่านชื่อครบมาอ้างว่าเฉลยทั้งใบพร้อมแล้ว |
| YOLO เดิม | ฝึก 38 / validation 10 / ต่างฉาก 6 / กันออก 5; mAP@0.5 เดิม 0.9276 และ 0.2371; เป็นผล PC ชุดเล็กและ label ตรวจโดย assistant |
| OCR เดิม | EasyOCR มี weights ใน `models/easyocr`; spot-check 3 ภาพ วันที่/ยอดตรง 4/6 ช่อง ไม่ใช่ CER |
| JSON | `receipt_schema.json`, `json_extraction_scorer.py`, `JSON_SCORING_PROTOCOL.md`; regression 10 กรณีผ่าน แต่ยังไม่มีผล Local LLM |
| ไฟล์ส่งงาน | Ass5 18 สไลด์/บทพูด; Ass6 PDF 17 หน้า ใช้ฐาน Ass4 และ Ass5 ก่อน feedback; ผู้ใช้ให้เน้นเนื้อหา |

เอกสารเก่าบางไฟล์ยังระบุไม่มีภาพ, pilot 20 ภาพ หรือ schema `store_name/date/total/category` ซึ่งล้าสมัย ได้แก่ `plan_ass5_ass6_before_board.md`, `pilot_experiments_design_v1.md`, `receipt_lab/annotation_guidelines.md` อย่านำข้อเหล่านั้นมาทับสถานะใหม่ ให้ปรับคำเตือนและแนวปฏิบัติเมื่อ implement โดยเก็บประวัติการเปลี่ยนไว้

## ลำดับทำงานและโครงไฟล์

1. ตรวจ git status, อ่าน handoff และแผนนี้; รักษาไฟล์ของผู้ใช้และงานเดิม สร้าง branch `pc-preboard-implementation` หรือใช้ branch เดิมของงานนี้ถ้ามีแล้ว
2. เก็บ environment และเวอร์ชันก่อนติดตั้งเพิ่ม ใช้ venv แยกหาก dependency ชนกันกับชุด YOLO เดิม ห้ามอัปเกรดชุดเดิมทั้งชุดโดยไม่มีเหตุผล
3. ทำข้อ 1 พร้อมเครื่องมือรับผลตรวจจากคน และเริ่มข้อ 2–4 ส่วนโค้ด/ข้อมูลสมมติระหว่างรอได้ ติด instrumentation ของข้อ 5 ตั้งแต่การรันครั้งแรก
4. ตรึงเฉลยและ split แล้วรันข้อ 2 → เลือก OCR จาก development set → ข้อ 3 → เลือก configuration จาก development set → ข้อ 4 → สรุปข้อ 5 บน evaluation set
5. ทำ review packet, ตรวจเกณฑ์ทั้งหมด, commit/push branch และส่งให้ review ไม่แก้ Ass5/Ass6 `READY` เดิมด้วยผลใหม่จนผ่าน review; ทำร่างส่วนเพิ่มแยกได้

โครงที่ให้สร้าง/ปรับ (ปรับชื่อได้ถ้ามีเหตุผลและอัปเดต handoff):

```text
receipt_lab/preboard/           # config, dataset validation, OCR/LLM runners, metrics, CLI
receipt_lab/demo_pc/            # pipeline, review UI, persistence, MQTT adapter
tests/preboard/                # tests ที่กันคะแนนผิด/ข้อมูลรั่ว/ส่งซ้ำจริง
experiments/preboard/           # config, split IDs, environment, aggregate results
reports/preboard/               # ผลสรุปและรายการหลักฐานสำหรับ review
PREBOARD_STATUS.md             # สถานะ 5 ข้อ พร้อม next command และ dependency ที่รอ
PREBOARD_REVIEW_PACKET.md       # reviewer เริ่มอ่านจากไฟล์นี้

SeminarLab/preboard/            # ข้อมูลละเอียดและผลรันจริงนอก OneDrive
  dataset/                     # manifest รุ่นตรึง, group IDs, coordinate transforms
  annotations/                 # first pass, independent review, adjudication
  runs/<run_id>/               # input/output hashes, raw output, timing, errors
  services/                    # local broker / Home Assistant configuration and state
```

ใช้ `doc_id` และ `transaction_group_id` เชื่อมทุกชั้น ไม่อ้าง absolute path เป็นตัวระบุข้อมูลเพียงอย่างเดียว ใช้ config ระบุ lab root ได้ ผลสรุปใน repo ต้องตรวจย้อนถึงไฟล์จริงและ SHA-256 ได้ ห้าม commit weights, venv, token หรือ cache ขนาดใหญ่ ภาพดิบเดิมที่ผู้ใช้อนุญาตให้อัปโหลดแล้วให้คงไว้; ไม่สร้างสำเนาข้อมูลส่วนบุคคลเพิ่มโดยไม่จำเป็น

## 1. ทำเฉลย กรอบ และกลุ่มธุรกรรมให้พร้อม

### งานที่ต้องทำ

- ตรวจผู้สมัครทั้ง 59 ภาพ โดยอ้างต้นฉบับจาก manifest: ชนิดเอกสาร, พิมพ์/เขียนมือ, จำนวนหน้า/ธุรกรรมในภาพ, ความอ่านได้, ทิศภาพ, กรอบเอกสาร และความสัมพันธ์กับภาพอื่น
- SHA-256 ใช้หาภาพไฟล์ซ้ำ; perceptual hash/ความคล้ายภาพใช้เสนอคู่ให้ตรวจเท่านั้น ไม่ยืนยันธุรกรรมซ้ำอัตโนมัติ ใช้ร้าน วันที่ เลขใบเอกสาร และรายการเป็นหลักฐานเมื่ออ่านได้ บันทึก `uncertain` หากยังสรุปไม่ได้
- บันทึกกรอบในพิกัดต้นฉบับและ transformation เมื่อหมุน/crop ตรวจ overlay ทุกภาพที่ใช้วัด ห้ามใช้กรอบที่แก้แล้วกับภาพที่หมุนคนละทิศ ภาพหลายใบ/หลายหน้าต้องแยก region และประกาศกติกาประกอบธุรกรรม; ห้ามบีบเป็นกรอบเดียวเพื่อให้เข้ากับสคริปต์เดิม
- แยกสถานะ `not_started`, `draft_ai`, `human_transcribed`, `partial_unreadable`, `no_item_lines_visible`, `independently_reviewed`, `adjudicated` และเก็บผู้ตรวจ/เวลา/รุ่น/เหตุผล ไม่ map `transcribed_once` เดิมเป็น human-reviewed โดยอัตโนมัติ
- ทำ transcript พร้อม line/region ID และ JSON จากภาพตาม schema กลาง ครอบคลุมวันที่ ร้าน สินค้า จำนวน หน่วย ราคาต่อหน่วย ยอดต่อรายการ ยอดรวม และสกุลเงิน ไม่ใช่แค่ชื่อสินค้า
- `null` ในเฉลยหมายถึงข้อมูลไม่ปรากฏจริง; ข้อมูลมีอยู่แต่อ่านไม่ได้/กำกวมต้องแยกสถานะใน metadata และไม่นำเฉลยนั้นไปให้คะแนนเต็มเอกสาร ถ้าจะวัดเฉพาะช่วงที่อ่านได้ให้แยกชุด/ตัวหาร/ROI อย่างชัดเจน
- กำหนดกติกาวันที่ พ.ศ./ค.ศ., หน่วยสินค้า, ส่วนลด/คืนสินค้า, ราคารวมกับราคาต่อหน่วย และสกุลเงินไว้ก่อนตรวจเฉลย ห้ามเดาสกุลเงิน/จำนวนหรือคำนวณค่าทดแทนโดยไม่ระบุว่าอนุมาน
- ทำหน้าหรือแพ็กเกจให้ผู้ตรวจคนที่สองตรวจจากภาพ โดยไม่เห็นคำตอบโมเดลที่กำลังประเมิน เก็บความเห็นแยกแล้วทำ diff/adjudication ไม่เขียนทับการตรวจรอบแรก การตรวจโดย AI อีกรอบใช้เป็น QA ได้แต่ไม่นับเป็นคนที่สอง
- แบ่ง development/evaluation ตามกลุ่มธุรกรรมก่อนปรับ prompt หรือเลือกโมเดล กลุ่มที่ยังสงสัยว่าซ้ำให้จัดร่วมกันหรือกันออก ไม่มีธุรกรรมข้าม split

### เกณฑ์ผ่าน

- มี manifest ครบ 59 พร้อมกรอบหรือเหตุผลที่ไม่ใช้, group IDs, สถานะความอ่านได้ และที่มารูปตรวจย้อนครบ
- มีชุด pilot เต็มเอกสารที่ผ่านผู้ตรวจคนที่สองจริงและตกลงเฉลยแล้วอย่างน้อย **6 ธุรกรรมอิสระจากอย่างน้อย 2 แหล่งร้าน/เอกสาร** นี่เป็นขั้นต่ำเพื่อให้เริ่มเปรียบเทียบได้ ไม่ใช่หลักฐานว่าขนาดตัวอย่างเพียงพอสรุปทั่วไป ใช้ข้อมูลที่เข้าเกณฑ์ได้มากกว่านี้ทั้งหมดตาม split ที่ตรึง
- รายงานจำนวนทุกสถานะ รวมผู้ตรวจยังค้าง โดยยอดต้อง reconcile กับ 59; ไม่บังคับให้อ่านครบทุกภาพและไม่เติมคำที่อ่านไม่ออก
- validator ปฏิเสธเฉลย schema เก่า, ID ซ้ำ, missing image, bbox นอกภาพ, split leakage และสถานะ reviewed ที่ไม่มีหลักฐานผู้ตรวจ

## 2. ทดลอง OCR อย่างเป็นระบบ

- Baseline: EasyOCR `th+en` ที่มีแล้ว เทียบ Tesseract `tha+eng` ตรวจ runtime/language files และตรึงเวอร์ชัน ถ้ามีเหตุจำเป็นเปลี่ยน engine ต้องบันทึกก่อนเห็นคะแนน evaluation
- อ่านคู่มือทางการก่อนติดตั้ง Tesseract และเลือกไฟล์ภาษาให้ตรงรุ่น: https://tesseract-ocr.github.io/tessdoc/Installation.html
- เปรียบเทียบบนภาพ/region/การหมุนเดียวกัน แยก (A) crop อ้างอิงจากเฉลยเพื่อวัด OCR และ (B) crop จาก YOLO เพื่อวัดข้อผิดพลาดสะสม ห้ามใช้ crop เฉลยแล้วเรียกว่า end-to-end
- กำหนด reading order และขอบเขต transcript ให้ตรงภาพที่ส่งเข้า OCR หากปิดบังข้อมูลบางส่วนต้องใช้สำเนา/ขอบเขตเดียวกันทั้งสอง engine และเฉลย ไม่เทียบ OCR ทั้งใบกับเฉลยชื่อสินค้าอย่างเดียว
- ตรึง normalization (Unicode NFC, newline, whitespace) และ Thai tokenizer ก่อนรัน ใช้ CER เป็นหลัก รายงาน micro CER = ผลรวม edit distance / ผลรวมจำนวนอักษร และ macro ต่อเอกสารแยกกัน WER ใช้ tokenizer รุ่นเดียวกัน; ถ้าไม่มีห้ามเรียก whitespace split ว่า Thai WER
- แก้ `cer_wer_calculator.py` หรือใช้โมดูลใหม่: missing output/timeout ต้องอยู่ในตาราง ไม่ถูกข้าม; empty reference ให้ N/A พร้อมเหตุผล; OCR ว่างบน reference ที่ไม่ว่างคือ deletion ทั้งหมด; CER อาจมากกว่า 1 ได้
- วัดวันที่/ยอดรวม/ชื่อสินค้าโดยใช้ region alignment หรือ field extractor กติกาเดียวกันทั้งสองเครื่องมือ ระบุวิธีและตัวหาร ไม่ใช้ LLM ต่างกันจนปนผล OCR
- เก็บ raw OCR boxes/text/confidence, error, เวลา และ input hash ก่อน normalization

**เกณฑ์ผ่าน:** มีผลรันจริงสอง engine บนชุดประเมินเดียวกันจากข้อ 1, ตารางรายภาพและผลรวมที่คำนวณซ้ำได้, ความล้มเหลวไม่หายจากตัวหาร, ตัวอย่างผิดอย่างน้อย 3 แบบที่พบจริงหรือบอกว่าพบไม่ถึง 3; tests สำหรับ insertion/deletion/empty/missing และไทย normalization ผ่าน

## 3. ทดลอง Local LLM → JSON

- ใช้ runtime local ที่บังคับ decoding grammar ได้ เช่น llama.cpp; อ่านเอกสารและบันทึก release/commit จริง: https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md
- เลือก **2 checkpoint ขนาดประมาณ 0.5–2B** ที่มีสิทธิใช้ชัด รองรับข้อความไทย และมี weights ที่ยืนยันที่มาได้; เลือกจาก model card ทางการ ณ ตอน implement ไม่ยึดชื่อโมเดลเก่าใน pilot v1 โดยไม่ตรวจ
- ต่อ checkpoint ใช้ **2 ระดับ quantization** เช่น Q4_K_M และ Q8_0 ของ weights รุ่นเดียวกัน มี source revision/hash ห้ามเปรียบเทียบคนละ checkpoint แล้วเรียกว่าผล quantization
- Matrix หลัก: 2 โมเดล × 2 quantization × grammar เปิด/ปิด × input เฉลย/OCR = **16 เงื่อนไขต่อเอกสาร** ใช้ OCR ที่เลือกจาก development set เป็น input OCR คงที่ ไม่เลือกผลที่ดีที่สุดรายภาพ
- ดาวน์โหลดทีละโมเดล ตรวจพื้นที่ก่อนและหลัง; คงพื้นที่ว่างอย่างน้อย 8 GiB ไม่โหลดหลายโมเดลพร้อมกันบน RAM 16 GB หากชนทรัพยากรให้เลือกโมเดลเล็กที่ยังครบ matrix ก่อนรันจริง ห้ามลดเหลือ 1 โมเดลแล้วประกาศผ่าน
- ตรึง prompt, schema, seed, temperature, context/output limits และ chat template บันทึก template ของแต่ละโมเดล การบังคับ grammar ต้องเกิดตอน decode ไม่ใช่ repair JSON หลังตอบ
- schema กลางคือ `receipt_schema.json`: `transaction_date`, `merchant`, `items[{name,quantity,unit,unit_price,line_total}]`, `grand_total`, `currency`; provenance/review metadata อยู่ envelope แยก ไม่ยัดเข้า extraction JSON
- เก็บ raw response ก่อน parse ห้ามตัด markdown fence, เติม key, แก้ comma หรือ retry เงียบในคะแนน raw ถ้าแสดงระบบ repair ต้องเป็นอีกเงื่อนไขและนับเวลารวม
- ตรวจ schema validator กับ grammar converter ว่ารองรับ nullable/required/additionalProperties ตามจริง; ผ่าน grammar ไม่ได้แปลว่าค่าฟิลด์ถูก
- รายงาน parse rate, schema-valid rate, field P/R/F1, exact match ทั้งเอกสาร, missing/extra items, ความคลาดเคลื่อนเงิน และ coverage ของฟิลด์ตัวเลข ใช้ scorer/protocol เดิมเป็นฐานแล้วแก้ข้อผิดพลาดที่พบพร้อม regression
- ทบทวน empty string/null, duplicate item names, reorder, bool-as-number, NaN/Infinity, extra/missing item, invalid output และ timeout ไม่ใช้จำนวน unmatched items เป็นข้อพิสูจน์ hallucination เพราะจับคู่พลาดได้ ให้ตรวจตัวอย่างกับ input ก่อนเรียกว่า hallucination
- เวลาที่ขาด/เกิน context ให้บันทึก failure อย่างตรงไปตรงมา ถ้าต้อง chunk ให้กำหนดจาก development set และใช้กติกาเดียวกันในทุกเงื่อนไขก่อน evaluation

**เกณฑ์ผ่าน:** มีผล inference จริงครบ 16 เงื่อนไขบน evaluation IDs เดียวกัน, ทุก expected attempt มี record รวม failure, ใช้เฉลยข้อ 1 เท่านั้นในผลหลัก, ย้อนตรวจ model/prompt/input/output/schema hashes ได้ และคะแนนมาจาก raw output ไม่ใช่คำตอบที่คนแก้ ไม่มีเกณฑ์ว่าต้องชนะ baseline จึงจะถือว่าทดลองสำเร็จ

## 4. ต่อเดโมครบกระบวนการบน PC

เส้นทางจริง: ภาพ → YOLO → หมุน/crop → OCR → Local LLM → schema/semantic checks → หน้าตรวจคู่ภาพ → แก้/ยืนยัน → persist → MQTT broker → Home Assistant local

- UI ภาษาไทยเรียบง่าย แสดงภาพกับฟิลด์/รายการและส่วนที่ตรวจไม่ได้ ให้แก้จำนวน/หน่วย/ราคา เพิ่ม/ลบรายการได้ เห็นสถานะ `pending_review`, `confirmed`, `publish_failed`, `published`; ไม่ใส่รายละเอียดโมเดลเกินจำเป็นใน flow ผู้ใช้
- เก็บ raw result และ confirmed result แยก พร้อม edit log ห้ามส่งรายการที่ยังไม่ยืนยันหรือ schema ไม่ผ่าน แสดงยอดรวมไม่ตรงเป็นคำเตือน ไม่บังคับว่า grand_total ต้องเท่าผลรวมสินค้าเมื่อมี VAT/ส่วนลด
- ใช้ SQLite หรือ storage local ที่ทน restart; transaction ID + revision/event ID สำหรับ dedup/outbox การ retry MQTT ต้องไม่ทำให้ Home Assistant นับซื้อซ้ำ
- สร้าง broker และ Home Assistant สำหรับทดลองบนเครื่องนี้แยกจากระบบบ้านจริง ใช้ topic namespace `seminar/preboard/...` ไม่สั่งงานเครื่องใช้ไฟฟ้าและไม่เปิดบริการสู่สาธารณะ
- ตรวจ WSL Ubuntu และ runtime ที่มีอยู่ก่อนเลือกวิธีติดตั้ง ตามวิธีที่ Home Assistant รองรับปัจจุบัน: https://www.home-assistant.io/installation/ ไม่ดาวน์โหลด VM ขนาดใหญ่โดยไม่คำนวณพื้นที่และ RAM
- ใน Home Assistant แสดงอย่างน้อยยอดซื้อที่ยืนยันล่าสุดและจำนวนรายการ พร้อม transaction ID/version ที่ตรวจเทียบได้ ไม่เรียกยอดซื้อว่าสต็อกคงเหลือหรือ burn rate
- ต้องตรวจว่า Home Assistant ได้รับจริงด้วย state/history/API หรือภาพหน้าจอที่สัมพันธ์กับ event ID; log ฝั่ง publisher หรือ mock subscriber อย่างเดียวไม่พอ ถ้า HA ยังติดตั้งไม่ได้ให้ทำ adapter/test ต่อได้แต่ gate นี้ยังไม่ผ่าน
- มีคำสั่ง start/stop, health checks, ตัวอย่างภาพที่เลือก และ quickstart ให้เพื่อนรันได้ ตั้งบริการเบื้องหลังไม่เปิดหน้าต่างรบกวนโดยไม่จำเป็น

**เกณฑ์ผ่าน:** เดโมภาพจริงอย่างน้อย 3 ภาพจากอย่างน้อย 2 ธุรกรรม จบครบ pipeline; แสดงอย่างน้อยกรณียืนยัน/แก้ไข/ปฏิเสธหรือข้อมูลผิด; มี event trace ถึง HA, ทดสอบ broker หยุดแล้ว retry, กดยืนยันซ้ำ, restart แล้วไม่ส่งซ้ำ, invalid JSON ไม่ publish ต้องมี local LLM จริงในเส้นทางหลัก ไม่ใช้ fixture แทน

## 5. วัดความถูกต้อง เวลา และ RAM พร้อมต่างฉาก

- เก็บข้อมูลนี้ตั้งแต่ข้อ 2–4: run ID, source/split/hash, CPU/OS/runtime, threads, model/quantization, config, wall time แต่ละ stage, model load, full pipeline, process IDs, sampled peak RSS ของ process tree, sampling interval และ error status
- CPU เป็น baseline เปรียบเทียบหลัก หากใช้ GPU เพิ่มให้แยกเป็นคนละ configuration ห้ามสับสน iGPU/NPU กับผล CPU ไม่รายงานพลังงานถ้าไม่มีการวัดพลังงานจริง
- แยก cold load กับ warm inference; warm-up ที่ไม่เอาเข้าคะแนนอย่างน้อย 1 ครั้ง และวัด warm ซ้ำ 3 ครั้งต่อเอกสาร/เงื่อนไข สลับลำดับ config ด้วย seed หลีกเลี่ยงรันงานหนักอื่นพร้อม benchmark
- สำหรับ runtime ที่อยู่ WSL วัด process ภายใน WSL และระบุ metric หน่วยความจำให้ชัด ไม่เอา memory ของ Python client บน Windows แทน LLM server; RSS ที่ sample อาจพลาด peak สั้น ต้องบอกข้อจำกัด
- ระบุ automated processing latency แยกจากเวลาคนตรวจ ไม่เอาการรอผู้ใช้มารวม inference หากยังไม่มี user study ห้ามรายงานเวลาการแก้ของ AI เป็นพฤติกรรมคน
- ภาพต่างฉากเดิม 6 ภาพถูกตรวจผลและทดลองหมุนแล้ว ใช้เป็น retrospective external set ได้ แต่ห้ามเรียกว่า untouched holdout ใหม่
- ขอภาพใหม่จริงอย่างน้อย **6 ภาพจากอย่างน้อย 3 ธุรกรรมที่ไม่ซ้ำชุดเดิม** มีฉาก/แสงหรืออุปกรณ์ต่างจากเดิม พร้อมข้อมูลเงื่อนไข ตรวจกลุ่มซ้ำและทำเฉลยตามข้อ 1 ก่อนใช้ final challenge; ใช้ configuration ที่เลือกและตรึงก่อนเปิดผล challenge
- ไม่จำเป็นต้องครบ 59 ภาพในคะแนนทุก metric; ใช้เฉพาะภาพที่มีเฉลยตรงขอบเขต และรายงานจำนวนที่ใช้/ค้าง/กันออกทุกครั้ง ห้ามนับ augmentation เป็นภาพต่างฉากใหม่หรือธุรกรรมใหม่
- สรุป median/range และ p95 พร้อมจำนวนตัวอย่าง; ในชุดเล็กระบุความไม่แน่นอน ไม่ทำ ANOVA/Wilcoxon ตามเอกสารเก่าอัตโนมัติ หากทำ bootstrap ให้ resample ตามธุรกรรม ไม่ถือ 3 repetitions เป็น 3 ธุรกรรม
- ให้ผล component, oracle crop/reference input และ end-to-end แยกกัน รวม failure rate ไม่รายงานเฉพาะงานที่สำเร็จเร็ว

**เกณฑ์ผ่าน:** มี raw measurements และตาราง aggregate ที่คำนวณซ้ำได้, timing/RAM ของทุก stage และทั้ง pipeline, ผล PC-only ชัดเจน, final challenge จากภาพจริงใหม่พร้อม provenance และ failure analysis หากยังไม่ได้ภาพใหม่ให้ระบุข้อ 5 ยังรอข้อมูล ไม่ใช้ 6 ภาพเก่าปิดงานแทน

## การตรวจรับและการส่งกลับ review

สร้าง `PREBOARD_STATUS.md` อัปเดตทุก milestone โดยแต่ละข้อมีสถานะ, evidence path, counts, command ล่าสุด, ปัญหาค้าง และขั้นถัดไป สถานะที่ใช้: `TODO`, `IN_PROGRESS`, `WAITING_HUMAN`, `WAITING_DATA`, `PASS_IMPLEMENTATION` ไม่มีสถานะผ่านที่อาศัยคำอธิบายอย่างเดียว

`PREBOARD_REVIEW_PACKET.md` ต้องประกอบด้วย:

1. ตารางครบ 5 ข้อ พร้อมลิงก์ evidence และคำสั่งรันซ้ำ; แยกของใหม่จากผลก่อนเริ่มงาน
2. environment/lock files, model/source/license/hash, dataset/split/schema/prompt versions
3. audit 59 ภาพ, independent-review/adjudication evidence, รายการข้อยกเว้นและจำนวนค้าง
4. OCR และ LLM comparison พร้อม raw failure counts, สูตร/ตัวหาร, ข้อสังเกตและข้อจำกัด
5. เดโมจริงและ event trace ถึง HA, วิธีเปิด/หยุด, persistence/retry verification
6. benchmark PC และภาพต่างฉากใหม่; อธิบายสิ่งที่ยังต้องรอบอร์ด
7. tests ที่รันพร้อมผลจริง, git diff summary, commit/branch ที่ให้ review, ประเด็นที่ต้องตัดสินจาก reviewer

ก่อนส่งตรวจ ต้องเรียก scorer regression เดิม, tests ใหม่ที่ตรวจเกณฑ์สำคัญ, dataset validator, completion validator ที่เทียบ expected runs กับ actual runs และ smoke demo จริงอีกหนึ่งรอบ ไม่เขียน tests เพียงตรวจว่าไฟล์มีอยู่

เมื่อครบทุก gate ให้ commit/push branch ตามสิทธิที่ผู้ใช้อนุญาตไว้ บอกสถานะ `READY_FOR_REVIEW` และหยุดเพื่อ review ไม่ merge เข้า main และไม่แก้ค่าผลใน Ass5/Ass6 READY อัตโนมัติ หากบาง gate รอคน/ภาพให้ส่งรายการที่ต้องการอย่างเฉพาะเจาะจงระหว่างทำส่วนอื่นต่อ ห้ามอ้างว่าครบ 5 ข้อแล้ว

## ข้อความเริ่มงานสำหรับ 6.1 sol

> อ่าน PREBOARD_IMPLEMENTATION_PLAN.md และ goal ปัจจุบัน แล้ว implement ทั้ง 5 ข้อตามลำดับและเกณฑ์ตรวจรับ ทำงานอิสระต่อระหว่างรอผู้ตรวจ/ภาพใหม่ เก็บผลจริงและอัปเดต PREBOARD_STATUS.md ไม่แต่งผลหรือเปลี่ยนเกณฑ์ให้ดูเสร็จ เมื่อผ่านครบให้ทำ PREBOARD_REVIEW_PACKET.md, commit/push branch แล้วหยุดส่งกลับให้ reviewer ตรวจ ยังไม่แก้ Ass5/Ass6 READY เดิมและไม่ merge main ก่อน review
