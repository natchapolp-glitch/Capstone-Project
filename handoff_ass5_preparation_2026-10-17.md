# Handoff หลังเตรียมหลักฐาน Assignment 5 (17 ตุลาคม 2569)

## อ่านอะไรเป็นฐาน

1. Assignment 4 ฉบับที่ผู้ใช้ยืนยันว่าถูกต้องคือ `Assignment4_รายงานทางวิชาการ _แก้ไข(2) (2).pdf` **32 หน้า** ใช้เป็นฐานแนวคิด/วรรณกรรมสำหรับ Ass5 และ Ass6
2. handoff หลักเดิมให้ยึด `handoff_thesis_unified_v10.md` ไม่ใช้ไฟล์ `(1)` ที่เก่ากว่า; ไฟล์นี้เป็น handoff **เพิ่มเติม** ของงานทดลอง Ass5 ล่าสุด
3. คำแนะนำ Ass5 อยู่ใน `ass 5ก่อนได้รับfeedback/คำแนะนำต่อ.docx`: เพิ่มภาพรวม e-Senses (e-Eye, e-Nose, e-Skin) แล้วเจาะ e-Eye และนำ EDA/ผลทดลองเบื้องต้นมาแสดง
4. อีเมลอาจารย์ล่าสุดให้ทำ hardware virtualization ก่อนบอร์ดจริง ผู้ใช้ตัดงานยื่นยืมบอร์ดจากรอบเวลาเร่งนี้ ไม่ได้ซื้อ/ทดสอบ RK3588 จริง ห้ามใช้ค่าที่สมมติเป็นผล NPU
5. ข้อมูลและโครงสไลด์ Ass5 ที่อัปเดตที่สุดอยู่ใน `ass5_ready_evidence.md` กราฟรวมที่ลงสไลด์ได้คือ `ass5_assets/eda_itemized_59.png` PPTX เก่าใน `ass 5ก่อนได้รับfeedback/assignment5 (1).pptx` ยังเป็นรุ่นก่อนคำแนะนำและก่อนผลทดลอง ห้ามนำไปส่งโดยไม่แก้

## สถานะข้อมูลล่าสุด

ข้อมูลภาพส่วนตัวทั้งหมดอยู่ที่ `C:\Users\NATCHAPOL\SeminarLab` **นอก OneDrive** ไม่คัดลอกภาพใบเสร็จ, contact sheet, OCR ดิบ, annotation รายภาพขึ้น workspace ที่ sync บน OneDrive เพราะอาจมีข้อมูลส่วนบุคคล

ผู้ใช้เพิ่มภาพใหม่ 10 ภาพ (`IMG_20261017_*.jpg`) ระหว่างงานนี้ รับภาพรวม **124 ไฟล์**, SHA-256 ไม่ซ้ำ **113 ภาพ**, ซ้ำตรงกัน 11, PIL อ่านไม่ได้ 0. ชนิดเอกสารใน **113 ภาพไม่ซ้ำ**: ใบซื้อสินค้ามีรายการ 59, ใบรับเงิน/หลักฐานชำระ 28, invoice ค่าหอ 14, อื่น 8, ใบส่งของ 2, ใบซื้อสินค้าไม่ครบหน้า 1, รอตรวจละเอียด 1. ตัวเลขตรวจด้วย `receipt_lab/summarize_current.py`; ผลส่วนตัว `SeminarLab/reports/classification_summary_113.json` และ manifest ที่ `SeminarLab/reports/manifest.csv`. **59 คือภาพผู้สมัคร ไม่ใช่ 59 ธุรกรรมอิสระ.** อาจมีหลายเอกสารในภาพเดียวหรือธุรกรรมซ้ำ

