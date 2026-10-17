"""Evaluate frozen YOLO weights on six new receipts from a different scene."""

import json
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from ultralytics import YOLO


LAB = Path.home() / "SeminarLab"
DATA = LAB / "external_scene_6"
WEIGHTS = LAB / "yolo_expanded/runs/receipt_region_v8n/weights/best.pt"


def iou(a, b):
    x1, y1 = max(a[0],b[0]), max(a[1],b[1])
    x2, y2 = min(a[2],b[2]), min(a[3],b[3])
    intersection = max(0,x2-x1)*max(0,y2-y1)
    aa=(a[2]-a[0])*(a[3]-a[1]); ab=(b[2]-b[0])*(b[3]-b[1])
    return intersection/(aa+ab-intersection) if aa+ab>intersection else 0


def main():
    torch.set_num_threads(6)
    model = YOLO(str(WEIGHTS))
    metric = model.val(data=str(DATA / "dataset.yaml"), imgsz=320, batch=1,
                       device="cpu", workers=0, plots=False,
                       project=str(DATA), name="val_frozen", exist_ok=True,
                       verbose=False)
    fig, axes = plt.subplots(2,3,figsize=(17,10))
    records = []
    for ax,path in zip(axes.flat, sorted((DATA/"images").glob("*.jpg"))):
        frame=cv2.imread(str(path)); h,w=frame.shape[:2]
        values=(DATA/"labels"/f"{path.stem}.txt").read_text().split()
        cx,cy,bw,bh=map(float,values[1:])
        gt=[(cx-bw/2)*w,(cy-bh/2)*h,(cx+bw/2)*w,(cy+bh/2)*h]
        pred=model.predict(str(path),imgsz=320,device="cpu",conf=.25,verbose=False)[0]
        boxes=pred.boxes.xyxy.cpu().numpy().tolist()
        scores=pred.boxes.conf.cpu().numpy().tolist()
        best=max(((iou(gt,box),box,score) for box,score in zip(boxes,scores)),
                 default=(0,None,None),key=lambda item:item[0])
        top=max(zip(scores,boxes),default=(None,None),key=lambda item:item[0] or -1)
        records.append({"photo":path.name,"detections_conf_0_25":len(boxes),
                        "best_iou":round(best[0],4),
                        "top_confidence":round(top[0],4) if top[0] is not None else None,
                        "top_confidence_iou":round(iou(gt,top[1]),4) if top[1] is not None else 0})
        ax.imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        for box,color in ((gt,"lime"),(top[1],"red")):
            if box:
                x1,y1,x2,y2=box
                ax.plot([x1,x2,x2,x1,x1],[y1,y1,y2,y2,y1],color=color,linewidth=2)
        ax.set_title(f"{path.stem[-6:]} top IoU {records[-1]['top_confidence_iou']:.2f}")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(DATA/"prediction_review_private.png",dpi=140)
    plt.close(fig)
    report={
        "train_on_external_photos":False,
        "external_photos":6,
        "mAP50":float(metric.box.map50),
        "mAP50_95":float(metric.box.map),
        "precision":float(metric.box.mp),
        "recall":float(metric.box.mr),
        "top_confidence_iou_at_least_0_5":sum(r["top_confidence_iou"]>=.5 for r in records),
        "any_detection_iou_at_least_0_5_conf_0_25":sum(r["best_iou"]>=.5 for r in records),
        "records":records,
        "note":"Different counter/background, rotated wrinkled receipts; six assistant-labeled photos only. Not RK3588 NPU performance.",
    }
    (DATA/"external_results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
