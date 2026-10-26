# Capstone Project — SCS3-4

> **ล่าสุด 26 ตุลาคม 2569:** เริ่มที่ [ชุดพรี 10 นาที](PRESENTATION_READY_2026-10-26/START_HERE.md) — สไลด์ v3 พร้อม notes บทพูดสองคน คู่มือเดโม 2 นาที และ Q&A; Robot/Selenium รอบใหม่ผ่าน 7/7 แล้ว แผนหลักอัดคลิปกดอ่านภาพจริงตามบท ยังต้องอัด/ตรวจคลิป และซ้อมจับเวลาจริง


Residential intelligence capstone. Examination group **SCS3**.

## Current deliverables

Ass5 ใช้ชุด 10MIN_RECORDED_DEMO_v3_2026-10-26 คู่กับบทพูด v3 และคู่มือเดโมด้านล่าง ส่วน Ass6 คง FORMAT_REVIEWED_2026-10-21 ไม่ได้แก้ในรอบนี้ เอกสาร handoff รุ่นก่อนเป็นประวัติ

| งาน | ไฟล์แก้ไขได้ | ไฟล์อ่าน/พิมพ์ |
|---|---|---|
| Ass5 สไลด์ 21 หน้า | [PowerPoint พร้อม notes](PRESENTATION_READY_2026-10-26/Ass5_10MIN_RECORDED_DEMO_v3_2026-10-26.pptx) | [PDF](PRESENTATION_READY_2026-10-26/Ass5_10MIN_RECORDED_DEMO_v3_2026-10-26.pdf) |
| Ass6 รายงานล่าสุด | [Word](Residential_Intelligence_Proposal_FORMAT_REVIEWED_2026-10-21.docx) | ใช้ Word นี้เป็นหลัก; PDF รุ่นก่อนอาจต่างจากการบันทึกล่าสุด |

บทอัดคลิป: [กดอ่านภาพจริง → ตรวจแก้ → Home Assistant](PRESENTATION_READY_2026-10-26/RECORD_DEMO_SCRIPT.html)

บทพูด: [สองคน 10 นาที](PRESENTATION_READY_2026-10-26/SCRIPT_10_MIN_REVIEWED_v3.md) · [คู่มือเดโม 2 นาที](PRESENTATION_READY_2026-10-26/DEMO_2_MIN_RUNBOOK.md) · [Q&A ครบ 21 หน้า](PRESENTATION_READY_2026-10-26/QA_ALL_21_SLIDES.md)

Start with the [current review handoff](HANDOFF_PRESENTATION_REVIEW_2026-10-26.md), [review findings](PRESENTATION_READY_2026-10-26/REVIEW_RESULTS_2026-10-26.md), and [single-run Robot report](DEMO_PRESENTATION_2026-10-21/robot_results/run-20261026-185448/report.html). The latest passing run followed the owner's antivirus change; it does not certify operation after protection settings change again. Earlier guideline/evidence audits describe their dated deliverables, not the new report pagination.

## Actual PC evidence

59 photographs have saved single-pass transcripts. Descriptive OCR CER uses 24 eligible photographs; 35 retain their exclusion status. Local LLM format/cost testing completed 288 attempts on six frozen photographs. Corrected PC-to-MQTT/Home Assistant timing completed nine trials on three photographs. These are not independent-transaction semantic accuracy results.

JSON field accuracy and fresh scene testing are **not yet experimented**, as agreed with the project owner. Board NPU/energy measurements require hardware. Skipped annotation fields are unreviewed, not empty ground truth. No second annotation round is required.

See [evidence summaries](reports/preboard/), [status](PREBOARD_STATUS.md), [scope](ASS5_ASS6_COMPLETION_GOAL.md), and [local demo quickstart](PREBOARD_QUICKSTART.md). The [raw images](raw_receipts/README.md) are retained. Models, transcript revisions, raw responses and SQLite evidence remain in the owner's external SeminarLab directory; public reports record their hashes. A friend's machine needs its own runtime/assets before localhost links work.

The original Ass4 and pre-feedback Ass5 remain the foundations. e-Senses is the system concept; e-Eye is the current experimental part. Builder directories contain reproducible update scripts, not additional final submissions. Work is on `pc-preboard-implementation`.
