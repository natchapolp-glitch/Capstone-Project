# Capstone Project — SCS3-4

Residential intelligence capstone. Examination group **SCS3**.

## Current deliverables

Use **REVIEWED_2026-10-18**. Earlier READY files are retained as history.

| งาน | ไฟล์แก้ไขได้ | ไฟล์อ่าน/พิมพ์ |
|---|---|---|
| Ass5 สไลด์ 21 หน้า | [PowerPoint](ass5_output/Residential_Intelligence_Project_Progress_REVIEWED_2026-10-18.pptx) | [PDF](ass5_output/Residential_Intelligence_Project_Progress_REVIEWED_2026-10-18.pdf) |
| Ass6 รายงาน 22 หน้า | [Word](ass6_output/Residential_Intelligence_Computer_Project_Proposal_REVIEWED_2026-10-18.docx) | [PDF](ass6_output/Residential_Intelligence_Computer_Project_Proposal_REVIEWED_2026-10-18.pdf) |

บทพูด 21 สไลด์: [Residential_Intelligence_Presentation_Script_REVIEWED_2026-10-18.md](ass5_output/Residential_Intelligence_Presentation_Script_REVIEWED_2026-10-18.md)

Start with the [team handoff](HANDOFF_ASS5_ASS6_FOR_TEAM_2026-10-18.md), [guideline review](ASS5_ASS6_GUIDELINE_CHECK_2026-10-18.md), and [evidence audit](reports/preboard/deliverable_audit.json).

## Actual PC evidence

59 photographs have saved single-pass transcripts. Descriptive OCR CER uses 24 eligible photographs; 35 retain their exclusion status. Local LLM format/cost testing completed 288 attempts on six frozen photographs. Corrected PC-to-MQTT/Home Assistant timing completed nine trials on three photographs. These are not independent-transaction semantic accuracy results.

JSON field accuracy and fresh scene testing are **not yet experimented**, as agreed with the project owner. Board NPU/energy measurements require hardware. Skipped annotation fields are unreviewed, not empty ground truth. No second annotation round is required.

See [evidence summaries](reports/preboard/), [status](PREBOARD_STATUS.md), [scope](ASS5_ASS6_COMPLETION_GOAL.md), and [local demo quickstart](PREBOARD_QUICKSTART.md). The [raw images](raw_receipts/README.md) are retained. Models, transcript revisions, raw responses and SQLite evidence remain in the owner's external SeminarLab directory; public reports record their hashes. A friend's machine needs its own runtime/assets before localhost links work.

The original Ass4 and pre-feedback Ass5 remain the foundations. e-Senses is the system concept; e-Eye is the current experimental part. Builder directories contain reproducible update scripts, not additional final submissions. Work is on `pc-preboard-implementation`.
