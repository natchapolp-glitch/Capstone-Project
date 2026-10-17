"""Train and validate the larger PC-only receipt-region feasibility detector."""

import csv
import json
from pathlib import Path

import torch
from ultralytics import YOLO


LAB = Path.home() / "SeminarLab"
DATA = LAB / "yolo_expanded"


def main():
    torch.set_num_threads(6)
    weights = DATA / "runs" / "receipt_region_v8n" / "weights" / "best.pt"
    if not weights.exists():
        model = YOLO("yolov8n.pt")
        model.train(
            data=str(DATA / "dataset.yaml"),
            epochs=15, imgsz=320, batch=4, device="cpu", workers=0,
            seed=42, deterministic=True, patience=7, plots=False,
            project=str(DATA / "runs"), name="receipt_region_v8n", exist_ok=True,
            verbose=False,
        )
    with (weights.parents[1] / "results.csv").open(encoding="utf-8", newline="") as stream:
        epoch_rows = list(csv.DictReader(stream))
    trained = YOLO(str(weights))
    metrics = trained.val(
        data=str(DATA / "dataset.yaml"), imgsz=320, batch=1,
        device="cpu", workers=0, plots=False,
        project=str(DATA / "runs"), name="val_receipt_region_v8n", exist_ok=True,
        verbose=False,
    )
    output = {
        "model": "YOLOv8n fine-tuned",
        "ultralytics_version": __import__("ultralytics").__version__,
        "torch_version": torch.__version__,
        "device": "PC CPU",
        "image_size": 320,
        "train_photos": 38,
        "validation_photos": 10,
        "epochs_requested": 15,
        "epochs_completed": len(epoch_rows),
        "mAP50": float(metrics.box.map50),
        "mAP50_95": float(metrics.box.map),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "weights": str(weights),
        "note": "Same capture setting, assistant-reviewed labels; preliminary PC-only result, not RK3588 NPU or generalization performance.",
    }
    (DATA / "expanded_metrics.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
