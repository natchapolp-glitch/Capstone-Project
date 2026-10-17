# Research Gap ฉบับสมบูรณ์ — Performance Trade-off (12 ฉบับ)
**สำหรับแทรกในหัวข้อ 2.3 "ช่องว่างทางความรู้ (Research Gap)" ของ Ass3_Literature_Review.docx**

---

## ร่าง Research Gap (ผูก citation ครบ 12 ฉบับ)

งานวิจัยด้านการอนุมานแบบจำลองภาษาบนอุปกรณ์ประมวลผลเฉพาะถิ่น (on-device LLM inference) ในช่วงที่ผ่านมามีแนวโน้มศึกษาปัจจัยด้านประสิทธิภาพแยกออกจากกันเป็นสามมิติหลัก แทนที่จะประเมินปฏิสัมพันธ์ร่วมกันภายใต้ทรัพยากรจำกัดจริงของอุปกรณ์ single-board computer (SBC)

ในมิติแรก งานวิจัยกลุ่มที่มุ่งเน้นการบีบอัดแบบจำลอง (quantization) และสถาปัตยกรรมฮาร์ดแวร์เร่งความเร็วมีจำนวนมากและมีความก้าวหน้าอย่างต่อเนื่อง Cai et al. (2024) เสนอกรอบการทำงาน Edge-LLM ที่ผสมผสาน adaptive quantization ร่วมกับกลไกแคชเพื่อลดภาระ GPU โดยยังคงพึ่งพาคลาวด์บางส่วน ขณะที่ Husom et al. (2025) ประเมินแบบจำลอง quantized LLM จำนวน 28 แบบจำลองบน Raspberry Pi 4 และพบว่าการลดระดับการบีบอัดส่งผลโดยตรงต่อทั้งประสิทธิภาพเชิงพลังงานและความแม่นยำของผลลัพธ์ Moon et al. (2025) และ Yin et al. (2026) นำเสนอสถาปัตยกรรมฮาร์ดแวร์เฉพาะทางระดับ GPU-NPU และ NPU-on-smartphone ตามลำดับ เพื่อลดความหน่วงของการอนุมาน แต่ทั้งสองงานอาศัยฮาร์ดแวร์ที่มีต้นทุนสูงกว่าหรือมีระบบนิเวศต่างจาก SBC ในบริบทที่พักอาศัย Zheng et al. (2025) สังเคราะห์ภาพรวมของสายงานนี้ไว้ในการทบทวนวรรณกรรมที่ครอบคลุมตั้งแต่การออกแบบแบบจำลองจนถึงการอนุมานขณะรันไทม์บนอุปกรณ์ edge ส่วน Giedra et al. (2026) ได้วัด trade-off ระหว่างความแม่นยำและประสิทธิภาพพลังงานของแบบจำลอง quantized ขนาด sub-1B ถึง 8B บนอุปกรณ์ NVIDIA Jetson โดยตรง ซึ่งเป็นหลักฐานเชิงประจักษ์ล่าสุดที่ยืนยันว่าระดับการบีบอัดแบบจำลองส่งผลต่อทั้งความเร็วและความแม่นยำอย่างมีนัยสำคัญบนอุปกรณ์ที่มีทรัพยากรจำกัดจริง อย่างไรก็ตาม งานวิจัยกลุ่มนี้ทั้งหมดวัดผลกระทบของ quantization ต่อความแม่นยำเชิง benchmark ทั่วไป (เช่น question-answering, reasoning) มิได้เชื่อมโยงกับความแม่นยำของผลลัพธ์ที่มีโครงสร้าง (structured output) ซึ่งเป็นรูปแบบผลลัพธ์ที่จำเป็นสำหรับงานสกัดข้อมูล

ในมิติที่สอง งานวิจัยด้านการบังคับโครงสร้างผลลัพธ์ของแบบจำลองภาษาก็เป็นสายงานที่พัฒนาแยกต่างหากเช่นกัน Zheng et al. (2024) นำเสนอ SGLang ซึ่งใช้เทคนิค compressed finite state machine เพื่อเร่งความเร็วการถอดรหัสแบบมีโครงสร้าง (grammar-constrained decoding) ให้ throughput สูงขึ้นถึง 6.4 เท่าเทียบกับระบบอนุมานทั่วไป แต่งานดังกล่าวทดสอบบนฮาร์ดแวร์ระดับ data center มิใช่ edge NPU ขณะที่ Hu et al. (2025) พัฒนา mPLUG-DocOwl2 สำหรับความเข้าใจเอกสารหลายหน้าแบบ OCR-free ที่ลดจำนวน visual token ได้มากกว่า 80% แต่เป็นแบบจำลองขนาดใหญ่ที่ยังไม่ได้ออกแบบมาเพื่อทำงานร่วมกับ quantized local LLM บน SBC งานทั้งสองฉบับนี้ชี้ให้เห็นว่าการบังคับ schema ระหว่างการถอดรหัสส่งผลโดยตรงต่อทั้งความเร็วและความถูกต้องของ JSON output แต่ยังไม่มีงานใดวัดผลกระทบนี้ร่วมกับระดับการบีบอัดแบบจำลองบนอุปกรณ์ edge NPU ทรัพยากรจำกัดพร้อมกัน

