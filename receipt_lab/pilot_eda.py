"""Describe the curated 20-photo pilot without exposing document contents."""

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LAB = Path.home() / "SeminarLab"


def stats(values):
    return {"min": round(min(values), 2), "median": round(median(values), 2),
            "max": round(max(values), 2), "mean": round(mean(values), 2)}


def main():
    with (LAB / "reports" / "manifest.csv").open(encoding="utf-8-sig", newline="") as stream:
        manifest = {row["doc_id"]: row for row in csv.DictReader(stream)}
    with (LAB / "reports" / "pilot_itemized_20.csv").open(encoding="utf-8-sig", newline="") as stream:
        pilot = list(csv.DictReader(stream))
    if len(pilot) != 20 or len({row["doc_id"] for row in pilot}) != 20:
        raise RuntimeError("Pilot must have 20 unique photo IDs")
    rows = [manifest[row["doc_id"]] for row in pilot]
    brightness = [float(row["brightness_0_255"]) for row in rows]
    contrast = [float(row["contrast_0_255"]) for row in rows]
    resolution = [float(row["megapixels"]) for row in rows]
    orientation = Counter("portrait" if int(row["height"]) > int(row["width"])
                          else "landscape" for row in rows)
    result = {
        "n_photos": len(pilot),
        "store_counts": dict(Counter(row["store_or_source"] for row in pilot)),
        "page_form_counts": dict(Counter(row["page_form"] for row in pilot)),
        "orientation_counts": dict(orientation),
        "brightness_0_255": stats(brightness),
        "contrast_0_255": stats(contrast),
        "resolution_megapixels": stats(resolution),
        "faded_print_marked": sum(row["condition"] == "faded_print" for row in rows),
        "note": "Whole-image statistics on the curated photos; no perspective-skew or text-density claim.",
    }
    out = LAB / "reports"
    (out / "pilot_eda_20.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
    axes[0].bar(result["store_counts"].keys(), result["store_counts"].values())
    axes[0].set(title="Store mix", ylabel="Photos")
    axes[0].tick_params(axis="x", labelrotation=20)
    axes[1].hist(brightness, bins=8, edgecolor="white")
    axes[1].set(title="Whole-image brightness", xlabel="Mean gray value (0-255)")
    axes[2].bar(["One page", "Two pages"], [
        result["page_form_counts"].get("single_page", 0),
        result["page_form_counts"].get("two_pages_one_photo", 0),
    ])
    axes[2].set(title="Pages visible per photo", ylabel="Photos")
    fig.tight_layout()
    fig.savefig(out / "pilot_eda_20.png", dpi=170)
    plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