10 ภาพใหม่ตรวจภาพเต็มแล้ว พบ **6 ภาพเป็นใบซื้อสินค้าที่มีสินค้า/ราคา** และกันเป็น external scene holdout ทั้งหมด อีก 4 ภาพเป็นหลักฐานแต้ม/ธุรกรรมธนาคาร/ชำระเงิน ไม่เข้าชุดหลัก ความเข้าใจเบื้องต้นจากภาพย่อที่เคยจัดทั้ง 10 เป็นใบซื้อสินค้าถูกแก้ใน manifest แล้ว ชุดใหม่มีพื้นและแสงต่างจากชุดฝึกเดิม จึงใช้ทดสอบ generalization โดยไม่มีภาพใดเข้า train

คำสั่งที่รันผ่านบน Windows PowerShell (ใช้ venv ส่วนตัว):

```powershell
$env:PYTHONIOENCODING='utf-8'
& C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe receipt_lab\intake.py
& C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe receipt_lab\summarize_current.py
& C:\Users\NATCHAPOL\SeminarLab\.venv\Scripts\python.exe receipt_lab\eda_itemized_current.py
```

`intake.py` มีการแก้ bug แล้ว: หากไฟล์ซ้ำมีช่อง annotation ว่าง จะเลือกแถวที่กรอกมากกว่ามาคงไว้ตาม SHA-256; รอบแรกหลังเพิ่มภาพเคยทำชนิดเอกสาร 11 ภาพหายชั่วคราว และกู้คืนด้วย `receipt_lab/restore_review_labels.py` จากรายการคัดภาพเดิม จากนั้นรัน intake ซ้ำและตรวจจำนวน unique จนครบ ไม่มีภาพต้นฉบับถูกแก้ `classification_summary_103.json` และ EDA 53 เป็น snapshot เก่า

## EDA และผลทดลองที่อ้างได้

EDA ของภาพผู้สมัครใบซื้อสินค้า 59: พิมพ์ 41, เขียนมือ 18; แนวตั้ง 38, แนวนอน 21; brightness median 173.9/255 ช่วง 109.7–185.9; contrast median 63.6/255; ความละเอียด 1.55–1.64 MP. สถิติ brightness/contrast เป็น **ทั้งภาพรวมพื้นหลัง** ไม่ใช่ ROI บนใบเสร็จ ยังไม่วัด perspective skew หรือสัดส่วนตัวอักษรไทย/อังกฤษ ผล `SeminarLab/reports/eda_itemized_59.json` และกราฟที่ไม่มีข้อมูลในภาพใบเสร็จ `ass5_assets/eda_itemized_59.png`

YOLOv8n detection ของ `receipt_region` (หนึ่งบริเวณต่อภาพ) ใช้ภาพเก่า 48 จาก 53 ผู้สมัคร โดยกัน 5 ภาพที่มีหลายเอกสารหรือสงสัย near-duplicate ออกก่อน แบ่ง train 38 / validation ฉากเดิม 10; CPU Windows, imgsz320, Ultralytics 8.4.178, PyTorch 2.14.1+cpu, ขอ 15 epochs และหยุดเร็วที่ 8. Validation: mAP@0.5 **0.9276316**, mAP@0.5:0.95 **0.6868047**, precision **0.8831**, recall **0.7583**. ที่ conf .25 มีกรอบอย่างน้อยหนึ่งกรอบ IoU≥.5 ครบ 10/10 แต่หลายภาพมี 4–8 detections ต้องแก้ false positives. Median end-to-end predict call บน PC CPU 28.45 ms/ภาพ จาก 30 warm repetitions รวมอ่านไฟล์/pre/postprocess. ผลส่วนตัว `SeminarLab/yolo_expanded/expanded_metrics.json` และ `prediction_review.json`; weights `SeminarLab/yolo_expanded/runs/receipt_region_v8n/weights/best.pt`; ONNX `best.onnx`. Label ยังเป็น assistant visual review และฉากเดิมคล้ายกันมาก จึงเป็น feasibility pilot

