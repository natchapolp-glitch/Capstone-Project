"""Create private contact sheets for every remaining unique, unclassified photo."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageOps


LAB = Path.home() / "SeminarLab"
OUT = LAB / "reports" / "classification_review"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with (LAB / "reports" / "manifest.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream)
                if not row["duplicate_of"] and not row["doc_type"]]
    for start in range(0, len(rows), 12):
        batch = rows[start:start+12]
        fig, axes = plt.subplots(3, 4, figsize=(15, 15))
        for ax, row in zip(axes.flat, batch):
            with Image.open(LAB / "incoming" / row["filename"]) as source:
                image = ImageOps.exif_transpose(source)
                ax.imshow(image)
            ax.set_title(row["filename"].replace("S__", ""), fontsize=12)
            ax.axis("off")
        for ax in axes.flat[len(batch):]:
            ax.axis("off")
        fig.tight_layout()
        fig.savefig(OUT / f"unclassified_{start//12+1:02d}.png", dpi=135)
        plt.close(fig)
    print(f"{len(rows)} unique unclassified photos across {(len(rows)+11)//12} sheets")


if __name__ == "__main__":
    main()
