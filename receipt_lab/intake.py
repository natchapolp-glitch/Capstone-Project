"""Inventory receipt photos and create a first EDA report without changing images."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps, ImageStat, UnidentifiedImageError

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pass


FIELDS = [
    "doc_id", "filename", "sha256", "width", "height", "megapixels",
    "brightness_0_255", "contrast_0_255", "bytes", "duplicate_of",
    "doc_type", "store_or_source", "lighting", "condition", "angle_note",
    "transcript_checked", "json_checked", "notes",
]
MANUAL_FIELDS = FIELDS[10:]
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def old_annotations(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    previous = {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            sha = row.get("sha256")
            if not sha:
                continue
            # Exact duplicate rows may carry blank manual fields. Keep the
            # most annotated copy instead of silently replacing it.
            score = sum(bool(row.get(field)) for field in MANUAL_FIELDS)
            if sha not in previous or score > sum(bool(previous[sha].get(field)) for field in MANUAL_FIELDS):
                previous[sha] = row
    return previous


def inspect(path: Path, base: Path) -> dict[str, object]:
    sha = digest(path)
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        width, height = image.size
        gray = ImageOps.grayscale(image)
        gray.thumbnail((512, 512))
        stat = ImageStat.Stat(gray)
    return {
        "doc_id": "R" + sha[:12].upper(),
        "filename": path.relative_to(base).as_posix(),
        "sha256": sha,
        "width": width,
        "height": height,
        "megapixels": round(width * height / 1_000_000, 3),
        "brightness_0_255": round(stat.mean[0], 1),
        "contrast_0_255": round(stat.stddev[0], 1),
        "bytes": path.stat().st_size,
        "duplicate_of": "",
    }


def chart(rows: list[dict[str, object]], out: Path) -> None:
    if not rows:
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    axes[0].hist([float(r["brightness_0_255"]) for r in rows], bins=10)
    axes[0].set(title="Image brightness", xlabel="Mean grayscale (0-255)", ylabel="Photos")
    axes[1].hist([float(r["megapixels"]) for r in rows], bins=10)
    axes[1].set(title="Image resolution", xlabel="Megapixels", ylabel="Photos")
    types = Counter(str(r.get("doc_type") or "Unclassified") for r in rows)
    axes[2].bar(types.keys(), types.values())
    axes[2].set(title="Document type", ylabel="Photos")
    axes[2].tick_params(axis="x", labelrotation=25)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def run(data_root: Path) -> dict[str, object]:
    incoming = data_root / "incoming"
    reports = data_root / "reports"
    incoming.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    manifest = reports / "manifest.csv"
    previous = old_annotations(manifest)
    rows: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    first_seen: dict[str, str] = {}
    for path in sorted(incoming.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            row = inspect(path, incoming)
        except (OSError, ValueError, UnidentifiedImageError) as exc:
            errors.append({"filename": path.relative_to(incoming).as_posix(), "error": str(exc)})
            continue
        sha = str(row["sha256"])
        row["duplicate_of"] = first_seen.get(sha, "")
        first_seen.setdefault(sha, str(row["filename"]))
        old = previous.get(sha, {})
        for field in MANUAL_FIELDS:
            row[field] = old.get(field, "")
        rows.append(row)

    with manifest.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "photos": len(rows),
        "unique_photos": len(first_seen),
        "duplicates": len(rows) - len(first_seen),
        "unreadable_photos": errors,
        "document_types": dict(Counter(str(row.get("doc_type") or "Unclassified") for row in rows)),
        "note": "Brightness and contrast are descriptive image statistics, not OCR or NPU results.",
    }
    (reports / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    chart(rows, reports / "eda.png")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path.home() / "SeminarLab")
    args = parser.parse_args()
    print(json.dumps(run(args.data_root), ensure_ascii=False, indent=2))
