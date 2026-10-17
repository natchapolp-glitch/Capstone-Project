"""Propose paper boxes on the 11 single-page pilot photos for manual review."""

import csv
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


LAB = Path.home() / "SeminarLab"
OUT = LAB / "reports" / "yolo_box_review"
OUT.mkdir(parents=True, exist_ok=True)


def propose(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    low_saturation = cv2.inRange(hsv, (0, 0, 75), (44, 150, 255))
    opening = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
    low_saturation = cv2.morphologyEx(low_saturation, cv2.MORPH_OPEN, opening)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    mask = cv2.morphologyEx(low_saturation, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No low-saturation region found")
    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)
    if w * h < image.shape[0] * image.shape[1] * 0.10:
        raise ValueError("Largest paper candidate is too small")
    return x, y, x + w, y + h


def main():
    with (LAB / "reports" / "pilot_itemized_20.csv").open(encoding="utf-8-sig", newline="") as stream:
        pilot = [row for row in csv.DictReader(stream) if row["page_form"] == "single_page"]
    assert len(pilot) == 11
    fig, axes = plt.subplots(3, 4, figsize=(14, 15))
    rows = []
    for ax, row in zip(axes.flat, pilot):
        image = cv2.imread(str(LAB / "incoming" / row["filename"]))
        if image is None:
            raise RuntimeError(row["filename"])
        x1, y1, x2, y2 = propose(image)
        rows.append({"doc_id": row["doc_id"], "filename": row["filename"],
                     "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                     "width": image.shape[1], "height": image.shape[0],
                     "review_status": "candidate_unreviewed"})
        preview = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ax.imshow(preview)
        ax.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], color="red", linewidth=2)
        ax.set_title(row["filename"].replace("S__", ""), fontsize=10)
        ax.axis("off")
    for ax in axes.flat[len(pilot):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "contact_sheet.png", dpi=140)
    plt.close(fig)
    with (OUT / "candidates.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Proposed {len(rows)} boxes; review {OUT / 'contact_sheet.png'} before training")


if __name__ == "__main__":
    main()
