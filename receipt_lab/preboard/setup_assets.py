"""Download pinned public weights/binaries, verify HF LFS hash, derive Q4 from Q8."""
import json
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

from .common import LAB, WORK, digest, environment, read_json, write_json

MODELS = [("0.6B", "23749fefcc72300e3a2ad315e1317431b06b590a"),
          ("1.7B", "90862c4b9d2787eaed51d12237eafdfe7c5f6077")]
LLAMA_TAG = "b11714"


def download(url, path, expected=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (not expected or digest(path) == expected):
        return
    part = path.with_suffix(path.suffix + ".part")
    with urllib.request.urlopen(url, timeout=90) as src, part.open("wb") as out:
        shutil.copyfileobj(src, out, length=1024 * 1024)
    if expected and digest(part) != expected:
        raise ValueError(f"Hash mismatch: {path.name}")
    part.replace(path)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    write_json(WORK / "environment_before_setup.json", environment())
    binary = LAB / "tools" / f"llama-{LLAMA_TAG}"
    archive = binary.with_suffix(".zip")
    url = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_TAG}/llama-{LLAMA_TAG}-bin-win-cpu-x64.zip"
    download(url, archive)
    binary.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        z.extractall(binary)
    print("llama binary ready", binary, flush=True)
    entries = []
    for size, revision in MODELS:
        repo = f"Qwen/Qwen3-{size}-GGUF"
        name = f"Qwen3-{size}-Q8_0.gguf"
        metadata = json.load(urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true", timeout=30))
        info = next(x for x in metadata["siblings"] if x["rfilename"] == name)
        expected = info["lfs"]["sha256"]
        q8 = LAB / "models" / "llm" / name
        needed = (0 if q8.exists() else info["size"]) + info["size"] * 0.8
        if shutil.disk_usage(LAB).free - needed < 8 * 2**30:
            raise RuntimeError("Download/quantization would leave less than 8 GiB free")
        source = f"https://huggingface.co/{repo}/resolve/{revision}/{name}"
        print("downloading", name, info["size"], flush=True)
        download(source, q8, expected)
        write_json(q8.with_suffix(".source.json"), {"repo": repo, "revision": revision,
                   "source_url": source, "license": metadata.get("cardData", {}).get("license"),
                   "sha256": expected, "bytes": q8.stat().st_size})
        quantizer = next(binary.rglob("llama-quantize.exe"))
        q4 = q8.with_name(name.replace("Q8_0", "Q4_K_M"))
        if not q4.exists():
            log = WORK / f"quantize-{size}.log"
            with log.open("wb") as out:
                subprocess.run([str(quantizer), "--allow-requantize", str(q8), str(q4), "Q4_K_M"],
                               stdout=out, stderr=subprocess.STDOUT, check=True)
        for quant, path in [("Q8_0", q8), ("Q4_K_M", q4)]:
            entries.append({"id": f"qwen3-{size}-{quant}", "repo": repo, "revision": revision,
                            "license": "apache-2.0", "path": str(path), "quantization": quant,
                            "sha256": digest(path), "bytes": path.stat().st_size,
                            "quantization_source": "publisher Q8_0" if quant == "Q8_0" else "local requantization from publisher Q8_0, not original FP16"})
        write_json(WORK / "model_registry.json", {"llama_tag": LLAMA_TAG, "binary_dir": str(binary),
                   "binary_archive_sha256": digest(archive), "models": entries})
        print("ready", size, flush=True)


if __name__ == "__main__":
    main()
