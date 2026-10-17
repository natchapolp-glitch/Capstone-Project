from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from .common import LAB, REPO, WORK, Measurement, digest, read_json, utc, write_json
from .dataset import MANIFEST


def wsl_path(path):
    path = Path(path).resolve()
    return "/mnt/" + path.drive[0].lower() + path.as_posix()[2:]


def prepare_image(row, mode="reference", detector=None, rotation=None):
    from PIL import Image
    im = Image.open(row["source"]).convert("RGB")
    direction = rotation if rotation is not None else row["rotation_to_read"]
    already_rotated = False
    box = None
    if mode == "reference":
        if len(row["original_pixel_boxes"]) != 1:
            raise ValueError("Single-region runner needs exactly one reviewed region; complex photos need region composition")
        box = row["original_pixel_boxes"][0]
    elif mode == "predicted":
        if detector is None:
            from ultralytics import YOLO
            detector = YOLO(str(LAB / "yolo_expanded/runs/receipt_region_v8n/weights/best.pt"))
        import numpy as np
        if direction == "cw":
            im = im.transpose(Image.Transpose.ROTATE_270)
        elif direction == "ccw":
            im = im.transpose(Image.Transpose.ROTATE_90)
        elif direction != "none":
            raise ValueError("Unknown rotation")
        already_rotated = True
        result = detector.predict(np.array(im)[:, :, ::-1], imgsz=320, conf=0.25, device="cpu", verbose=False)[0]
        if not len(result.boxes):
            raise ValueError("No document detection; no fallback to reference crop")
        best = int(result.boxes.conf.argmax())
        upright_box = result.boxes.xyxy[best].tolist()
        x0, y0, x1, y1 = upright_box
        width, height = row["width"], row["height"]
        box = [y0, height-x1, y1, height-x0] if direction == "cw" else [width-y1, x0, width-y0, x1] if direction == "ccw" else upright_box
        im = im.crop(tuple(round(v) for v in upright_box))
    elif mode != "full":
        raise ValueError("Unknown crop mode")
    if box and not already_rotated:
        im = im.crop(tuple(round(v) for v in box))
    if direction == "cw" and not already_rotated:
        im = im.transpose(Image.Transpose.ROTATE_270)
    elif direction == "ccw" and not already_rotated:
        im = im.transpose(Image.Transpose.ROTATE_90)
    elif direction not in {"none", "cw", "ccw"}:
        raise ValueError("Rotation must be none, cw or ccw")
    target = WORK / "crops" / f"{row['doc_id']}-{mode}-{direction}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    im.save(target)
    return target, {"crop_mode": mode, "box_original_pixels": box, "rotation": direction,
                    "rotation_provenance": "manual metadata (oracle orientation); not an automatic orientation model",
                    "detection_frame": "after operator-selected rotation" if mode == "predicted" else None,
                    "source_sha256": row["sha256"], "crop_sha256": digest(target)}


class OCREngine:
    def __init__(self, engine):
        self.engine = engine
        if engine == "easyocr":
            import torch
            torch.set_num_threads(6)
            import easyocr
            with Measurement() as measured:
                self.reader = easyocr.Reader(["th", "en"], gpu=False, verbose=False,
                       model_storage_directory=str(LAB / "models/easyocr"), download_enabled=False)
            self.load_measurement = measured.result
            self.version = easyocr.__version__
        elif engine == "tesseract":
            self.load_measurement = None
            self.version = subprocess.check_output(["wsl", "-d", "Ubuntu", "--exec", "tesseract", "--version"], text=True).splitlines()[0]
        else:
            raise ValueError("Unknown OCR engine")

    def run(self, image, timeout=120):
        image = Path(image)
        if self.engine == "easyocr":
            with Measurement() as m:
                detected = self.reader.readtext(str(image), detail=1, paragraph=False, canvas_size=1600)
            lines = [{"box": [[float(v) for v in p] for p in box], "text": text,
                      "confidence": float(conf)} for box, text, conf in detected]
            # Preserve engine reading order, fixed in the preregistered config.
            result = {"status": "ok", "lines": lines, "text": "\n".join(x["text"] for x in lines), **m.result}
        else:
            command = ["wsl", "-d", "Ubuntu", "--exec", "python3", wsl_path(REPO / "receipt_lab/preboard/wsl_tesseract.py")]
            p = subprocess.run(command, input=json.dumps({"image": wsl_path(image), "psm": 3, "timeout": timeout}),
                               text=True, encoding="utf-8", capture_output=True, timeout=timeout+20)
            if p.returncode:
                raise RuntimeError(p.stderr[-1000:])
            result = json.loads(p.stdout)
        return {"engine": self.engine, "version": self.version, "languages": ["th", "en"], "cpu_thread_limit": 6,
                "input_sha256": digest(image), "timestamp": utc(), **result}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["easyocr", "tesseract"], required=True)
    ap.add_argument("--doc-id", action="append", required=True)
    ap.add_argument("--crop", choices=["reference", "predicted", "full"], default="reference")
    args = ap.parse_args()
    rows = {r["doc_id"]: r for r in read_json(MANIFEST)["records"]}
    engine = OCREngine(args.engine)
    for doc_id in args.doc_id:
        image, crop = prepare_image(rows[doc_id], args.crop)
        result = engine.run(image)
        result.update({"doc_id": doc_id, "crop": crop, "scope": "engineering run, not scored until truth is independently adjudicated"})
        write_json(WORK / "ocr" / args.engine / f"{doc_id}-{args.crop}.json", result)
        print(doc_id, args.engine, result["status"], round(result["wall_seconds"], 3), len(result["text"]), flush=True)


if __name__ == "__main__":
    main()