ในมิติที่สาม บริบทของการประยุกต์ใช้งานจริงในครัวเรือนก็เป็นสายงานที่พัฒนาคู่ขนานกันไปเช่นกัน Rivkin et al. (2025) นำเสนอตัวแทน LLM อัตโนมัติสำหรับควบคุมอุปกรณ์ในบ้านอัจฉริยะ (AIoT smart home) ซึ่งแสดงให้เห็นศักยภาพของ LLM ในการเชื่อมต่อกับระบบ IoT ในครัวเรือน แต่มิได้กล่าวถึงข้อจำกัดด้านฮาร์ดแวร์ระดับ SBC หรือความแม่นยำของการสกัดข้อมูลเชิงโครงสร้าง ส่วนในระดับปลายน้ำของสถาปัตยกรรม Sawalha and Al-Naymat (2025) เสนอแบบจำลอง Adaptive Holt–Winters สำหรับพยากรณ์ข้อมูลอนุกรมเวลาตามฤดูกาลจากข้อมูล IoT ซึ่งสามารถประยุกต์ใช้กับการพยากรณ์อัตราการสิ้นเปลืองสินค้าในครัวเรือน (burn rate) ได้ในเชิงหลักการ และ Serepas et al. (2025) นำเสนอการออกแบบ IoT gateway น้ำหนักเบาบนไมโครคอนโทรลเลอร์ ESP32 ที่รองรับโปรโตคอล MQTT สำหรับเชื่อมต่ออุปกรณ์ edge เข้ากับระบบบ้านอัจฉริยะ ซึ่งสอดคล้องโดยตรงกับ stage การเชื่อมต่อ Home Assistant ผ่าน MQTT ในสถาปัตยกรรมของโครงงานนี้ อย่างไรก็ตาม ทั้งสามงานนี้ศึกษาเฉพาะชั้นการเชื่อมต่อและการพยากรณ์ปลายน้ำ โดยไม่ได้เชื่อมโยงย้อนกลับไปถึงความแม่นยำของการสกัดข้อมูลต้นทางจาก LLM ภายใต้ข้อจำกัดด้าน quantization และ decoding ที่กล่าวถึงในมิติแรกและมิติที่สอง

นอกจากนี้ เพื่อยืนยันว่าแนวคิดการประมวลผลแบบ on-device เพื่อการตัดสินใจแบบเรียลไทม์มีความสำคัญข้ามศาสตร์วิชา มิได้จำกัดอยู่เฉพาะสายวิทยาการคอมพิวเตอร์ งานทบทวนวรรณกรรมของ Oloko-Oba et al. (2026) ในสาขาวิศวกรรมชีวการแพทย์ได้แสดงให้เห็นว่าการประมวลผลสัญญาณชีวภาพแบบเรียลไทม์บนอุปกรณ์ edge สำหรับการติดตามสุขภาพด้วยอุปกรณ์สวมใส่ เผชิญกับความท้าทายด้าน latency และความน่าเชื่อถือของข้อมูลภาคสนามในลักษณะที่คล้ายคลึงกับบริบทของโครงงานนี้ แม้จะเป็นคนละโดเมนการประยุกต์ใช้งาน จึงเป็นหลักฐานสนับสนุนว่าความสำคัญของ real-time on-device inference ภายใต้ทรัพยากรจำกัดเป็นปัญหาร่วมของหลายสาขาวิชา มิใช่ปัญหาเฉพาะทางวิศวกรรมคอมพิวเตอร์เพียงอย่างเดียว

โดยสรุป จากการทบทวนวรรณกรรมทั้ง 12 ฉบับ พบว่างานวิจัยที่ผ่านมาศึกษาปัจจัยด้านประสิทธิภาพของ on-device LLM inference แยกเป็นสามมิติที่ไม่เชื่อมโยงกัน ได้แก่ (1) trade-off ระหว่างระดับการบีบอัดแบบจำลอง (quantization) กับความแม่นยำและความเร็วบนฮาร์ดแวร์ NPU/edge (Cai et al., 2024; Husom et al., 2025; Moon et al., 2025; Yin et al., 2026; Zheng et al., 2025; Giedra et al., 2026) (2) ผลกระทบของการบังคับโครงสร้างผลลัพธ์ (grammar-constrained decoding) ต่อความเร็วและความถูกต้องของ JSON output (Zheng et al., 2024; Hu et al., 2025) และ (3) การประยุกต์ใช้งานในบริบทบ้านอัจฉริยะและการพยากรณ์ปลายน้ำ (Rivkin et al., 2025; Sawalha & Al-Naymat, 2025; Serepas et al., 2025) แต่ยังไม่มีงานวิจัยฉบับใดประเมินปฏิสัมพันธ์ร่วมกันของทั้งสามมิตินี้ — ความหน่วงของ grammar-constrained decoding, ความสูญเสียความแม่นยำจาก NPU quantization, และความแม่นยำของ JSON schema — พร้อมกันบนอุปกรณ์ single-board computer (SBC) ที่มีทรัพยากรจำกัดจริงในบริบทที่พักอาศัย งานวิจัยนี้จึงมุ่งวัด performance trade-off ทั้งสามมิติพร้อมกันบน SBC edge device จริง ผ่าน Pilot 1–2 ที่ออกแบบไว้ เพื่ออุดช่องว่างทางความรู้ดังกล่าว

