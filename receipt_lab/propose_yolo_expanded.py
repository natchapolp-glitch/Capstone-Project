"""Propose and visualize receipt-region boxes for all eligible purchase photos."""

import csv
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from detect_paper_candidates import propose
from make_yolo_pilot import BOXES as REVIEWED_FIRST_BOXES


LAB = Path.home() / "SeminarLab"
OUT = LAB / "reports" / "yolo_expanded_review"
OUT.mkdir(parents=True, exist_ok=True)
EXCLUDE_CODES = {200, 245, 246, 289, 293}


def code(filename):
    return int(filename.split("__")[1].split("_")[0][-3:])


def main():
    with (LAB / "reports" / "manifest.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream)
                if not row["duplicate_of"] and row["doc_type"] == "itemized_purchase"
                and code(row["filename"]) not in EXCLUDE_CODES]
    if len(rows) != 48:
        raise RuntimeError(f"Expected 48 candidate photos, got {len(rows)}")
    proposals = []
    for row in rows:
        image = cv2.imread(str(LAB / "incoming" / row["filename"]))
        h, w = image.shape[:2]
        source = "automatic_candidate"
        if row["filename"] in REVIEWED_FIRST_BOXES:
            box = REVIEWED_FIRST_BOXES[row["filename"]]
            source = "manual_reviewed_first_pilot"
        else:
            try:
                x1, y1, x2, y2 = propose(image)
                box = (x1/w, y1/h, x2/w, y2/h)
            except ValueError:
                box = (0.0, 0.0, 1.0, 1.0)
                source = "proposal_failed_full_frame_placeholder"
        proposals.append({"doc_id": row["doc_id"], "filename": row["filename"],
                          "x1": round(box[0], 4), "y1": round(box[1], 4),
                          "x2": round(box[2], 4), "y2": round(box[3], 4),
                          "source": source, "review_status": "needs_visual_review"})
    for start in range(0, len(proposals), 12):
        fig, axes = plt.subplots(3, 4, figsize=(15, 15))
        for ax, row in zip(axes.flat, proposals[start:start+12]):
            image = cv2.imread(str(LAB / "incoming" / row["filename"]))
            h, w = image.shape[:2]
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            x1, y1, x2, y2 = [float(row[k]) for k in ("x1", "y1", "x2", "y2")]
            ax.plot([x1*w,x2*w,x2*w,x1*w,x1*w], [y1*h,y1*h,y2*h,y2*h,y1*h],
                    color="red", linewidth=2)
            ax.set_title(row["filename"][3:11] + " " + row["source"][:1], fontsize=10)
            ax.axis("off")
        fig.tight_layout()
        fig.savefig(OUT / f"proposals_{start//12+1:02d}.png", dpi=140)
        plt.close(fig)
    with (OUT / "proposals.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(proposals[0]))
        writer.writeheader()
        writer.writerows(proposals)
    print(f"{len(proposals)} candidates; {sum(r['source']=='automatic_candidate' for r in proposals)} automatic")


if __name__ == "__main__":
    main()
