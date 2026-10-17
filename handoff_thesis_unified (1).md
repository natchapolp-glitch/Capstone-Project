# Handoff Note — สถานะงานวิทยานิพนธ์ (รวมทุกสาย รวมแชทคู่ขนาน)

**นักศึกษา:** ______ รหัส 673380267-4 กลุ่ม 15 | **รวมข้อมูลล่าสุด:** 5 สิงหาคม 2026 (อัปเดตรอบนี้: ตัดสินใจ P5 + reframe gap + verify DOI ครบ P6-P12)

⚠️ **หมายเหตุสำคัญ:** โน้ตนี้รวมข้อมูลจาก 2 แชท — แชทนี้ (เน้นแก้ไฟล์ Ass3/citation + verify DOI ทั้งชุด) และแชทคู่ขนาน "round 7" (เน้น Scopus check เต็มรูปแบบ + Pilot experiments) เพื่อไม่ให้ข้อมูลตกหล่นอีก

---

## 1. หัวข้อวิทยานิพนธ์ (ยืนยันแล้ว — ใช้หัวข้อเดิม)

**ไทย:** การพัฒนาระบบประสาทส่วนกลางอัจฉริยะในที่พักอาศัยเพื่อสกัดและวิเคราะห์ข้อมูลห่วงโซ่อุปทานในครัวเรือนด้วยปัญญาประดิษฐ์ประมวลผลเฉพาะถิ่น (โครงงานที่ 6 ของอาจารย์ — อาจารย์มีนักศึกษาหลายคนทำหัวข้อคนละแบบ)

**English:** Development of a Localized Residential Intelligence Engine for Household Supply-Chain Analytics Using Edge Computing and Home Network Infrastructure

**สถาปัตยกรรม:** IP Camera (RTSP) → VLAN-isolated Edge Server (NPU) → YOLO document detection → Local OCR → Quantized Local LLM (Ollama: Llama-3/Phi-3/Gemma via llama.cpp) → Structured JSON → Home Assistant (MQTT) → Smart Fridge/Storage Inventory + Burn Rate prediction + Stateful validation dashboard

---

## 2. เกณฑ์จากอาจารย์ (คงที่ ไม่เปลี่ยน)

* ตัด keyword: Receipt, OCR, Invoice, Document Understanding
* เน้น: Local AI, Edge AI, On-device AI, Local/Efficient/Small LLM, Quantization, NPU, GPU, AI Accelerators
* เกณฑ์คัดเปเปอร์: **Scopus-indexed (บังคับ)** + high citation (เฉพาะ conceptual/core) + high impact factor (เฉพาะ methodology/results) + IEEE/ACM/Elsevier/Springer + cross-disciplinary ≥1 ฉบับ (ต้อง outside computing จริง)
* 4-Layer Evaluation Framework: CRAAP → Bibliometrics → GrCOT → GeCOT (ทำครบทั้ง 4 ชั้นแล้วในแชทคู่ขนาน ดูข้อ 5)

---

## 3. Assignment 2 — Fast-Track Research Skills: ✅ **FINAL เสร็จสมบูรณ์ อาจารย์เซ็นแล้ว**

ใช้ 5 เปเปอร์เดิม (P1-P5) พร้อม CRAAP score เต็มรูปแบบทุกข้อ (C-R-A-A-P แยกคะแนน 1-5):

|#|เปเปอร์|Venue|Citation|CRAAP รวม|
|-|-|-|-|-|
|P1|Cai et al. (2024) — Edge-LLM|IEEE ICWS 2024|62 ครั้ง|25/25|
|P2|Husom et al. (2025) — Sustainable LLM Inference|ACM Trans. IoT|58 ครั้ง|25/25|
|P3|Moon et al. (2025) — Hybe|ISCA 2025|9 ครั้ง|24/25|
|P4|Yin et al. (2026) — ShadowNPU|ACM MobiSys 2026|4 ครั้ง|24/25|
|P5|Oloko-Oba et al. (2026) — Biosignals to Bedside|Bioengineering (MDPI)|(review article)|24/25|

**DOI ทั้งหมดยืนยันถูกต้อง 100%** — ไฟล์นี้จบแล้ว ไม่ต้องแตะอีก

---

## 4. Assignment 3 — Literature Review: ⚠️ **ตัดสินใจหลักแล้วในรอบนี้ ที่เหลือคือ execution**

