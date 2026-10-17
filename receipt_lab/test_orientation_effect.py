"""Paired rotation check with frozen YOLO weights and transformed boxes.

This is a small sensitivity test, not an independent model test or proof that
rotation alone caused the difference between the original photo batches.
"""

import json
import shutil
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO


LAB = Path.home() / "SeminarLab"
BASE = LAB / "orientation_effect"
WEIGHTS = LAB / "yolo_expanded/runs/receipt_region_v8n/weights/best.pt"
VAL = LAB / "yolo_expanded/val"
EXTERNAL = LAB / "external_scene_6"
SIDEWAYS_VAL = {"R1C26C140E415", "RC0CFE64586A9", "RF96D447DC21E"}


def transform_label(line, direction):
    cls, cx, cy, w, h = line.split()
    cx, cy, w, h = map(float, (cx, cy, w, h))
    if direction == "cw":
        vals = (1 - cy, cx, h, w)
    elif direction == "ccw":
        vals = (cy, 1 - cx, h, w)
    else:
        vals = (cx, cy, w, h)
    return cls + " " + " ".join(f"{v:.6f}" for v in vals) + "\n"


def prepare(name, source, files, direction):
    root = BASE / name
    img_dir, label_dir = root / "images", root / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)
    for path in files:
        target = img_dir / path.name
        if direction is None:
            shutil.copy2(path, target)
        else:
            frame = cv2.imread(str(path))
            code = cv2.ROTATE_90_CLOCKWISE if direction == "cw" else cv2.ROTATE_90_COUNTERCLOCKWISE
            if not cv2.imwrite(str(target), cv2.rotate(frame, code)):
                raise RuntimeError(target)
        original_label = (source / "labels" / f"{path.stem}.txt").read_text(encoding="ascii")
        label_dir.joinpath(f"{path.stem}.txt").write_text(
            "".join(transform_label(line, direction) for line in original_label.splitlines() if line.strip()),
            encoding="ascii",
        )
    yaml_path = root / "dataset.yaml"
    yaml_path.write_text(f"path: {root.as_posix()}\ntrain: images\nval: images\nnames:\n  0: receipt_region\n", encoding="utf-8")
    return yaml_path


def main():
    torch.set_num_threads(6)
    model = YOLO(str(WEIGHTS))
    upright = [p for p in sorted((VAL / "images").glob("*.jpg")) if p.stem not in SIDEWAYS_VAL]
    external = sorted((EXTERNAL / "images").glob("*.jpg"))
    assert len(upright) == 7 and len(external) == 6
    specs = [
        ("same_upright_7", VAL, upright, None),
        ("same_rotated_7", VAL, upright, "cw"),
        ("later_original_6", EXTERNAL, external, None),
        ("later_uprighted_6", EXTERNAL, external, "ccw"),
    ]
    results = {}
    for name, source, files, rotation in specs:
        yaml_path = prepare(name, source, files, rotation)
        metric = model.val(
            data=str(yaml_path), imgsz=320, batch=1, device="cpu", workers=0,
            plots=False, project=str(BASE), name="metric_" + name,
            exist_ok=True, verbose=False,
        )
        results[name] = {
            "n": len(files), "mAP50": round(float(metric.box.map50), 4),
            "mAP50_95": round(float(metric.box.map), 4),
            "rotation": rotation or "original",
        }
        print(name, results[name], flush=True)
    results["interpretation"] = (
        "Paired 90-degree rotation changes only image orientation and matching boxes. "
        "The seven-photo comparison estimates orientation sensitivity on selected same-scene photos. "
        "The six-photo corrected comparison is exploratory; it cannot isolate the full cause "
        "of the between-batch gap. Small samples and assistant-reviewed labels remain limitations."
    )
    (BASE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
