"""Review all ten held-out detections and benchmark PC predict calls."""

import json
import time
from pathlib import Path
from statistics import median

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from ultralytics import YOLO


DATA = Path.home() / "SeminarLab" / "yolo_expanded"
WEIGHTS = DATA / "runs" / "receipt_region_v8n" / "weights" / "best.pt"


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    overlap = max(0, x2-x1) * max(0, y2-y1)
    area_a = (a[2]-a[0])*(a[3]-a[1])
    area_b = (b[2]-b[0])*(b[3]-b[1])
    return overlap/(area_a+area_b-overlap) if area_a+area_b > overlap else 0


def main():
    torch.set_num_threads(6)
    model = YOLO(str(WEIGHTS))
    paths = sorted((DATA / "val" / "images").glob("*.jpg"))
    assert len(paths) == 10
    fig, axes = plt.subplots(2, 5, figsize=(20, 12))
    records, all_times = [], []
    for ax, path in zip(axes.flat, paths):
        frame = cv2.imread(str(path))
        h, w = frame.shape[:2]
        values = (DATA / "val" / "labels" / f"{path.stem}.txt").read_text().split()
        cx, cy, bw, bh = map(float, values[1:])
        gt = [(cx-bw/2)*w, (cy-bh/2)*h, (cx+bw/2)*w, (cy+bh/2)*h]
        model.predict(str(path), imgsz=320, device="cpu", conf=.25, verbose=False)
        times = []
        for _ in range(3):
            start = time.perf_counter()
            prediction = model.predict(str(path), imgsz=320, device="cpu",
                                       conf=.25, verbose=False)[0]
            times.append((time.perf_counter()-start)*1000)
        all_times.extend(times)
        boxes = prediction.boxes.xyxy.cpu().numpy().tolist()
        scores = prediction.boxes.conf.cpu().numpy().tolist()
        best = max(((iou(gt, box), box, score) for box, score in zip(boxes, scores)),
                   default=(0, None, None), key=lambda entry: entry[0])
        records.append({"doc_id": path.stem, "detections_at_conf_0_25": len(boxes),
                        "best_iou": round(best[0], 4),
                        "best_confidence": round(best[2], 4) if best[2] is not None else None,
                        "median_predict_call_ms": round(median(times), 2)})
        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        for box, color in ((gt, "lime"), (best[1], "red")):
            if box:
                x1, y1, x2, y2 = box
                ax.plot([x1,x2,x2,x1,x1], [y1,y1,y2,y2,y1], color=color, linewidth=2)
        ax.set_title(f"{path.stem[-6:]} IoU {best[0]:.2f}", fontsize=9)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(DATA / "validation_predictions.png", dpi=130)
    plt.close(fig)
    result = {
        "validation_photos": records,
        "median_predict_call_ms_30_runs": round(median(all_times), 2),
        "count_iou_at_least_0_5_at_conf_0_25": sum(r["best_iou"] >= .5 for r in records),
        "timing_definition": "Windows PC CPU, YOLO.predict end-to-end, image read/preprocess/inference/postprocess; 3 warm repetitions per held-out photo.",
        "note": "Same capture background and assistant-reviewed labels; not RK3588 NPU latency.",
    }
    (DATA / "prediction_review.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