### 4.1 ไฟล์ที่ส่งจริง (`Ass3_Literature_Review___1_.docx`)

ใช้ 5 เปเปอร์เดียวกับ Ass2 (P1-P5 ด้านบน) — เวอร์ชันที่ส่งจริงยังไม่มีการแก้ไข formatting (แก้หลังส่งไปแล้ว จึงยังไม่ส่งผลต่อเกรดจริง เว้นแต่มีรอบ resubmission)

### 4.2 ✅ จุดขัดแย้งเดิมระหว่างข้อเสนอ 1 กับข้อเสนอ 2 — **ตัดสินใจแล้วในรอบนี้**

**เรื่อง P5 (Biosignals to Bedside):** **เก็บไว้ แต่ลด role** — เหตุผลชี้ขาด: เกณฑ์อาจารย์บังคับ cross-disciplinary ≥1 ฉบับ (outside computing จริง) และ P5 เป็นฉบับเดียวใน Ring0 ที่ทำหน้าที่นี้ได้ ข้อเสนอ 2 ที่บอกให้ตัดทิ้งไม่ได้เสนอตัวแทน cross-disciplinary มาแทน จึงเลือกทางกลาง:
- ไม่ใช้ P5 เป็น pillar หลักที่ synthesis เข้ากับ hardware architecture (domain ไม่ตรงจริงตามที่ Razor 1 ชี้)
- ใช้เป็น evidence สนับสนุนความสำคัญของ on-device/real-time inference ในบริบท critical (health monitoring) วางไว้ใน introduction/motivation แทน

**เรื่อง Research Gap:** **Reframe เป็น "performance trade-off"** — ตัดสินใจทำแล้ว เพราะมี measurable research question ชัดกว่า "system integration/API glue" และใช้ Pilot 1/2 ที่ออกแบบไว้แล้วได้ทันที ไม่ต้องเปลี่ยนแผน pilot ร่างแรกของ gap statement เขียนไว้แล้ว (ดูข้อ 4.3) — เน้น 3 มิติ: grammar-constrained decoding latency, NPU quantization loss, JSON schema precision บน SBC

### 4.3 ร่าง Research Gap (ฉบับร่างแรก — พร้อมใช้)

> งานวิจัยที่ผ่านมาด้าน on-device LLM inference มักศึกษาปัจจัยด้านประสิทธิภาพแยกจากกัน — งานด้าน quantization เน้นวัด trade-off ระหว่างขนาดโมเดลกับความแม่นยำ (เช่น Husom et al., 2025) งานด้าน hardware acceleration เน้นวัด latency บน NPU เฉพาะทาง (เช่น Yin et al., 2026) ขณะที่งานด้าน structured output/grammar-constrained decoding (เช่น SGLang) เน้นวัด throughput ของการบังคับ schema แต่ยังไม่มีงานที่ประเมินปฏิสัมพันธ์ร่วมกันของทั้งสามมิตินี้ภายใต้ single-board computer (SBC) ที่มีทรัพยากรจำกัดจริง งานวิจัยนี้จึงมุ่งวัด performance trade-off ทั้งสามมิติพร้อมกันบน SBC edge device จริง ผ่าน Pilot 1-2 ที่ออกแบบไว้

**หมายเหตุ:** ยังไม่ได้ใส่ประเด็น time-series forecasting (household consumption) เพราะไม่จำเป็นสำหรับ framing ใหม่นี้ (ดูข้อ 4.4) — Holt-Winters paper ที่หามาสำรองไว้แล้วในกรณีต้องการเก็บประเด็นนี้ไว้

### 4.4 ✅ ผล Verify DOI ของ P6-P12 (ทำครบแล้วในรอบนี้ — เช็คทีละฉบับด้วย web search จริง)

