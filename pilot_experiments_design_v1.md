# การออกแบบ 3 Pilot Experiments ตามข้อเสนอแนะของ GeCOT

> เอกสารนี้เป็นประวัติแผน v1 งานปัจจุบันใช้ `PREBOARD_IMPLEMENTATION_PLAN.md`, `experiments/preboard/protocol.json`, `receipt_schema.json` และ `PREBOARD_STATUS.md` แทนส่วนจำนวนภาพ ชื่อโมเดล schema และ matrix ที่ล้าสมัย ผู้ใช้ยืนยันทำคนเดียว จึงตรวจสองรอบโดยคนเดียวและรายงานข้อจำกัดนี้
**สำหรับวิทยานิพนธ์:** การพัฒนาระบบประสาทส่วนกลางอัจฉริยะในที่พักอาศัยเพื่อสกัดและวิเคราะห์ข้อมูลห่วงโซ่อุปทานในครัวเรือนด้วยปัญญาประดิษฐ์ประมวลผลเฉพาะถิ่น
**อ้างอิงสถาปัตยกรรม:** IP Camera (RTSP) → VLAN-isolated Edge Server (NPU) → YOLO document detection → Local OCR (PaddleOCR/EasyOCR) → Quantized Local LLM (Ollama: Llama-3/Phi-3/Gemma ผ่าน llama.cpp) → Structured JSON → Home Assistant (MQTT) → Smart Fridge/Storage Inventory + Burn Rate prediction + Stateful validation dashboard

---

## ภาพรวมความสัมพันธ์ระหว่าง 3 Pilot กับ Pipeline

```
Stage 1-3 (Camera→YOLO→OCR)     ──► Pilot 1 วัดความแม่นยำ ณ จุดนี้
Stage 4 (Local LLM extraction)  ──► Pilot 2 วัดความแม่นยำ ณ จุดนี้
Stage 1-6 (ทั้งระบบ end-to-end) ──► Pilot 3 วัดความแม่นยำรวม ผ่าน proxy metric จาก dashboard
```

การออกแบบ 3 pilot นี้จงใจให้ครอบคลุมทุก stage ของสถาปัตยกรรมแบบไม่ overlap กัน เพื่อให้สามารถ "ชี้จุดบอด" ได้ว่าความคลาดเคลื่อนของระบบเกิดจาก stage ไหน (OCR, LLM extraction, หรือ integration/UX) — ตอบโจทย์ GeCOT ที่ประเมินสถาปัตยกรรมทั้ง 6 stage

---

## Pilot 1: OCR Accuracy บนใบเสร็จ/ฉลากอาหารภาษาไทยจริง

### 1.1 วัตถุประสงค์
วัดความแม่นยำของ Local OCR engine (PaddleOCR เทียบ EasyOCR) ในการอ่านข้อความภาษาไทยจากใบเสร็จซื้อของและฉลากอาหาร ภายใต้สภาพแวดล้อมจริงในบ้าน (แสง มุมกล้อง สภาพเอกสาร) ก่อนที่ข้อมูลจะถูกส่งต่อไปยัง LLM

### 1.2 คำถามวิจัย
- RQ1.1: PaddleOCR หรือ EasyOCR ให้ Character Error Rate (CER) ต่ำกว่ากันสำหรับข้อความไทยบนใบเสร็จ/ฉลาก?
- RQ1.2: ความแม่นยำระดับ field (ชื่อสินค้า/ราคา/วันที่) ต่างจากความแม่นยำระดับตัวอักษรอย่างมีนัยสำคัญหรือไม่ (field ไหนอ่อนไหวต่อ error มากสุด)?

### 1.3 Dataset
- **ใบเสร็จ:** เก็บจริง 60–80 ใบ จากร้านสะดวกซื้อ/ซูเปอร์มาร์เก็ต/ตลาดสด คละประเภทเครื่องพิมพ์ (thermal dot-matrix, thermal direct, inkjet) และสภาพ (ใหม่/ยับ/จางจากความร้อน)
- **ฉลากอาหาร:** 40–60 ภาพ จากบรรจุภัณฑ์จริงในบ้าน (ผัก ผลไม้ ของแห้ง เครื่องปรุง) ให้ครอบคลุมทั้งฉลากพิมพ์และฉลากสติกเกอร์เขียนมือ
- **Ground truth:** พิมพ์ transcript ด้วยมือ (double-entry โดยผู้วิจัย 2 รอบ แล้ว diff เพื่อลด human error)

