# วิธีเปิดเดโมและตรวจเฉลยด้วยคนเดียว

รัน PowerShell จากโฟลเดอร์ Seminar ใช้ Python เดิมใน `C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe`

เวอร์ชัน dependency ที่ติดตั้งจริงบันทึกใน `experiments/preboard/requirements-pc-lock.txt` และ `requirements-ha-lock.txt`; runtime ฝั่ง WSL อยู่ใน `reports/preboard/environment_wsl.json` สำหรับเครื่องเพื่อนต้องเปลี่ยน path ตามชื่อผู้ใช้และจัดพื้นที่ `SeminarLab` พร้อมภาพ/โมเดลภายนอก repo ก่อน คำสั่งนี้อ้าง environment ที่เตรียมแล้วบนเครื่องเจ้าของงาน ยังไม่ใช่ตัวติดตั้งอัตโนมัติสำหรับทุกเครื่อง

```powershell
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.services start
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.services configure
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.demo_pc.server
```

เปิดหน้าตรวจเฉลยที่ http://127.0.0.1:8090/review หรือเดโมที่ http://127.0.0.1:8090/demo โดยให้หน้าต่าง PowerShell ของ server ทำงานอยู่ ถ้าเปิดไว้แล้วไม่ต้องรัน server ซ้ำ

## เดโมสำหรับตรวจผลโมเดล

1. เลือกภาพและทิศที่อ่านตรง แล้วกด **อ่านภาพด้วยระบบ** รอให้จบ ชื่อร้าน/สินค้า/ตัวเลขที่เห็นเป็นผลโมเดล ยังอาจผิด
2. เปรียบเทียบกับภาพ แก้ข้อมูล เพิ่ม/ลบรายการ แล้วใส่ชื่อผู้ตรวจ
3. กด **ยืนยันและส่งข้อมูล** จะบันทึกการแก้ไขและส่งรายการที่ยืนยันแล้วผ่าน MQTT ถ้า broker ไม่พร้อม รายการจะค้างส่งและกดส่งใหม่ได้
4. การเลือกในช่อง **รายการที่บันทึกไว้** จะเปิดงานที่ประมวลผลแล้วกลับมาตรวจได้ การกดยืนยันซ้ำข้อมูลเดิมใช้ event เดิม ไม่เพิ่มการซื้อซ้ำ

## เฉลยสำหรับวัดความถูกต้อง

ผู้ใช้ยืนยันว่าทำคนเดียว ใช้นายณัชพล เพ็งพลตรวจสองรอบ แล้วรายงานข้อจำกัดนี้ตามจริง

1. เปิด http://127.0.0.1:8090/review เลือกภาพและรอบแรก ถอดข้อความในภาพสำหรับตรวจให้ตรงทุกบรรทัด พร้อมฟิลด์และรายการสินค้า ช่องไหนมีข้อความแต่อ่านไม่ได้ให้ระบุในช่องตำแหน่งที่อ่านไม่ได้
2. ใส่ชื่อ ติ๊กยืนยันว่าอ่านจากภาพด้วยตนเอง แล้วกด **บันทึกเฉลยรอบนี้** รอข้อความว่าบันทึกสำเร็จก่อนกด **ภาพถัดไป** ต้องบันทึกทีละภาพ ปุ่มนี้บันทึกเฉพาะภาพและรอบที่เปิดอยู่ ไม่ส่งข้อมูลซื้อเข้า Home Assistant
3. เว้นช่วงแล้วเริ่มรอบสองจากช่องว่าง โดยอ่านภาพเองไม่เปิดคำตอบรอบแรก ใช้ชื่อเดิมได้ ระบบเก็บเป็นคนเดียวตรวจสองรอบ หากเคยเปิดผลโมเดลอยู่ให้เลือกภาพใหม่ก่อน
4. เปิด http://127.0.0.1:8090/adjudicate เพื่อเทียบสองรอบ ตรวจส่วนต่างกับภาพ แก้เฉลยสุดท้าย ใส่กรอบและรหัสกลุ่มธุรกรรม เลือก development/evaluation ตามการแบ่งชุดที่ตกลงก่อนดูคะแนน แล้วบันทึก
5. เริ่มจากหกภาพต้นรายการ: `R3B0A1D27A6DC`, `R74946CAAC57E`, `R4F4EA934251E`, `RC4859AC7A019`, `R295ACA1B69DF`, `RCDB7A40C2061` ภาพที่อ่านไม่ครบเก็บสถานะค้าง ไม่ต้องเดาหรือบังคับให้ผ่าน ต้องหาภาพที่อ่านครบมาทดแทนจนมีอย่างน้อย 6 ธุรกรรม