| เปเปอร์ที่เสนอเดิม | สถานะ | สรุป |
|---|---|---|
| P6 AdaHome | 🔴 ไม่ใช้ | มีจริงแต่เป็น arXiv preprint (ก.ค. 2026) ยังไม่ผ่าน Scopus — ไม่จำเป็นสำหรับ framing ใหม่อยู่แล้ว |
| P7 HomeAssistant LLM | 🔴 ไม่ใช้ | ชื่อ/venue ที่อ้างไม่ตรงกับที่เจอจริง (พบแค่ OpenReview preprint) — ไม่จำเป็นสำหรับ framing ใหม่ |
| **P8 RL-Struct/FSM** | 🔴 ชื่อนี้ไม่มีจริง → **แทนด้วย SGLang** | ✅ verify แล้วด้วย web search: ตีพิมพ์จริง NeurIPS 2024 (Advances in NeurIPS 37, pp. 62557-62583) DOI `10.5555/3737916.3739916` ตรงกันทุกแหล่ง (dblp, ACM DL, Stanford bibliography) |
| P9 mPLUG-DocOwl2 | 🔴 ไม่ใช้ | มีจริงแต่เป็น arXiv preprint เท่านั้น ยังไม่ยืนยันฉบับตีพิมพ์ Scopus — ไม่จำเป็นสำหรับ framing ใหม่ |
| **P10 RK3588 SBC benchmark** | 🔴 ของเดิมไม่มีอยู่จริง (มีแต่ blog) → **แทนด้วย Edge-LLM-Bench** | ✅ verify แล้ว: Duc Viet Le, Özlem Durmaz Incel — ตีพิมพ์จริง ACM MobiSys '26 Workshops (Cambridge, มิ.ย. 2026) ทดสอบ Raspberry Pi 5 + Hailo-10H NPU DOI `10.1145/3812836.3814998` ยืนยันตรงจาก researchr.org และ ACM DL |
| **P11 Household Consumption Forecasting** | ⚠️ ของเดิมชื่อ journal ผิด → **แก้เป็น Adaptive Holt-Winters IoT** | ✅ verify แล้ว: Sawalha, S., & Al-Naymat, G. (2025) ตีพิมพ์ในวารสาร **"IoT"** (MDPI) เล่ม 6(3):39 — ชื่อ journal ที่ถูกต้องคือ "IoT" ไม่ใช่ "Journal of Sensor and Actuator Networks" ตามที่เข้าใจผิดตอนแรก DOI `10.3390/iot6030039` ยืนยันตรงจากหลายแหล่งอ้างอิง |
| P12 MQTT Gateway | 🔴 ไม่ใช้ | ชื่อ/venue ที่อ้างยังไม่เคยเช็คตรงตัว มีความเสี่ยง hallucination แบบเดียวกับ P8/P10 เดิม — ไม่จำเป็นสำหรับ framing ใหม่ |

**สรุป:** สำหรับ framing "performance trade-off" ที่เลือกแล้ว **ไม่จำเป็นต้องใช้ P6/P7/P9/P12** (กลุ่ม smart-home/pipeline integration ไม่ใช่แกนหลักของ gap ใหม่) — เปเปอร์ที่นำมาใช้จริงมีแค่ 3 ฉบับใหม่: **SGLang, Edge-LLM-Bench, Adaptive Holt-Winters IoT** (ทั้ง 3 ผ่าน verify DOI/venue แล้ว)

⚠️ **ข้อจำกัดที่ยังเหลืออยู่:** verify ได้แค่ "เปเปอร์มีจริง + DOI/venue ตรง" เท่านั้น **สถานะ Scopus indexing ของทั้ง 3 ฉบับใหม่ยังไม่ยืนยัน** ต้องเช็คเองผ่าน library.kku.ac.th ก่อนใส่ Final Cut จริง (เหมือนที่ทำกับ 124 ฉบับก่อนหน้าในแชทคู่ขนาน)

---

## 5. Literature Review หลัก (151→ปรับเป็น Final Cut ในแชทคู่ขนาน)

* เริ่มจาก 146 เปเปอร์จาก Semantic Scholar → เพิ่ม 5 conceptual/core → **151 ฉบับ**
* แชทคู่ขนาน (round 7) เช็ค Scopus มือครบ 100% (124/124 แถวที่เช็คได้) → ตัด 16 เปเปอร์ Priority (Ring0) ที่ Not Found ใน Scopus ออกจาก Final Cut
* **Ring0 เหลือจริง 35 ฉบับ** (จากเดิมนับหมวดหมู่ไว้ 51 ฉบับ)
* 4-Layer Evaluation Framework (CRAAP/Bibliometrics/GrCOT/GeCOT) — ทำครบทั้ง 4 ชั้นแล้วในแชทคู่ขนาน
* CARS venue — ยืนยันแล้วว่าเป็น IEEE Cyber Awareness and Research Symposium ไม่ใช่ Computer Assisted Radiology and Surgery

