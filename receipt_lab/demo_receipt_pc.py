"""Local PC demonstration of the 38-photo receipt-region pilot model."""

from argparse import ArgumentParser
from pathlib import Path
import cv2
from ultralytics import YOLO

PRIVATE = Path.home() / "SeminarLab"
WEIGHTS = PRIVATE / "yolo_expanded" / "runs" / "receipt_region_v8n" / "weights" / "best.pt"
EXAMPLE = PRIVATE / "yolo_expanded" / "val" / "images" / "R4F4EA934251E.jpg"
OUTPUT = PRIVATE / "demo_output" / "receipt_detection.jpg"

parser = ArgumentParser(description="Run the e-Eye YOLOv8n pilot on one local image")
parser.add_argument("--image", type=Path, default=EXAMPLE, help="Local image chosen for presentation")
parser.add_argument("--weights", type=Path, default=WEIGHTS)
parser.add_argument("--output", type=Path, default=OUTPUT)
parser.add_argument("--conf", type=float, default=0.8, help="Display confidence threshold")
parser.add_argument("--show", action="store_true", help="Open the result in a local window")
args = parser.parse_args()

if not args.image.is_file():
    raise SystemExit(f"Input image not found: {args.image}")
if not args.weights.is_file():
    raise SystemExit(f"Model weights not found: {args.weights}")

model = YOLO(str(args.weights))
result = model.predict(source=str(args.image), imgsz=320, conf=args.conf, device="cpu", verbose=False)[0]
args.output.parent.mkdir(parents=True, exist_ok=True)
if not cv2.imwrite(str(args.output), result.plot()):
    raise SystemExit(f"Could not save result: {args.output}")

print(f"Detected boxes: {len(result.boxes)}")
print(f"Confidence threshold: {args.conf:.2f}")
for i, b in enumerate(result.boxes, 1):
    xyxy = [round(float(x), 1) for x in b.xyxy[0]]
    print(f"{i}: confidence={float(b.conf[0]):.3f} box_xyxy={xyxy}")
print(f"Annotated image saved locally: {args.output}")
print("This is a PC detector demonstration; it does not measure NPU performance.")

if args.show:
    annotated = cv2.imread(str(args.output))
    cv2.imshow("e-Eye PC detector demo", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
