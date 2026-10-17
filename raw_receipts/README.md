# Raw document image intake

`incoming/` contains all **124 original JPG files** from the project intake, with their original filenames and image bytes. `manifest.csv` records each image's filename, SHA-256 hash, document classification, and review metadata. The manifest and images were copied from `SeminarLab` on 2026-10-17; hashes were checked after copying (124 matches, zero missing).

This intake includes purchase receipts, payment receipts, housing invoices, delivery notes, and other images. For the **59 itemized-purchase photo candidates** used in the current EDA and language review, filter `manifest.csv` to rows where `doc_type` is `itemized_purchase` and `duplicate_of` is blank. These are 59 images, not necessarily 59 independent transactions.

The images are raw and have not been redacted or resized. The research results and their limits are described in the [team handoff](../HANDOFF_ASS5_ASS6_FOR_TEAM_2026-10-17.md).