**ไฟล์ปัจจุบันที่ใช้งานจริง: `papers_role_tagged_v11.xlsx`** (v10 และก่อนหน้าเลิกใช้ — v11 เพิ่ม 3 แถวใหม่ SGLang/Edge-LLM-Bench/Holt-Winters IoT พร้อม flag "รอ Scopus confirm" และ Ring ใหม่ `Ring2 - Structured Output/Constrained Decoding`; เก็บ P8/P10/P11 เดิมไว้เป็นบันทึกเหตุผลที่ตัดออก ไม่ได้ลบทิ้ง)

### สถานะจำนวนเปเปอร์ปัจจุบัน (นับจริง)

| กลุ่ม | เปเปอร์ | สถานะ |
|---|---|---|
| ยืนยันแล้ว 100% (Scopus confirmed) | P1 Cai, P2 Husom, P3 Moon, P4 Yin, P5 Oloko-Oba | ✅ 5 ฉบับ |
| มีจริง + venue/DOI verify แล้ว แต่ยังไม่เช็ค Scopus | SGLang, Edge-LLM-Bench, Adaptive Holt-Winters IoT | ⚠️ +3 ฉบับ |
| **รวมตอนนี้** | | **8 ฉบับ** |
| ยังขาดอีก | | **2-4 ฉบับ** ถึงจะครบ 10-12 ตามที่อาจารย์สั่ง (ควรหาเพิ่มในธีม SBC benchmark / quantization-loss / constrained-decoding — ไม่จำเป็นต้องเป็น P6/P7/P9/P12 เดิม เพราะเสี่ยง hallucination) |

---

## 6. Pilot Experiments (ออกแบบและเริ่มแล้วในแชทคู่ขนาน)

|Pilot|เนื้อหา|สถานะ|
|-|-|-|
|Pilot 1|OCR accuracy: PaddleOCR vs EasyOCR บนใบเสร็จ/ฉลากไทยจริง|ออกแบบเสร็จ + instrument พร้อม (`pilot1_ocr_data_log.xlsx`, `cer_wer_calculator.py`) — พร้อมเริ่มเก็บข้อมูลได้ทันที ไม่ต้องรอ IRB|
|Pilot 2|LLM extraction accuracy: 2×3 factorial (3 โมเดล × free-form/GBNF grammar-constrained)|ออกแบบเสร็จ + instrument พร้อม (`pilot2_llm_extraction_log.xlsx`, `json_extraction_scorer.py`) — ใช้ dataset จาก Pilot 1 ต่อได้|
|Pilot 3|End-to-end accuracy ผ่าน User Correction Rate (proxy metric) บน dashboard จริงในบ้าน|ออกแบบเสร็จ + ร่าง Consent/IRB เสร็จแล้ว (`Pilot3_Consent_IRB_Draft.docx`) — ยังไม่ได้ยื่น IRB จริง (ต้อง submit ผ่าน eckku.kku.ac.th ด้วยบัญชี มข. เอง)|

**หมายเหตุ:** `cer_wer_calculator.py` ตัดคำแบบ whitespace-split เพราะเครื่องพัฒนาไม่มีเน็ต — ต้อง `pip install pythainlp` ที่เครื่องจริงก่อนรัน

---

## 7. งานที่เหลือทั้งหมด (อัปเดตลำดับความสำคัญหลังตัดสินใจรอบนี้)

