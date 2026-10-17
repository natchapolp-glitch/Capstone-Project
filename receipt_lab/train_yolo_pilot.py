"""Fine-tune a receipt-page detector as a small PC-only feasibility pilot."""

import json
from pathlib import Path

import torch
from ultralytics import YOLO


LAB = Path.home() / "SeminarLab"
DATA = LAB / "yolo_pilot"


def main():
    torch.set_num_threads(6)
    model = YOLO("yolov8n.pt")
    model.train(
        data=str(DATA / "dataset.yaml"),
        epochs=12, imgsz=320, batch=4, device="cpu", workers=0,
        seed=42, deterministic=True, patience=6, plots=False,
        project=str(DATA / "runs"), name="receipt_page_v8n", exist_ok=True,
        verbose=False,
    )
    weights = DATA / "runs" / "receipt_page_v8n" / "weights" / "best.pt"
    trained = YOLO(str(weights))
    metrics = trained.val(
        data=str(DATA / "dataset.yaml"), imgsz=320, batch=1,
        device="cpu", workers=0, plots=False,
        project=str(DATA / "runs"), name="val_receipt_page_v8n", exist_ok=True,
        verbose=False,
    )
    output = {
        "model": "YOLOv8n fine-tuned",
        "software": "Ultralytics",
        "ultralytics_version": __import__("ultralytics").__version__,
        "device": "PC CPU",
        "image_size": 320,
        "train_photos": 8,
        "validation_photos": 3,
        "epochs_requested": 12,
        "mAP50": float(metrics.box.map50),
        "mAP50_95": float(metrics.box.map),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "weights": str(weights),
        "note": "Tiny same-background feasibility pilot; not a generalization or RK3588 NPU result.",
    }
    (DATA / "pilot_metrics.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