---

## รายการอ้างอิงที่ต้องเพิ่มในไฟล์ Ass3.docx (APA 7th) — P6–P12

*(P1–P5 มีอยู่แล้วในไฟล์เดิม ไม่ต้องเพิ่มซ้ำ)*

Giedra, H., Matuzevičius, D., Sledevič, T., Shubitidze, G., & Serackis, A. (2026). Benchmarking large language model inference on limited-resource edge systems. *Electronics, 15*(11), Article 2451. https://doi.org/10.3390/electronics15112451

Hu, A., Xu, H., Zhang, L., Ye, J., Yan, M., Zhang, J., Jin, Q., Huang, F., & Zhou, J. (2025). mPLUG-DocOwl2: High-resolution compressing for OCR-free multi-page document understanding. In *Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 5817–5834). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.acl-long.291

Rivkin, D., Hogan, F., Feriani, A., Konar, A., Sigal, A., Liu, X., & Dudek, G. (2025). AIoT smart home via autonomous LLM agents. *IEEE Internet of Things Journal, 12*(3), 2458–2472. https://doi.org/10.1109/JIOT.2024.3471904

Sawalha, S., & Al-Naymat, G. (2025). An adaptive Holt–Winters model for seasonal forecasting of Internet of Things (IoT) data streams. *IoT, 6*(3), Article 39. https://doi.org/10.3390/iot6030039

Serepas, F., Papias, I., Christakis, K., Dimitropoulos, N., & Marinakis, V. (2025). Lightweight embedded IoT gateway for smart homes based on an ESP32 microcontroller. *Computers, 14*(9), Article 391. https://doi.org/10.3390/computers14090391

Zheng, L., Yin, L., Xie, Z., Sun, C. L., Huang, J., Yu, C. H., Cao, S., Kozyrakis, C., Stoica, I., Gonzalez, J. E., Barrett, C., & Sheng, Y. (2024). SGLang: Efficient execution of structured language model programs. *Advances in Neural Information Processing Systems, 37*, 62557–62583. https://doi.org/10.5555/3737916.3739916

Zheng, Y., Chen, Y., Qian, B., Shi, X., Shu, Y., & Chen, J. (2025). A review on edge large language models: Design, execution, and applications. *ACM Computing Surveys, 57*(8), Article 209. https://doi.org/10.1145/3719664

---

## หมายเหตุการใช้งาน

1. ย่อหน้าร่างด้านบนเขียนต่อเนื่องเป็น narrative ผูก citation ครบทั้ง 12 ฉบับแล้ว — พร้อมนำไปแทนที่หัวข้อ **2.3 ช่องว่างทางความรู้ (Research Gap)** ในไฟล์ Ass3.docx เดิมได้ทันที (เดิมอ้างอิงจาก P1–P5 เท่านั้น ฉบับนี้ขยายเป็น P1–P12 และ reframe เป็น performance trade-off ตามมติที่ตัดสินใจไว้)
2. ยังไม่ได้แก้ **หัวข้อ 1 (Synthesis Matrix)**, **หัวข้อ 2.1–2.2 (Consensus/Disagreement)**, หรือ **หัวข้อ 3 (Literature Review เรียบเรียง)** ในไฟล์ Ass3.docx — งานเหล่านี้ตรงกับข้อ 6–7 ในหัวข้อ "งานที่เหลือ" ของ handoff v2 ซึ่งยังไม่ได้เริ่ม
3. ชื่อผู้แต่งอ้างอิงทั้งหมดตรวจสอบจาก DOI/หน้าเว็บทางการของสำนักพิมพ์แล้ว (ACM DL, dblp, MDPI, arXiv, ACL Anthology) ณ วันที่ 6 ส.ค. 2026 — ยังไม่ได้ตรวจสถานะ Scopus ของ P6–P12 ซ้ำในรอบนี้ (ใช้สถานะจากไฟล์ `papers_role_tagged_v11.xlsx` เดิม)