1. ~~ตัดสินใจข้อขัดแย้งเรื่อง P5~~ ✅ **เสร็จแล้ว** — เก็บไว้แบบลด role (ดูข้อ 4.2)
2. ~~ตัดสินใจ reframe research gap~~ ✅ **เสร็จแล้ว** — ใช้ "performance trade-off" (ร่างพร้อมแล้ว ดูข้อ 4.3)
3. ~~เช็ค DOI ของเปเปอร์ P6-P12~~ ✅ **เสร็จแล้ว** — ผลอยู่ในข้อ 4.4 (ใช้จริงแค่ 3 ฉบับ: SGLang, Edge-LLM-Bench, Holt-Winters IoT)
4. **🔴 เช็ค Scopus ของ 3 ฉบับใหม่** (SGLang, Edge-LLM-Bench, Adaptive Holt-Winters IoT) ที่ library.kku.ac.th ด้วยบัญชี มข. เอง — ยังไม่มีใครเช็คให้ได้เพราะต้อง login
5. **หาเปเปอร์เพิ่มอีก 2-4 ฉบับ** ในธีม SBC benchmark / quantization-loss / constrained-decoding ให้ครบ 10-12 ฉบับตามเกณฑ์อาจารย์ (แยกจากเรื่อง framing — เป็นเงื่อนไขจำนวนของวิชาสัมมนา)
6. ตัดสินใจว่า Ring0 ที่เหลือ 35 ฉบับพอไหม ถ้าไม่พอ หา journal/published version ของ 16 ฉบับที่ถูกตัดเพิ่มเติม
7. เริ่มเก็บข้อมูล **Pilot 1** จริง (พร้อมเริ่มได้ทันที) — ใบเสร็จ 60-80 ใบ + ฉลากอาหาร 40-60 ภาพ
8. เริ่มเก็บข้อมูล **Pilot 2** ต่อจาก Pilot 1
9. ยื่น IRB จริงสำหรับ Pilot 3 ผ่าน eckku.kku.ac.th (ร่างพร้อมแล้ว รอยื่นจริง)
10. เขียน Ass3 ใหม่ตามทิศทางที่ตัดสินใจในข้อ 1-2 (P5 + gap reframe) แล้วจึงค่อยไล่ format ตาม APA ให้ครบ (เรียงอ้างอิง, hyperlink DOI, page range ฯลฯ)

---

## 8. ไฟล์ทั้งหมดที่มีอยู่ (รวมทุกแหล่ง)

|ไฟล์|มาจากแชท|เนื้อหา|
|-|-|-|
|`papers_role_tagged_v11.xlsx`|แชทนี้ (อัปเดตจาก v10 คู่ขนาน)|⭐ ไฟล์ literature tracking หลักปัจจุบัน — เพิ่ม SGLang/Edge-LLM-Bench/Holt-Winters IoT|
|`papers_role_tagged_v10.xlsx`|คู่ขนาน (round7)|เวอร์ชันก่อนหน้า เลิกใช้ เก็บไว้อ้างอิง|
|`handoff_thesis_status_round7.md`|คู่ขนาน|บันทึกละเอียด round 7|
|`pilot_experiments_design_v1.md`|คู่ขนาน|ออกแบบ 3 pilot เต็มรูปแบบ|
|`pilot1_ocr_data_log.xlsx` + `cer_wer_calculator.py`|คู่ขนาน|Instrument Pilot 1|
|`pilot2_llm_extraction_log.xlsx` + `json_extraction_scorer.py`|คู่ขนาน|Instrument Pilot 2|
|`Pilot3_Consent_IRB_Draft.docx`|คู่ขนาน|ร่าง Consent/IRB Pilot 3|
|`GrCOT_GeCOT_evaluation.md`, `CRAAP_test_Ring0_Ring1.md`, `GeCOT_full_system_evaluation.md`|คู่ขนาน|ผล 4-Layer Evaluation|
|`Ass2_Fast-Track_Research_Skills...pdf`|แชทนี้ (เซ็นแล้ว)|Assignment 2 — FINAL|
|`Ass3_Literature_Review___1_.docx`|แชทนี้|ฉบับที่ส่งอาจารย์จริง (5 เปเปอร์, ยังไม่แก้ format)|
|`Ass3_Literature_Review_แก้ไขแล้ว.docx`|แชทนี้|เวอร์ชันแก้ format แล้ว — ใช้เป็น template สำหรับตอนแก้ไขส่งใหม่|
|`4_main_project_2026.docx`|แชทนี้|โจทย์ 5 โครงงานจากอาจารย์ (อ้างอิง)|
|`Beyond_CRAAP_Citation_Metrics.docx`|แชทนี้|เปรียบเทียบ CRAAP/Bibliometrics/GeCOT/GrCOT|
|`check_papers.py`|แชทนี้|ดึง citation/venue จาก Semantic Scholar API|

---

## วิธีใช้ไฟล์นี้ในแชทใหม่

แนบไฟล์นี้ + `papers_role_tagged_v11.xlsx` + `pilot_experiments_design_v1.md` + `Ass3_Literature_Review___1_.docx` (ฉบับจริงที่ส่งไปแล้ว) เป็นอย่างน้อย พร้อมบอกว่า "นี่คือ handoff รวมจากงานวิทยานิพนธ์ ช่วยอ่านแล้วต่อจากข้อ [ระบุลำดับ] ในส่วนที่ 7"