**ผลสำคัญที่สุดสำหรับ Ass5:** โมเดลเดิมที่ freeze แล้วทดสอบกับใบซื้อสินค้าใหม่ต่างฉาก 6 ภาพ (ไม่ฝึกเพิ่ม) ได้ mAP@0.5 **0.2370833**, mAP@0.5:0.95 **0.1596578**, precision **0.2572**, recall **0.6667**. ที่ conf .25 กรอบ confidence สูงสุด IoU≥.5 เพียง **1/6** ภาพ, หากเลือกกรอบที่ IoU ดีที่สุดจากทุก detection จะได้ 5/6 แต่การเลือกเช่นนั้นต้องรู้เฉลย จึงไม่ใช่ความสำเร็จในระบบจริง โมเดลชอบทำนายกรอบทั้งภาพ/บางส่วนเมื่อพื้นหลังเปลี่ยน ผลส่วนตัว `SeminarLab/external_scene_6/external_results.json`, `label_review_private.png`, `prediction_review_private.png`. Ultralytics แจ้งว่า JPEG ทั้ง 6 ใน **สำเนาชุดทดสอบ** มีการซ่อมรูปแบบไฟล์อัตโนมัติ; ต้นฉบับใน `incoming` ไม่ถูกแก้ ผลนี้ n=6 และ label โดยผู้ช่วย ต้องให้ผู้วิจัยตรวจซ้ำก่อนอ้างผลวิจัยฉบับสุดท้าย แต่เหมาะเป็นผลนำร่องที่ซื่อสัตย์ใน Ass5

EasyOCR ไทย+อังกฤษบน 3 ภาพพิมพ์ CPU พบ 92/77/64 text regions ใช้เวลาราว 87.6/91.6/85.4 วินาทีต่อภาพหลังโหลดโมเดล ค่าความมั่นใจมัธยฐาน .326/.459/.089 ตามลำดับ Spot-check ตัวเลขวัน/ยอดรวมที่คนจับคู่เองถูกตรง 4/6 ช่อง (2/3 วัน, 2/3 ยอด) **ไม่ใช่ automatic field accuracy, ไม่ใช่ CER, และ ground truth ยังไม่ผ่าน second check** ผลส่วนตัว `SeminarLab/reports/ocr_field_spotcheck_3.json` และ OCR ดิบใน `SeminarLab/ocr_outputs/easyocr_th_en`

JSON schema มีร่างเฉลยหนึ่งใบที่ `SeminarLab/annotation_drafts/RC4859AC7A019.json` สถานะ `draft_needs_second_check`; `ground_truth_json` ยังไม่มีเฉลยตรวจซ้ำที่ใช้ให้คะแนนได้ ยังไม่ได้ทดลอง LLM/grammar/quantization หรือ MQTT/Home Assistant

## RKNN PC-side virtualization สำเร็จหนึ่งโมเดล

