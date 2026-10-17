"""Aggregate image-level EDA of purchase candidates; exports no receipt pixels."""

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LAB = Path.home() / "SeminarLab"
REPORTS = LAB / "reports"


def stats(values):
    return {"min": round(min(values), 2), "median": round(median(values), 2),
            "max": round(max(values), 2), "mean": round(mean(values), 2)}


def main():
    with (REPORTS / "manifest.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream)
                if not row["duplicate_of"] and row["doc_type"] == "itemized_purchase"]
    assert len(rows) == 53 and len({row["sha256"] for row in rows}) == 53
    brightness = [float(row["brightness_0_255"]) for row in rows]
    contrast = [float(row["contrast_0_255"]) for row in rows]
    resolution = [float(row["megapixels"]) for row in rows]
    media = Counter("handwritten" if row["condition"] == "handwritten" else "printed"
                    for row in rows)
    orientation = Counter("portrait" if int(row["height"]) > int(row["width"])
                          else "landscape" for row in rows)
    result = {
        "n_photo_candidates": len(rows),
        "medium_counts": dict(media),
        "store_counts": dict(Counter(row["store_or_source"] or "handwritten/unspecified"
                                     for row in rows)),
        "orientation_counts": dict(orientation),
        "brightness_0_255": stats(brightness),
        "contrast_0_255": stats(contrast),
        "resolution_megapixels": stats(resolution),
        "faded_print_marked": sum(row["condition"] == "faded_print" for row in rows),
        "note": "Photo-level candidate review, not independent transaction count or human-verified ground truth. Brightness and contrast are whole-image proxies, not receipt crops.",
    }
    (REPORTS / "eda_itemized_53.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    axes[0].bar(media.keys(), media.values(), color=["#3677ad", "#dc8c44"])
    axes[0].set(title="Document medium", ylabel="Photos")
    axes[1].hist(brightness, bins=10, color="#3677ad", edgecolor="white")
    axes[1].set(title="Whole-image brightness", xlabel="Mean gray value (0-255)")
    axes[2].bar(orientation.keys(), orientation.values(), color="#529e76")
    axes[2].set(title="Photo orientation", ylabel="Photos")
    fig.suptitle("53 itemized-purchase photo candidates (visual review)")
    fig.tight_layout()
    fig.savefig(REPORTS / "eda_itemized_53.png", dpi=170)
    plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