ภาพสำหรับตรวจเป็น crop อ้างอิงที่หมุนตามการตรวจเดิม ต้องใช้ขอบเขตเดียวกันทั้ง transcript และ OCR ถ้ากรอบตัดข้อมูลหรือภาพหลายใบต้องแก้ region ก่อนให้คะแนน ข้อมูลไม่ปรากฏจริงใช้ null; ข้อมูลอ่านไม่ได้ให้ระบุความไม่ครบ ไม่ใช้ null ปิดบัง

ช่อง **รวมบรรทัด** คือยอดของสินค้ารายการนั้นตามที่พิมพ์ เช่น กาแฟ 2 ชิ้น ราคาชิ้นละ 20 บาท รวมบรรทัด 40 บาท หากพิมพ์เฉพาะยอดท้ายรายการ ให้กรอกยอดนั้นและเว้นราคาต่อหน่วยที่ไม่ได้แสดง การบันทึกซ้ำข้อมูลเดิมไม่เพิ่ม entry; หากแก้ข้อมูลจะสร้าง revision ใหม่โดยเก็บต้นฉบับไว้

การระบุชื่อผู้ตรวจหรือการติ๊กในข้อมูลทดสอบอัตโนมัติไม่ใช่หลักฐานว่าคนตรวจจริง ผลรันที่ assistant สร้างอยู่ในสถานะ engineering/draft

## ภาพต่างฉากใหม่

นำภาพจริงใหม่อย่างน้อย 6 ภาพ จากอย่างน้อย 3 ธุรกรรมที่ไม่ซ้ำชุดเดิม ใส่ใน `C:\Users\NATCHAPOL\SeminarLab\preboard\new_scene_inbox` ถ่ายให้เห็นเอกสารครบและตัวอักษรชัด เก็บร้าน/วันที่/อุปกรณ์/แสง/ฉากในบันทึกกำกับ การถ่ายซ้ำธุรกรรมเดียวให้นับอยู่กลุ่มเดียวกัน การหมุนหรือปรับแสงภาพเก่าไม่ใช่ภาพใหม่

```powershell
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.intake_challenge 'C:\Users\NATCHAPOL\SeminarLab\preboard\new_scene_inbox'
```

ภาพนี้เป็น candidate ก่อน ต้องตรวจชนิด กรอบ ธุรกรรมซ้ำ และเฉลย แล้วใช้ configuration ที่ตรึงจาก development set ก่อนเปิดผล challenge เดิม 6 ภาพต่างฉากถูกทดลองแล้ว จึงยังใช้แทน final challenge ใหม่ไม่ได้

ตัวรับภาพเก็บต้นฉบับไว้ แล้วสร้าง PNG ที่จัด EXIF orientation ให้ตรงกันทั้งเบราว์เซอร์กับ OCR ก่อนกำหนดพิกัดกรอบ ผู้เตรียมต้องใช้ `python -m receipt_lab.preboard.regions --help` ตั้งกรอบและทิศก่อนเริ่มกรอกสองรอบ พร้อม `capture_conditions` ได้แก่ device, lighting, background, capture_source จากข้อมูลการถ่ายจริง กรอบที่กำหนดนี้ยังเป็นร่างจนผู้ใช้ตรวจ ภาพซับซ้อนหลายเอกสารยังกันออกจาก protocol แบบ region เดียว

การเปลี่ยนกรอบหลังเริ่มกรอกจะถูกปฏิเสธเพื่อไม่ให้ข้อความเฉลยอ้างภาพคนละส่วน หน้าตกลงเฉลยแสดงภาพเดียวกับที่ใช้ตรวจ และให้ยืนยันเงื่อนไขภาพใหม่อีกครั้ง หากต้องเปลี่ยนกรอบต้องเก็บประวัติเดิมแล้วเริ่มการตรวจภาพนั้นใหม่

## คำสั่งสำหรับทดลองและตรวจรับ

```powershell
# ตรวจโครงข้อมูลและการตรวจเฉลย
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.dataset validate
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.verify

# ใช้หลังมีเฉลยจริงและ split พร้อมแล้ว
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.benchmark_ocr --split development --run-id ocr-development-v1
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.selection ocr --run 'C:\Users\NATCHAPOL\SeminarLab\preboard\runs\ocr-development-v1'
$preboardOcr = (Get-Content 'C:\Users\NATCHAPOL\SeminarLab\preboard\ocr_selection.json' -Raw | ConvertFrom-Json).engine
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.experiment --split development --engine $preboardOcr --ocr-run 'C:\Users\NATCHAPOL\SeminarLab\preboard\runs\ocr-development-v1' --run-id llm-development-v1
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.selection freeze --run 'C:\Users\NATCHAPOL\SeminarLab\preboard\runs\llm-development-v1'

# ประเมินด้วยข้อมูลอีกชุดหลังตรึงวิธีแล้ว
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.benchmark_ocr --split evaluation --run-id ocr-evaluation-v1
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.experiment --split evaluation --engine $preboardOcr --ocr-run 'C:\Users\NATCHAPOL\SeminarLab\preboard\runs\ocr-evaluation-v1' --run-id llm-evaluation-v1
$preboardModel = (Get-Content 'C:\Users\NATCHAPOL\SeminarLab\preboard\selection.json' -Raw | ConvertFrom-Json).model_id
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.evaluate_ocr_fields --split evaluation --model $preboardModel --ocr-run 'C:\Users\NATCHAPOL\SeminarLab\preboard\runs\ocr-evaluation-v1'

# ตรวจการส่งจริงและเงื่อนไขครบห้าข้อ
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.verify_delivery
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.gates

# หยุดเฉพาะบริการทดลองที่สร้างไว้
& 'C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe' -m receipt_lab.preboard.services stop
```

