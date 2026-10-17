# รับภาพใบเสร็จสำหรับงาน Ass 5

ภาพต้นฉบับเก็บใน `C:\Users\NATCHAPOL\SeminarLab\incoming` ซึ่งอยู่นอก OneDrive รายงานที่สร้างจะอยู่ใน `C:\Users\NATCHAPOL\SeminarLab\reports` สคริปต์ไม่แก้ไขภาพและไม่ส่งภาพไปบริการออนไลน์

1. คัดลอกรูปใบเสร็จ `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic` หรือ `.tiff` ไปที่ `incoming` จะจัดเป็นโฟลเดอร์ย่อยก็ได้ หลีกเลี่ยงรูปคนหรือข้อมูลส่วนตัวที่ไม่จำเป็น
2. เปิด PowerShell ในโฟลเดอร์ `Seminar\receipt_lab` แล้วรัน `./run_intake.ps1` หรือรัน `C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe intake.py`
3. เปิด `reports\manifest.csv` เพื่อกรอก `doc_type`, `store_or_source`, `lighting`, `condition` และหมายเหตุ สคริปต์จะเก็บข้อมูลที่กรอกไว้เมื่อรันซ้ำสำหรับไฟล์ที่มี SHA-256 เดิม

   ชุดทดลองหลักใช้ใบซื้อสินค้าที่มีรายการสินค้า/จำนวน/ราคา ให้ใส่ `doc_type=itemized_purchase`; ใบรับเงินใช้ `payment_receipt`, ใบแจ้งหนี้ค่าหอใช้ `housing_invoice`, ใบส่งของใช้ `delivery_note`, เอกสารอื่นใช้ `other` และเก็บเป็นชุดทดสอบเสริม ถ้าภาพหนึ่งมีหลายใบหรือเอกสารต่อหลายหน้า ให้บันทึกใน `notes`
4. ดูกราฟ `reports\eda.png` และสรุป `reports\summary.json` ตัวเลขเหล่านี้เป็น EDA ของภาพ ยังไม่ใช่ผล YOLO/OCR
5. ใส่ข้อความถอดจากใบเสร็จใน `ground_truth_text` และเฉลย JSON ใน `ground_truth_json` โดยใช้ `doc_id` จาก manifest เป็นชื่อไฟล์ เช่น `R123456789ABC.txt` และ `R123456789ABC.json`
6. หากต้องการติดป้ายกรอบเอกสารสำหรับ YOLO ให้รัน `C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe label_boxes.py` แล้วลากกรอบบนภาพ โปรแกรมบันทึกป้ายกำกับรูปแบบ YOLO ใน `labels` ทันที ปุ่ม Next/Previous ใช้เปลี่ยนภาพ เครื่องมือนี้รองรับหนึ่งกรอบเอกสารต่อภาพ

7. ทดลอง OCR แบบออฟไลน์ด้วย `C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe run_ocr.py --doc-id RC4859AC7A019` (รันจากโฟลเดอร์ `Seminar\receipt_lab`; ID นี้เป็นใบซื้อสินค้าตัวอย่าง) โมเดลภาษาไทย/อังกฤษอยู่ใน `SeminarLab\models\easyocr` ผลข้อความอยู่ใน `SeminarLab\ocr_outputs\easyocr_th_en` นอก OneDrive และยังไม่ใช่คะแนนความแม่นยำจนกว่าจะเทียบกับเฉลยที่ตรวจแล้ว

ชุดนำร่องใบซื้อสินค้า 20 ภาพที่ตรวจชนิดเอกสารแล้วอยู่ใน `SeminarLab\reports\pilot_itemized_20.csv` ใช้ `curate_pilot.py` เพื่อสร้างไฟล์นี้ซ้ำอย่างปลอดภัย และอ่าน `annotation_guidelines.md` ก่อนลงเฉลย 9 ภาพมีใบซื้อสองหน้าในภาพเดียว จึงต้องอ่านทั้งสองหน้าเมื่อทำเฉลย JSON

ถ้าอ่านไฟล์ HEIC ไม่ได้ ให้เปิด `summary.json` เพื่อดูข้อผิดพลาด แล้วแปลงรูปต้นทางเป็น JPEG ด้วยเครื่องมือบนเครื่องก่อนนำเข้าใหม่ รูปภาพและรายงานอาจมีข้อมูลส่วนตัว จึงไม่ควรคัดลอกกลับเข้าโฟลเดอร์ OneDrive โดยไม่ตรวจข้อมูลก่อน

การตรวจชุดประเมิน 10+6 ภาพล่าสุดใช้ `estimate_skew_projection_16.py` ประมาณมุมจัดแนวอัตโนมัติ, `measure_orientation_language_16.py` นับอักษรในผล OCR และ `write_orientation_language_followup.py` เขียนรายงานวิธีและข้อจำกัดใน `ass5_output` สัดส่วนอักษรในผล OCR ไม่ใช่สัดส่วนภาษาจริงของเอกสาร เพราะยังไม่มีข้อความถอดที่ตรวจครบทุกบรรทัด

การตรวจชุดใบซื้อสินค้าทั้ง 59 ภาพใช้ `contact_itemized_59.py` สร้างแผ่นภาพตรวจส่วนตัว, `audit_orientation_skew_59.py` ตรวจทิศตัวหนังสือและประมาณมุมย่อยสำหรับ 54 ภาพที่มีกรอบเดี่ยว, `ocr_script_proxy_59.py` ตรวจความครอบคลุมของ OCR และ `write_59_audit_report.py` เขียนรายงานรวม 59 ภาพ ภาพครอปและข้อความ OCR อยู่เฉพาะใน `SeminarLab`; รายงานสรุปไม่มีภาพหรือข้อความจากใบเสร็จ
