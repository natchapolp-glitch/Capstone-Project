"""Private visual sheet of newly added IMG_20261017 photos."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageOps


LAB = Path.home() / "SeminarLab"


def main():
    paths = sorted((LAB / "incoming").glob("IMG_20261017_*.jpg"))
    if len(paths) != 10:
        raise RuntimeError(f"Expected 10 new photos, got {len(paths)}")
    fig, axes = plt.subplots(2, 5, figsize=(20, 11))
    for path, ax in zip(paths, axes.flat):
        with Image.open(path) as photo:
            ax.imshow(ImageOps.exif_transpose(photo).convert("RGB"))
        ax.set_title(path.name, fontsize=10)
        ax.axis("off")
    fig.tight_layout()
    output = LAB / "reports/new_photos_10_private.png"
    fig.savefig(output, dpi=140)
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