### 1.4 ตัวแปรที่ควบคุม/บันทึก
- สภาพแสง (แสงธรรมชาติ/แสงหลอด LED ในบ้าน/มุมอับแสง) — ให้ครอบคลุมทั้ง 3 สภาพ
- มุมกล้อง IP Camera จริงตามสถาปัตยกรรม (ไม่ใช่ scan flatbed) เพื่อให้ผลสะท้อน production จริง
- ผลลัพธ์การ crop จาก YOLO document detection (ถ้า crop ผิด/เอียง ก็ต้องนับเป็นความคลาดเคลื่อนสะสมของ pipeline ด้วย ไม่ใช่แค่ OCR อย่างเดียว)

### 1.5 Metrics
| Metric | นิยาม |
|---|---|
| CER (Character Error Rate) | Levenshtein distance ระดับตัวอักษร / จำนวนตัวอักษร ground truth |
| WER (Word Error Rate) | เช่นเดียวกันระดับคำ (ตัด word ด้วย PyThaiNLP tokenizer) |
| Field-level Accuracy | สัดส่วน field (ชื่อสินค้า/ราคา/วันที่/รวมยอด) ที่อ่านถูก 100% เทียบ ground truth |
| Confidence Calibration | เทียบ confidence score ที่ OCR engine รายงาน กับความถูกต้องจริง (ใช้ตัดสินใจ threshold สำหรับ dashboard flag ให้ผู้ใช้ตรวจ) |

### 1.6 การวิเคราะห์
- Paired comparison (PaddleOCR vs EasyOCR) ด้วย Wilcoxon signed-rank test (ข้อมูลไม่ likely normal distribution)
- แยกวิเคราะห์ตาม subgroup (ประเภทเครื่องพิมพ์ / สภาพแสง) เพื่อหาจุดอ่อนของแต่ละ engine

### 1.7 ข้อจำกัด
- ขนาด sample เป็นระดับ pilot (ไม่ใช่ full-scale validation) เพียงพอสำหรับชี้แนวโน้มและเลือก engine ที่จะใช้ในสถาปัตยกรรมจริง ไม่ใช่เพื่อ generalize ทางสถิติเต็มรูปแบบ

---

## Pilot 2: LLM Extraction Accuracy พร้อม Grammar-Constrained Decoding (เทียบหลายโมเดล)

### 2.1 วัตถุประสงค์
วัดความแม่นยำของการสกัดข้อมูลโครงสร้าง (structured JSON) จากข้อความ OCR โดย Local LLM แบบ quantized เทียบระหว่างโมเดล และเทียบระหว่างการถอดรหัสแบบ grammar-constrained (GBNF ผ่าน llama.cpp) กับแบบ free-form

### 2.2 คำถามวิจัย
- RQ2.1: Grammar-constrained decoding ช่วยเพิ่ม JSON validity rate และ field-level accuracy เทียบกับ free-form prompting หรือไม่ และเพิ่มขึ้นเท่าไร?
- RQ2.2: ระหว่าง Llama-3(-8B), Phi-3(-mini), Gemma(-2/3) รุ่น quantized (เช่น Q4_K_M) โมเดลใดให้ extraction accuracy สูงสุดที่ latency ยอมรับได้บน edge NPU?

### 2.3 Dataset
ใช้ transcript ที่ **ถูกต้อง 100%** (ground truth จาก Pilot 1) เป็น input หลัก เพื่อแยกวัด "ความแม่นยำของ LLM extraction" ล้วนๆ โดยไม่ปนกับความคลาดเคลื่อนจาก OCR (isolate the variable) — จากนั้นรันซ้ำอีกรอบด้วย **transcript จริงที่มาจาก OCR** (มี error ปนอยู่) เพื่อดูว่า error จาก Pilot 1 ถูกขยาย (amplify) หรือถูกซ่อม (self-correct) โดย LLM แค่ไหน

Schema เป้าหมาย (ตัวอย่าง):
```json
{
  "store_name": "string",
  "date": "YYYY-MM-DD",
  "items": [
    {"name": "string", "quantity": "number", "unit_price": "number", "category": "string"}
  ],
  "total": "number"
}
```