คำสั่งด้านบนเลือก OCR จาก development แล้วตรึงโมเดลก่อน evaluation ไฟล์ `selection.json` เก็บ criterion และ hash หลักฐาน ห้ามเลือกใหม่จากผล evaluation/challenge การให้คะแนน LLM/ฟิลด์ต้องระบุ `--ocr-run` ซึ่งชี้ผล benchmark ที่ครบและตรงกับเฉลยรุ่นนั้น ไม่อ่านจาก cache ที่อาจถูกเขียนทับ

วัดฟิลด์จาก OCR สองตัวผ่านโมเดลที่ตรึงเดียวกัน โดยเปิด grammar เหมือนกันทั้งสอง engine ค่าเริ่มต้นเทียบทั้ง reference/predicted crop อุ่นเครื่องหนึ่งรอบที่ไม่นับคะแนน แล้วรันสามรอบต่อเงื่อนไข ใช้ repetition 0 ให้คะแนน ฟังก์ชันนี้วัด OCR ร่วมกับ extractor คงที่ ส่วนเวลาที่บันทึกเป็นเวลาของ extractor; เวลา OCR อยู่ใน benchmark แยกต่างหาก ใช้ `--run-id` เดิมเพื่อรันต่อโดยไม่ทับ failure ได้

เมื่อเฉลยภาพต่างฉากใหม่พร้อม ใช้ `python -m receipt_lab.preboard.challenge_pipeline` เพื่อวัด pipeline ที่ตรึงไว้บน PC ก่อนคนแก้คำตอบ ส่วนการยืนยันเข้า Home Assistant ยังคงต้องกดจากหน้าตรวจ

OCR และ LLM benchmark ใช้ run ID เดิมเพื่อรันต่อหลังหยุดได้ โดยเก็บ trial ที่ล้มเหลวไว้ด้วย หากแก้ข้อมูล/config/code ต้องใช้ run ID ใหม่ ส่วน final challenge โหลดโมเดลครั้งเดียว เก็บเวลาโหลดแยก อุ่นเครื่องหนึ่งรอบ แล้ววัดขณะโมเดลอยู่ใน RAM สามรอบต่อภาพ เดโมทั่วไปที่เริ่มโมเดลใหม่ทุกคำขอจะไม่ถูกเรียกว่า warm inference

หลังแต่ละ scored run เสร็จ ให้เรียก `python -m receipt_lab.preboard.aggregate --run <โฟลเดอร์ผลรัน> --publish` ตัวสรุปจะตรวจเฉลยรุ่นเดิมและ expected attempts แล้วสร้าง `aggregate.json`/`aggregate.csv` พร้อมตาราง Markdown ใน `reports/preboard/scored` ใช้คะแนนจาก repetition 0 เท่านั้น ส่วนรอบซ้ำใช้สรุปเวลา/RAM พร้อมจำนวนที่วัดไม่ได้ เก็บ cold load แยก และไม่รวม RSS ฝั่ง Windows กับ Linux เข้าด้วยกัน เกณฑ์รับงานจะยังไม่ผ่านหากไม่มีตารางที่อ้าง raw evidence รุ่นปัจจุบัน ผล engineering 24 ครั้งไม่สามารถใช้คำสั่งนี้เพื่อสร้างคะแนนความถูกต้องได้

ไฟล์ `selection.json` ต้องมี engine, เวลา frozen_at และ hash หลักฐาน development โค้ดไม่เลือกผู้ชนะให้จากภาพ evaluation โดยอัตโนมัติ

Home Assistant ใช้ Core development instance แยกใน WSL สำหรับทดลองทางวิศวกรรม ไม่ใช่การติดตั้ง production ที่แนะนำให้ผู้ใช้ทั่วไป รายละเอียด runtime/model และผลจริงแบบไม่เผยข้อความใบเสร็จอยู่ใน `reports/preboard/` ส่วน raw output และข้อมูลเข้าสู่ระบบอยู่เฉพาะ `SeminarLab/preboard` ห้ามอัปโหลด token หรือรหัสผ่าน
