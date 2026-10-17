from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAB = Path(os.environ.get("SEMINAR_LAB", str(Path.home() / "SeminarLab")))
WORK = LAB / "preboard"


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def object_hash(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


class Measurement:
    """Sample RSS of a process and descendants; this is not allocated VRAM."""

    def __init__(self, pid=None, interval=0.05):
        self.pid, self.interval = pid or os.getpid(), interval
        self.peak = 0
        self.samples = 0
        self.stop = threading.Event()

    def _sample(self):
        import psutil
        try:
            root = psutil.Process(self.pid)
            processes = [root] + root.children(recursive=True)
            total = 0
            for p in processes:
                try:
                    total += p.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            self.peak = max(self.peak, total)
            self.samples += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _loop(self):
        while not self.stop.wait(self.interval):
            self._sample()

    def __enter__(self):
        self.started = time.perf_counter()
        self._sample()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        self.thread.join()
        self._sample()
        self.result = {"wall_seconds": time.perf_counter() - self.started,
                       "sampled_peak_rss_bytes": self.peak, "rss_samples": self.samples,
                       "rss_interval_seconds": self.interval, "measured_pid": self.pid,
                       "memory_metric": "sampled process-tree RSS; shared pages may be counted twice"}


def environment():
    import importlib.metadata as md
    import psutil
    versions = {}
    for name in ["torch", "ultralytics", "easyocr", "psutil", "Pillow", "paho-mqtt"]:
        try:
            versions[name] = md.version(name)
        except md.PackageNotFoundError:
            versions[name] = None
    return {"timestamp": utc(), "python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "cpu": platform.processor(),
            "logical_cpu_count": os.cpu_count(), "physical_ram_bytes": psutil.virtual_memory().total,
            "free_disk_bytes": __import__("shutil").disk_usage(LAB).free,
            "packages": versions, "device": "PC CPU", "lab_root": str(LAB),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()}