### 2.4 Experimental Design (2×3 factorial)
| | Free-form prompting | GBNF grammar-constrained |
|---|---|---|
| Llama-3-8B (Q4_K_M) | ✓ | ✓ |
| Phi-3-mini (Q4_K_M) | ✓ | ✓ |
| Gemma-2/3 (Q4_K_M) | ✓ | ✓ |

รันแต่ละ cell ซ้ำ N=60–80 เอกสาร (ใช้ set เดียวกับ Pilot 1) × ทำ 3 ครั้งต่อเอกสารเพื่อดู variance จาก temperature/sampling

### 2.5 Metrics
| Metric | นิยาม |
|---|---|
| JSON Validity Rate | สัดส่วน output ที่ parse เป็น valid JSON ตาม schema ได้โดยไม่ error |
| Field-level Precision/Recall/F1 | เทียบ field ต่อ field กับ ground truth (โดยเฉพาะ items array ต้อง align ด้วย fuzzy matching ชื่อสินค้า) |
| Exact Match Rate | สัดส่วนเอกสารที่ extraction ตรงกับ ground truth ทั้งหมด 100% |
| Hallucination Rate | สัดส่วน item ที่ LLM สร้างขึ้นเองแต่ไม่มีอยู่ใน input จริง |
| Latency (ms/เอกสาร) | เวลาที่ใช้บน edge NPU จริงตามสถาปัตยกรรม — trade-off กับ accuracy |

### 2.6 การวิเคราะห์
- Two-way ANOVA (หรือ non-parametric เทียบเท่าถ้าข้อมูลไม่ normal) เพื่อดู main effect ของ (โมเดล) และ (decoding mode) และ interaction effect
- Pareto analysis ระหว่าง Accuracy vs Latency เพื่อเลือกโมเดล/โหมด default ของสถาปัตยกรรมจริง

### 2.7 ข้อจำกัด
- Quantization level ตรึงไว้ที่ Q4_K_M เพื่อควบคุมตัวแปร — ถ้าต้องการศึกษาผลของ quantization level เพิ่มเติม (Q4 vs Q8 vs FP16) แนะนำเป็น experiment แยกในอนาคต ไม่รวมใน pilot นี้เพื่อไม่ให้ design ซับซ้อนเกินไป

---

## Pilot 3: End-to-End Accuracy โดยใช้ User Correction Rate เป็น Proxy Metric

### 3.1 วัตถุประสงค์
วัดประสิทธิภาพความแม่นยำของระบบทั้ง pipeline (Stage 1–6) ในสภาพการใช้งานจริงในครัวเรือน โดยใช้ **อัตราการแก้ไขของผู้ใช้บน Stateful Validation Dashboard** เป็น proxy metric แทนการหา ground truth แบบ manual ทุกรายการ (ซึ่งทำไม่ได้จริงในสเกล production)

### 3.2 เหตุผลที่ใช้ Correction Rate เป็น Proxy
การหา ground truth เต็มรูปแบบสำหรับทุกใบเสร็จที่ระบบประมวลผลทุกวันเป็นไปไม่ได้ในทางปฏิบัติ — Correction Rate จึงเป็นตัวแทนที่วัด "ต้นทุนที่ผู้ใช้ต้องแบกรับจากความผิดพลาดของระบบ" ได้ตรงกับเป้าหมายการใช้งานจริงมากกว่า accuracy metric เชิงวิชาการ (ธรรมชาติของ dashboard คือผู้ใช้ต้องกด confirm/edit/delete อยู่แล้วเป็นส่วนหนึ่งของ workflow ปกติ ทำให้ log การแก้ไขเก็บได้โดยไม่ต้องเพิ่ม overhead พิเศษ)

### 3.3 การตั้งค่าการทดลอง
- ติดตั้งระบบเต็ม pipeline ในครัวเรือนทดสอบ (อย่างน้อย 1 ครัวเรือน สำหรับ pilot — ถ้าทำได้มากกว่า 1 จะเพิ่มความหลากหลายของพฤติกรรมผู้ใช้)
- ระยะเวลาเก็บข้อมูล: **2–4 สัปดาห์** ต่อเนื่อง เพื่อให้ครอบคลุมรอบการซื้อของปกติ (รายวัน/รายสัปดาห์)
- Log ทุก transaction ที่เข้าสู่ dashboard พร้อม action ของผู้ใช้ (Confirm / Edit-field / Delete-item / Add-missing-item)

