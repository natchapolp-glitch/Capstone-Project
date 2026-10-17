"""Executed inside WSL. resource reports the actual Linux child, not Windows client RSS."""
import csv
import io
import json
import resource
import subprocess
import sys
import time
import os

request = json.load(sys.stdin)
os.environ['OMP_THREAD_LIMIT'] = '6'
start = time.perf_counter()
try:
    result = subprocess.run(["tesseract", request["image"], "stdout", "-l", "tha+eng", "--psm", str(request.get("psm", 3)), "tsv"],
                            capture_output=True, text=True, timeout=request.get("timeout", 120))
    groups = {}
    for r in csv.DictReader(io.StringIO(result.stdout), delimiter="\t"):
        if r.get("text", "").strip():
            key = tuple(r[k] for k in ["page_num", "block_num", "par_num", "line_num"])
            groups.setdefault(key, []).append(r)
    lines = [{"text": " ".join(w["text"] for w in words), "words": words} for words in groups.values()]
    output = {"status": "ok" if result.returncode == 0 else "failed", "lines": lines,
              "text": "\n".join(r["text"] for r in lines), "stderr": result.stderr,
              "exit_code": result.returncode}
except subprocess.TimeoutExpired:
    output = {"status": "timeout", "lines": [], "text": "", "stderr": "Tesseract timeout"}
output.update({"wall_seconds": time.perf_counter()-start,
               "child_peak_rss_bytes": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
               "memory_metric": "Linux RUSAGE_CHILDREN maxrss for Tesseract child (KiB converted to bytes)"})
print(json.dumps(output, ensure_ascii=True))
