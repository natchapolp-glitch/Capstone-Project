"""Executed inside WSL. resource reports the actual Linux child, not Windows client RSS."""
import csv
import io
import json
import resource
import subprocess
import sys
import time
import os
import hashlib
from pathlib import Path
from tesseract_tsv import parse_tsv

request = json.load(sys.stdin)
os.environ['OMP_THREAD_LIMIT'] = '6'
start = time.perf_counter()
try:
    directory=request.get('tessdata_dir')
    for filename,expected in request.get('expected_assets',{}).items():
        if filename not in {'tha.traineddata','eng.traineddata'}:raise ValueError('Unexpected language asset')
        value=hashlib.sha256((Path(directory)/filename).read_bytes()).hexdigest()
        if value!=expected:raise ValueError('Tesseract language asset changed: '+filename)
    args=["tesseract",request['image'],'stdout']+(['--tessdata-dir',directory] if directory else [])
    result = subprocess.run(args+["-l", "tha+eng", "--psm", str(request.get("psm", 3)), "tsv"],
                            capture_output=True, text=True, timeout=request.get("timeout", 120))
    lines = parse_tsv(result.stdout)
    output = {"status": "ok" if result.returncode == 0 else "failed", "lines": lines,
              "text": "\n".join(r["text"] for r in lines), "stderr": result.stderr,
              "exit_code": result.returncode, "raw_tsv": result.stdout,
              "tsv_parser": "literal_quotes_v2"}
except subprocess.TimeoutExpired:
    output = {"status": "timeout", "lines": [], "text": "", "stderr": "Tesseract timeout"}
except (OSError,ValueError) as exc:
    output={'status':'failed','lines':[],'text':'','stderr':str(exc)}
output.update({"wall_seconds": time.perf_counter()-start,
               "child_peak_rss_bytes": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
               "memory_metric": "Linux RUSAGE_CHILDREN maxrss for Tesseract child (KiB converted to bytes)"})
print(json.dumps(output, ensure_ascii=True))
