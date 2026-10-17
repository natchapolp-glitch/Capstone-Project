"""Reproducible exploratory line-skew audit for the fixed 10+6 photos.

Image-projection estimates are diagnostic measurements, not annotated angles.
They should be checked visually, especially on handwriting and folded receipts.
"""

import json
import statistics
from pathlib import Path

import cv2
import numpy as np

LAB = Path.home() / "SeminarLab"
ROOT = LAB / "reports" / "projection_skew_16"
SOURCES = [("first_validation", LAB / "yolo_expanded" / "val"),
           ("later_holdout", LAB / "external_scene_6")]
SIDEWAYS_VAL = {"R1C26C140E415", "RC0CFE64586A9", "RF96D447DC21E"}


def crop_receipt(frame, label_path):
    _, cx, cy, w, h = label_path.read_text(encoding="ascii").splitlines()[0].split()
    cx, cy, w, h = map(float, (cx, cy, w, h))
    ih, iw = frame.shape[:2]
    x0, y0 = max(0, round((cx-w/2)*iw)), max(0, round((cy-h/2)*ih))
    x1, y1 = min(iw, round((cx+w/2)*iw)), min(ih, round((cy+h/2)*ih))
    return frame[y0:y1, x0:x1]


def score_mask(gray):
    h, w = gray.shape
    scale = min(1, 850 / max(h, w))
    if scale < 1:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    # Adaptive threshold preserves faint thermal print better than a global cut.
    ink = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 31, 12)
    # Remove tiny isolated specks, and broad image-border shadows.
    ink[:5, :] = 0
    ink[-5:, :] = 0
    ink[:, :5] = 0
    ink[:, -5:] = 0
    return ink


def orientation(ink):
    h, w = ink.shape
    matrix_center = (w / 2, h / 2)
    candidates = []
    for angle in np.arange(-12, 12.01, 0.25):
        matrix = cv2.getRotationMatrix2D(matrix_center, float(angle), 1)
        rotated = cv2.warpAffine(ink, matrix, (w, h), flags=cv2.INTER_NEAREST,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # Square of each row's dark-pixel count favors aligned text baselines.
        row = (rotated > 0).sum(axis=1).astype(float)
        score = float(np.square(row).sum() / max(1, row.sum()**2))
        candidates.append((round(float(angle), 2), score))
    best = max(candidates, key=lambda item: item[1])
    no_rotation = next(score for angle, score in candidates if angle == 0)
    return best, no_rotation, candidates


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for group, source in SOURCES:
        for path in sorted((source / "images").glob("*.jpg")):
            frame = cv2.imread(str(path))
            crop = crop_receipt(frame, source / "labels" / (path.stem + ".txt"))
            sideways = group == "later_holdout" or path.stem in SIDEWAYS_VAL
            if sideways:
                direction = (cv2.ROTATE_90_COUNTERCLOCKWISE if group == "later_holdout"
                             else cv2.ROTATE_90_CLOCKWISE)
                crop = cv2.rotate(crop, direction)
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            ink = score_mask(gray)
            best, score0, scores = orientation(ink)
            row = {"group": group, "photo": path.name, "quarter_turn_corrected": sideways,
                   "rotation_to_align_text_deg": best[0],
                   "score_improvement_vs_0_pct": round((best[1]/score0-1)*100, 2),
                   "raw_scores": scores}
            rows.append(row)
            cv2.imwrite(str(ROOT / (path.stem + "_upright_crop.jpg")), crop)
            print(group, path.name, best[0], row["score_improvement_vs_0_pct"], flush=True)
    (ROOT / "raw_results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    for group in ("first_validation", "later_holdout"):
        vals = [abs(r["rotation_to_align_text_deg"]) for r in rows if r["group"] == group]
        print(group, "median_absolute_deg", statistics.median(vals), flush=True)


if __name__ == "__main__":
    main()
