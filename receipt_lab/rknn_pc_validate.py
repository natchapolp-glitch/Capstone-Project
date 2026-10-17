"""RK3588-targeted conversion and PC-side RKNN simulator smoke test.

Run on Linux x86_64 with official rknn-toolkit2. It does not measure NPU speed.
"""

import json
import sys
import traceback
from pathlib import Path

import cv2
import numpy as np


WIN_LAB = Path("/mnt/c/Users/NATCHAPOL/SeminarLab")
WEIGHTS = WIN_LAB / "yolo_expanded/runs/receipt_region_v8n/weights"
ONNX = WEIGHTS / "best.onnx"
OUT = Path.home() / "SeminarLab/rknn"
RKNN_FILE = OUT / "receipt_region_v8n_float_rk3588.rknn"
STATUS = OUT / "pc_sdk_validation.json"


def main():
    result = {
        "target_platform": "rk3588",
        "host": "WSL Linux x86_64 PC",
        "model": str(ONNX),
        "rknn_file": str(RKNN_FILE),
        "quantization": "disabled (float build)",
        "steps": [],
        "note": "PC-side RKNN Toolkit2 simulator, no board or NPU performance measurement.",
    }
    rknn = None
    try:
        from rknn.api import RKNN

        import importlib.metadata
        result["rknn_toolkit2_version"] = importlib.metadata.version("rknn-toolkit2")
        result["steps"].append("import_ok")
        rknn = RKNN(verbose=False)
        assert rknn.config(mean_values=[[0, 0, 0]],
                           std_values=[[255, 255, 255]],
                           target_platform="rk3588",
                           disable_rules=["seperate_conv_rs_split"]) == 0
        result["steps"].append("config_ok")
        assert rknn.load_onnx(model=str(ONNX)) == 0
        result["steps"].append("onnx_loaded")
        assert rknn.build(do_quantization=False) == 0
        result["steps"].append("rknn_built")
        assert rknn.export_rknn(str(RKNN_FILE)) == 0
        result["steps"].append("rknn_exported")
        assert rknn.init_runtime() == 0
        result["steps"].append("pc_simulator_initialized")
        images = sorted((WIN_LAB / "yolo_expanded/val/images").glob("*.jpg"))
        image = cv2.imread(str(images[0]))
        assert image is not None
        rgb = cv2.cvtColor(cv2.resize(image, (320, 320)), cv2.COLOR_BGR2RGB)
        output = rknn.inference(inputs=[np.expand_dims(rgb, 0)],
                                data_format=["nhwc"])
        if output is None:
            raise RuntimeError("rknn.inference returned None")
        result["steps"].append("pc_simulator_inference_ok")
        result["output_shapes"] = [list(a.shape) for a in output]
        result["all_output_finite"] = all(bool(np.isfinite(a).all()) for a in output)
        import onnxruntime as ort
        session = ort.InferenceSession(str(ONNX), providers=["CPUExecutionProvider"])
        onnx_input = np.transpose(rgb.astype(np.float32) / 255.0,
                                  (2, 0, 1))[None, ...]
        reference = session.run(None, {session.get_inputs()[0].name: onnx_input})
        if len(output) == len(reference) and all(a.shape == b.shape for a, b in zip(output, reference)):
            result["onnx_vs_rknn_max_abs_diff"] = round(float(max(
                np.max(np.abs(a-b)) for a, b in zip(output, reference))), 6)
            result["onnx_vs_rknn_mean_abs_diff"] = round(float(np.mean(
                [np.mean(np.abs(a-b)) for a, b in zip(output, reference)])), 6)
            result["steps"].append("onnx_output_compared")
        result["status"] = "success"
    except Exception as error:
        result["status"] = "failed"
        result["error_type"] = type(error).__name__
        result["error"] = str(error)
        result["traceback"] = traceback.format_exc()
    finally:
        if rknn is not None:
            rknn.release()
        OUT.mkdir(parents=True, exist_ok=True)
        STATUS.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in result.items() if k != "traceback"},
                         ensure_ascii=False, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
