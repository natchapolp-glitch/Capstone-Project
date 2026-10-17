"""Reserve six new itemized receipts as an unseen, different-scene test."""

import csv
import shutil
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LAB = Path.home() / "SeminarLab"
DATA = LAB / "external_scene_6"

# Assistant visual annotations from full-resolution photos, not model proposals.
# Bounds cover the visible paper, including paper clipped by the photo edge.
BOXES = {
    "132729": (.14, .09, .92, .76),
    "132750": (.12, .12, .83, .81),
    "132757": (.15, .16, .85, .75),
    "132815": (0.0, .045, 1.0, .76),
    "132845": (.24, .17, .71, .83),
    "132950": (.27, .18, .74, .78),
}


def main():
    source = LAB / "incoming"
    images = DATA / "images"
    labels = DATA / "labels"
    images.mkdir(parents=True, exist_ok=True)
    labels.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(17, 10))
    report = []
    for code, ax in zip(BOXES, axes.flat):
        path = source / f"IMG_20261017_{code}.jpg"
        frame = cv2.imread(str(path))
        if frame is None:
            raise RuntimeError(path)
        h, w = frame.shape[:2]
        box = BOXES[code]
        shutil.copy2(path, images / path.name)
        x1,y1,x2,y2 = box
        (labels / f"{path.stem}.txt").write_text(
            f"0 {(x1+x2)/2:.6f} {(y1+y2)/2:.6f} {x2-x1:.6f} {y2-y1:.6f}\n",
            encoding="ascii")
        report.append({"filename": path.name, "x1":x1, "y1":y1, "x2":x2, "y2":y2,
                       "review_status": "assistant_full_image_review"})
        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ax.plot([x1*w,x2*w,x2*w,x1*w,x1*w],
                [y1*h,y1*h,y2*h,y2*h,y1*h], color="red", linewidth=2)
        ax.set_title(code)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(DATA / "label_review_private.png", dpi=140)
    plt.close(fig)
    with (DATA / "labels_review.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(report[0]))
        writer.writeheader()
        writer.writerows(report)
    (DATA / "dataset.yaml").write_text(
        f"path: {DATA.as_posix()}\ntrain: images\nval: images\nnames:\n  0: receipt_region\n",
        encoding="utf-8")
    print("External scene: 6 labeled photos, no training")


if __name__ == "__main__":
    main()