WSL Ubuntu 26.04 ใช้ managed Python 3.12.15 ใน `/home/natchapol/SeminarLab/rknn/.venv`, RKNN Toolkit2 **2.5.0** wheel ทางการจาก [airockchip/rknn-toolkit2](https://github.com/airockchip/rknn-toolkit2/blob/master/README.md), torch 2.4.0+cpu, ONNX Runtime 1.26.0. สคริปต์ `receipt_lab/rknn_pc_validate.py` ถูกคัดลอกไป `C:\Users\NATCHAPOL\SeminarLab\rknn_pc_validate.py` ก่อนรันด้วย WSL

รอบแรก RKNN build ล้มที่กฎ fuse `seperate_conv_rs_split` (`IndexError: list index out of range`); คำเตือน SDK แนะนำให้ปิดกฎนี้ จึงตั้ง `disable_rules=['seperate_conv_rs_split']` แล้ว build สำเร็จ **แบบไม่ quantize** เป้าหมาย `rk3588`. ทำ `ONNX load → RKNN build → export → init_runtime() บน PC → inference ภาพจริงหนึ่งภาพ` ครบ ผล output `(1,5,2100)` finite; เทียบ raw output กับ ONNX mean absolute difference 0.048006 และ max 1.341362 (หน่วยผสมตาม raw output; ยังไม่ใช่ detection accuracy comparison). สถานะ `success` ที่ WSL `~/SeminarLab/rknn/pc_sdk_validation.json`, ไฟล์โมเดลล่าสุด `~/SeminarLab/rknn/receipt_region_v8n_float_rk3588.rknn`, log ที่ Windows `SeminarLab/reports/rknn_pc_run_log.txt` ในรายงานให้พูดอย่างแม่นยำว่า **float build, do_quantization=False** จนกว่าจะตรวจ dtype ภายในอีกครั้ง

นี่คือ **PC-side SDK simulation/validation**, ไม่มีการวัด latency, FPS, RAM, พลังงาน หรือ accuracy บน NPU จริง อย่าเรียกผล CPU หรือ PC simulator ว่า NPU benchmark

## สิ่งที่ควรทำต่อหลัง handoff

1. สร้าง/แก้ Ass5 PPTX จากโครง 10 สไลด์ใน `ass5_ready_evidence.md` ให้แสดง e-Senses ก่อนเจาะ e-Eye และเปรียบเทียบผลฉากเดิมกับต่างฉาก ใช้กราฟ aggregate ที่ปลอดข้อมูลส่วนตัว ห้ามเอา contact sheet/ใบเสร็จดิบขึ้นสไลด์โดยไม่ปกปิดข้อมูลและตรวจสิทธิ
2. ให้ผู้วิจัยตรวจชนิดเอกสาร 113 ภาพและ label 54 ภาพที่ใช้วัด YOLO ซ้ำ โดยเฉพาะ 6 ภาพต่างฉาก; จับกลุ่มธุรกรรมซ้ำ/เอกสารคู่เพื่อ split ที่แน่นขึ้น
3. ทำเฉลยข้อความและ JSON ที่คนตรวจสองรอบอย่างน้อยชุดเล็กก่อนคำนวณ CER, field accuracy หรือ LLM JSON validity; อย่าใส่ตัวเลขผลเหล่านี้ก่อนมีเฉลย
4. หากเวลาพอ เพิ่มภาพต่างพื้น/แสง/มุมเข้า **train ชุดใหม่** และกันชุดทดสอบต่างฉากอีกชุดที่ไม่ถูกใช้ปรับโมเดล เพื่อดูว่าปัญหา generalization ดีขึ้นจริงหรือไม่; อย่าใช้ 6 ภาพเดิมเป็น final test หลังนำไปฝึก
5. Ass6 เป็นเค้าโครงต่อยอด Ass4 32 หน้าและวิธีทดลองนี้ โดยแยกผลนำร่อง PC จากงาน NPU จริงในอนาคต; รอบนี้ไม่ทันกระบวนการยืมบอร์ดตามผู้ใช้

## การสื่อสารกับผู้ใช้

ผู้ใช้เคยถามว่าทำไมใช้เพียง 20 ภาพจาก 100+ ภาพ คำตอบล่าสุดคือคัดทั้งหมดแล้ว: 124 ไฟล์, 113 ไม่ซ้ำ, 59 ภาพผู้สมัครหลัก; YOLO ใช้ภาพเก่า 48 (38/10) และภาพใหม่ต่างฉาก 6 เป็น holdout, อีก 5 กันออกด้วยเหตุผลหลายเอกสาร/near-duplicate รวมใช้งานเชิงทดลอง 54 จาก 59 ผู้สมัคร สิ่งที่ยังไม่พร้อมคือเฉลยมนุษย์สำหรับ OCR/LLM ไม่ใช่จำนวนภาพไม่พอ

หากเริ่ม turn ใหม่ ให้อ่าน `ass5_ready_evidence.md` และ handoff นี้ก่อน แล้วตรวจ `SeminarLab/reports/classification_summary_113.json`, `SeminarLab/yolo_expanded/expanded_metrics.json`, `SeminarLab/external_scene_6/external_results.json`, และ WSL `~/SeminarLab/rknn/pc_sdk_validation.json` เพื่อใช้เลขจากหลักฐานล่าสุด