### 3.4 Metrics
| Metric | นิยาม |
|---|---|
| Overall Correction Rate | (# รายการที่ถูก Edit หรือ Delete) / (# รายการที่ระบบสกัดออกมาทั้งหมด) |
| Correction Rate by Error Type | แยกตาม field ที่ถูกแก้ (ชื่อสินค้า/ราคา/หมวดหมู่/จำนวน) เพื่อสืบต่อว่า error มาจาก stage ไหน (เทียบผลกับ Pilot 1/2) |
| Miss Rate (Add-missing-item) | สัดส่วนรายการที่ผู้ใช้ต้อง "เพิ่มเอง" เพราะระบบตรวจไม่พบเลย (พลาดทั้งใบเสร็จ/ทั้งรายการ) |
| Time-to-Confirm | เวลาเฉลี่ยที่ผู้ใช้ใช้ตรวจสอบ 1 transaction บน dashboard (สะท้อน UX burden ไม่ใช่แค่ accuracy) |
| Correction Rate Trend over Time | แนวโน้มรายสัปดาห์ (ดูว่าผู้ใช้ปรับพฤติกรรมการวางเอกสาร/ระบบเรียนรู้ pattern ครัวเรือนได้หรือไม่) |

### 3.5 การวิเคราะห์
- สรุปเชิงพรรณนา (descriptive statistics) ของ correction rate โดยรวมและแยกตาม error type
- เทียบ correction rate ตรงนี้กับผลจาก Pilot 1 (OCR) และ Pilot 2 (LLM) เพื่อ "สอบทาน" ว่า proxy metric สะท้อนผลสอดคล้องกับ component-level accuracy ที่วัดแยกไว้หรือไม่ (construct validity ของ proxy metric)
- วิเคราะห์ trend รายสัปดาห์แบบ time-series เชิงพรรณนา (ไม่จำเป็นต้องใช้ inferential stat เนื่องจากเป็น pilot ระยะสั้น)

### 3.6 ข้อจำกัดและประเด็นจริยธรรม
- ต้องขอความยินยอม (informed consent) จากผู้พักอาศัยในครัวเรือนทดสอบ เนื่องจากมีกล้อง IP Camera ติดตั้งในบ้านจริง และมีข้อมูลการซื้อของ/พฤติกรรมการบริโภคที่ sensitive — ควรผ่านการพิจารณาจริยธรรมการวิจัยในมนุษย์ (IRB/EC) ของมหาวิทยาลัยก่อนเริ่มเก็บข้อมูลจริง
- ผลจาก 1 ครัวเรือนไม่สามารถ generalize ได้ — เหมาะสำหรับ pilot เพื่อพิสูจน์ความเป็นไปได้ (proof of concept) ของ proxy metric เท่านั้น

---

## ตารางสรุปเชื่อมโยง 3 Pilot กับ GeCOT Layer

| Pilot | Stage ที่วัด | ตอบโจทย์ GeCOT ข้อไหน |
|---|---|---|
| 1. OCR Accuracy | Stage 1–3 (Camera→YOLO→OCR) | ความเสี่ยงของ error สะสมตั้งแต่ input stage |
| 2. LLM Extraction | Stage 4 (Local LLM) | ผลของ quantization + grammar constraint ต่อความน่าเชื่อถือของ structured output |
| 3. End-to-End (Correction Rate) | Stage 1–6 (ทั้งระบบ) | ความน่าเชื่อถือของระบบในสภาพใช้งานจริง ผ่าน practical proxy metric ที่ scale ได้ |

## ลำดับการทำที่แนะนำ
1. **Pilot 1 ก่อน** (ใช้เวลาสั้นสุด เก็บข้อมูล static ไม่ต้องรอ real-time) — ผลจาก Pilot 1 (ground truth transcript) จำเป็นสำหรับ Pilot 2
2. **Pilot 2 ต่อ** (ใช้ dataset จาก Pilot 1 ได้ทันที ไม่ต้องเก็บข้อมูลใหม่)
3. **Pilot 3 ทำคู่ขนานหรือหลังสุด** (ใช้เวลานานสุด 2–4 สัปดาห์ ควรเริ่มติดตั้งระบบ+ขอ consent ตั้งแต่เนิ่นๆ ให้ทันคู่ขนานกับ Pilot 1-2)
