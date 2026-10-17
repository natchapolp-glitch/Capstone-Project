# สถานะงานก่อนมีบอร์ด

อัปเดต 18 ตุลาคม 2569 — รอบนี้จัดทำแผนเท่านั้น ยังไม่เริ่ม implementation

แผนหลัก: [PREBOARD_IMPLEMENTATION_PLAN.md](PREBOARD_IMPLEMENTATION_PLAN.md)

| ข้อ | งาน | สถานะ | สิ่งที่มีแล้ว | หลักฐานที่ยังต้องทำ |
|---|---|---|---|---|
| 1 | เฉลย/กรอบ/ธุรกรรมซ้ำ | TODO | manifest และการตรวจชื่อ 59 ภาพ | เฉลยเต็มใบ, group/split audit, ผู้ตรวจคนที่สองจริง |
| 2 | OCR เปรียบเทียบ | TODO | EasyOCR และ spot-check 3 ภาพ | สอง engine บนชุดเดียวกัน, CER/field metrics จากเฉลยตรวจแล้ว |
| 3 | Local LLM → JSON | TODO | schema/scorer และ regression 10 กรณี | runtime/weights, matrix 16 เงื่อนไข, ผล inference จริง |
| 4 | เดโมครบถึง HA | TODO | เดโม YOLO PC | OCR/LLM/UI ยืนยัน/persistence/MQTT/HA พร้อม trace |
| 5 | Benchmark และต่างฉาก | TODO | ผล YOLO ต่างฉากเดิม 6 ภาพ | เวลา/RAM รายขั้น, ภาพใหม่และเฉลย, ผล challenge |

## เริ่มงานครั้งถัดไป

ผู้ใช้จะเปลี่ยนเป็น 6.1 sol ให้เริ่มตามส่วน “ลำดับทำงานและโครงไฟล์” ในแผน ไม่ถือว่าการเปลี่ยนโมเดลเกิดขึ้นเองจากการตั้ง goal

## Dependency ที่ต้องขอระหว่าง implementation

- ผู้ตรวจคนที่สองสำหรับตรวจเฉลยจากภาพและบันทึกผลแยกจริง เตรียมแพ็กเกจตรวจให้ก่อนขอให้ลงมือ
- ภาพจริงต่างฉากใหม่อย่างน้อย 6 ภาพ จากอย่างน้อย 3 ธุรกรรมไม่ซ้ำ ให้ส่งคำแนะนำเก็บภาพและวิธีตรวจซ้ำที่ชัดเจน

สองรายการนี้ไม่ขัดขวางการทำ environment, validators, runners, review UI, MQTT/HA integration และ tests ด้วยข้อมูลสมมติ แต่ยังปิด gate ผลทดลองจริงไม่ได้
