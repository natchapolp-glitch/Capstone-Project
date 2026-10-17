"""Build a small, manually reviewed receipt-page detection set outside OneDrive."""

import csv
import shutil
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LAB = Path.home() / "SeminarLab"
DATA = LAB / "yolo_pilot"

# Relative paper bounding boxes estimated from visual inspection of each source photo.
# These are only for a feasibility pilot, not a production ground-truth dataset.
BOXES = {
    "S__18440201_0.jpg": (0.33, 0.17, 0.73, 0.96),
    "S__18440213_0.jpg": (0.04, 0.18, 0.93, 0.80),
    "S__18440214_0.jpg": (0.00, 0.13, 0.88, 0.76),
    "S__18440216_0.jpg": (0.01, 0.16, 0.95, 0.79),
    "S__18440219_0.jpg": (0.02, 0.21, 0.90, 0.82),
    "S__18440221_0.jpg": (0.00, 0.20, 0.98, 0.88),
    "S__18440253_0.jpg": (0.03, 0.22, 0.99, 0.91),
    "S__18440257_0.jpg": (0.30, 0.05, 0.70, 1.00),
    "S__18440258_0.jpg": (0.21, 0.08, 0.69, 0.97),
    "S__18440263_0.jpg": (0.29, 0.08, 0.67, 1.00),
    "S__18440264_0.jpg": (0.24, 0.01, 0.72, 1.00),
}
VAL = {"S__18440214_0.jpg", "S__18440257_0.jpg", "S__18440258_0.jpg"}


def main():
    with (LAB / "reports" / "pilot_itemized_20.csv").open(encoding="utf-8-sig", newline="") as stream:
        selected = {row["filename"]: row for row in csv.DictReader(stream)
                    if row["page_form"] == "single_page"}
    if set(selected) != set(BOXES):
        raise RuntimeError("Single-page selection changed; review labels before continuing")
    fig, axes = plt.subplots(3, 4, figsize=(14, 15))
    for ax, (filename, box) in zip(axes.flat, BOXES.items()):
        row = selected[filename]
        image_path = LAB / "incoming" / filename
        image = cv2.imread(str(image_path))
        h, w = image.shape[:2]
        x1, y1, x2, y2 = box
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            raise ValueError(filename)
        split = "val" if filename in VAL else "train"
        images = DATA / split / "images"
        labels = DATA / split / "labels"
        images.mkdir(parents=True, exist_ok=True)
        labels.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path, images / f"{row['doc_id']}.jpg")
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        (labels / f"{row['doc_id']}.txt").write_text(
            f"0 {cx:.6f} {cy:.6f} {x2-x1:.6f} {y2-y1:.6f}\n", encoding="ascii")
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax.plot([x1*w, x2*w, x2*w, x1*w, x1*w],
                [y1*h, y1*h, y2*h, y2*h, y1*h], color="red", linewidth=2)
        ax.set_title(f"{filename[3:11]} {split}", fontsize=10)
        ax.axis("off")
    for ax in axes.flat[len(BOXES):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(DATA / "label_review.png", dpi=140)
    plt.close(fig)
    yaml = f"path: {DATA.as_posix()}\ntrain: train/images\nval: val/images\nnames:\n  0: receipt_page\n"
    (DATA / "dataset.yaml").write_text(yaml, encoding="utf-8")
    print(f"Wrote 8 train and 3 val labeled photos to {DATA}")


if __name__ == "__main__":
    main()
