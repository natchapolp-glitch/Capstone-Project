"""Build the 48-photo receipt-region feasibility set after visual box review."""

import csv
import shutil
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LAB = Path.home() / "SeminarLab"
PROPOSALS = LAB / "reports" / "yolo_expanded_review" / "proposals.csv"
DATA = LAB / "yolo_expanded"
VAL_CODES = {198, 205, 214, 235, 239, 250, 252, 258, 265, 266}

# Relative bounds corrected by inspecting all four proposal contact sheets.
OVERRIDES = {
    198: (0.33, 0.18, 0.72, 0.94),
    223: (0.08, 0.04, 0.74, 0.93),
    226: (0.22, 0.06, 0.88, 0.94),
    235: (0.13, 0.16, 0.77, 0.90),
    236: (0.23, 0.05, 0.86, 0.91),
    237: (0.19, 0.06, 0.82, 0.92),
    238: (0.18, 0.08, 0.85, 0.95),
    239: (0.15, 0.06, 0.86, 0.96),
    243: (0.15, 0.06, 0.85, 0.94),
    249: (0.14, 0.09, 0.87, 0.93),
    250: (0.13, 0.13, 0.80, 0.94),
    261: (0.27, 0.12, 0.72, 0.94),
    265: (0.28, 0.12, 0.73, 0.94),
    266: (0.07, 0.18, 0.95, 0.94),
    281: (0.05, 0.17, 0.98, 0.91),
    290: (0.04, 0.19, 0.97, 0.90),
    292: (0.03, 0.20, 0.94, 0.90),
}


def code(filename):
    return int(filename.split("__")[1].split("_")[0][-3:])


def main():
    with PROPOSALS.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 48:
        raise RuntimeError("Expected 48 box proposals")
    # Rebuild only this derived dataset so changing the split leaves no stale files.
    for split in ("train", "val"):
        for kind in ("images", "labels"):
            folder = DATA / split / kind
            if folder.is_dir():
                shutil.rmtree(folder)
    fig, axes = plt.subplots(3, 4, figsize=(15, 15))
    report = []
    for index, row in enumerate(rows):
        filename = row["filename"]
        number = code(filename)
        box = OVERRIDES.get(number, tuple(float(row[key]) for key in ("x1", "y1", "x2", "y2")))
        if not (0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1):
            raise ValueError(filename)
        if row["source"] == "proposal_failed_full_frame_placeholder" and number not in OVERRIDES:
            raise RuntimeError(f"Unreviewed full-frame placeholder: {filename}")
        image_path = LAB / "incoming" / filename
        frame = cv2.imread(str(image_path))
        h, w = frame.shape[:2]
        split = "val" if number in VAL_CODES else "train"
        images = DATA / split / "images"
        labels = DATA / split / "labels"
        images.mkdir(parents=True, exist_ok=True)
        labels.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path, images / f"{row['doc_id']}.jpg")
        x1, y1, x2, y2 = box
        (labels / f"{row['doc_id']}.txt").write_text(
            f"0 {(x1+x2)/2:.6f} {(y1+y2)/2:.6f} {x2-x1:.6f} {y2-y1:.6f}\n",
            encoding="ascii")
        report.append({"doc_id": row["doc_id"], "filename": filename,
                       "split": split, "box_source": "manual_override" if number in OVERRIDES
                       else row["source"], "review_status": "assistant_visual_review"})
        ax = axes.flat[index % 12]
        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ax.plot([x1*w,x2*w,x2*w,x1*w,x1*w], [y1*h,y1*h,y2*h,y2*h,y1*h],
                color="red", linewidth=2)
        ax.set_title(f"{number} {split}", fontsize=10)
        ax.axis("off")
        if index % 12 == 11:
            fig.tight_layout()
            fig.savefig(DATA / f"label_review_{index//12+1:02d}.png", dpi=140)
            plt.close(fig)
            if index < len(rows)-1:
                fig, axes = plt.subplots(3, 4, figsize=(15, 15))
    yaml = f"path: {DATA.as_posix()}\ntrain: train/images\nval: val/images\nnames:\n  0: receipt_region\n"
    (DATA / "dataset.yaml").write_text(yaml, encoding="utf-8")
    with (DATA / "labels_review.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(report[0]))
        writer.writeheader()
        writer.writerows(report)
    if sum(row["split"] == "val" for row in report) != 10:
        raise RuntimeError("Expected 10 validation photos")
    print("Prepared 38 train and 10 validation photos")


if __name__ == "__main__":
    main()
