"""Paired OCR benchmark, preserving failures and requiring checked truths for scores."""
import argparse
import json
import random
import uuid

from .common import REPO, WORK, digest, environment, read_json, utc, write_json
from .dataset import MANIFEST, validate, fingerprints
from .metrics import ocr_metric, summarize
from .ocr import OCREngine, prepare_image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engineering", action="store_true")
    ap.add_argument("--doc-id", action="append")
    ap.add_argument("--split", choices=["development", "evaluation", "challenge"], default="development")
    ap.add_argument("--repetitions", type=int, default=3)
    ap.add_argument("--run-id")
    args = ap.parse_args()
    if args.repetitions < 1:
        ap.error("repetitions must be positive")
    data = read_json(MANIFEST)
    rows = [r for r in data["records"] if (not args.doc_id or r["doc_id"] in args.doc_id)
            and (args.engineering or r["split"] == args.split) and (not args.engineering or not r.get('challenge_candidate'))]
    if not rows:
        ap.error("No matching documents")
    if not args.engineering:
        errors = validate({**data, "records": rows}, require_review=True)
        if errors:
            ap.error("; ".join(errors))
    folder = WORK / "runs" / (args.run_id or "ocr-"+uuid.uuid4().hex[:12])
    manifest={"created_at": utc(), "purpose": "engineering_only_no_accuracy_claim" if args.engineering else "scored_ocr_evaluation",
               "environment": environment(), "dataset_sha256": digest(MANIFEST), "dataset_snapshot": fingerprints(rows), "split": args.split, "doc_ids": [r["doc_id"] for r in rows],
               "engines": ["easyocr", "tesseract"], "modes": ["reference", "predicted"], "repetitions": args.repetitions,
               "expected_attempts": len(rows)*2*2*args.repetitions, "orientation": "oracle metadata, not automatic orientation",
               "implementation_sha256": {name:digest(REPO/'receipt_lab/preboard'/name) for name in ['ocr.py','wsl_tesseract.py','metrics.py','benchmark_ocr.py']},
               "accuracy_repetitions": "Only repetition 0 enters accuracy summaries; repeats 1+ are timing samples"}
    if (folder/'manifest.json').exists():
        old=read_json(folder/'manifest.json')
        for key in ['purpose','dataset_snapshot','split','doc_ids','engines','modes','repetitions','implementation_sha256']:
            if old.get(key)!=manifest[key]:
                ap.error('Cannot resume changed data/config/code; preserve evidence and choose a new run ID')
    else:
        write_json(folder/'manifest.json',manifest)
    session=folder/'sessions'/uuid.uuid4().hex
    rng = random.Random(20261018)
    engines = ["easyocr", "tesseract"]; rng.shuffle(engines)
    for engine_name in engines:
        jobs = [(row, mode, rep) for row in rows for mode in ["reference", "predicted"] for rep in range(args.repetitions)]
        rng.shuffle(jobs)
        if all((folder/'attempts'/f"{r['doc_id']}-{engine_name}-{m}-r{rep}.json").exists() for r,m,rep in jobs):
            continue
        engine = OCREngine(engine_name)
        write_json(session/f"load-{engine_name}.json", {"measurement": engine.load_measurement, "version": engine.version})
        # Same warm-up region for both engines, separate from metrics.
        try:
            image, transform = prepare_image(rows[0], "reference")
            warmup=engine.run(image)
        except Exception as exc:
            warmup={'status':'failed','error':str(exc)}
        write_json(session/f"warmup-{engine_name}.json", {"included_in_metrics": False, **warmup})
        for row, mode, rep in jobs:
            doc_id = row["doc_id"]
            key = f"{doc_id}-{engine_name}-{mode}-r{rep}"
            path=folder/"attempts"/f"{key}.json"
            if path.exists():
                continue
            result = {"doc_id": doc_id, "engine": engine_name, "mode": mode, "repetition": rep,
                      "transaction_group_id": row["transaction_group_id"], "accuracy_scored": not args.engineering}
            try:
                image, transform = prepare_image(row, mode)
                result.update(engine.run(image))
                result["transform"] = transform
            except Exception as exc:
                result.update({"status": "failed", "error": str(exc), "text": ""})
            if not args.engineering:
                truth = read_json(WORK/"annotations/adjudicated"/f"{doc_id}.json")
                result["metric"] = ocr_metric(truth["transcript"], result["text"], result["status"])
            result["attempt_key"] = key
            write_json(path, result)
            # Publish fixed extraction input without masking failed attempts.
            if rep == 0:
                write_json(WORK/"ocr"/engine_name/f"{doc_id}-{mode}.json", result)
            print(key, result["status"], round(result.get("wall_seconds", 0), 2), flush=True)
    all_results=[read_json(p) for p in (folder/'attempts').glob('*.json')]
    summaries = {}
    if not args.engineering:
        for e in engines:
            for mode in ["reference", "predicted"]:
                summaries[e+"-"+mode] = summarize([r["metric"] for r in all_results if r["engine"]==e and r["mode"]==mode and r["repetition"]==0])
    expected = {f"{r['doc_id']}-{e}-{m}-r{rep}" for r in rows for e in engines for m in ["reference", "predicted"] for rep in range(args.repetitions)}
    actual = {r["attempt_key"] for r in all_results}
    write_json(folder/"completion.json", {"complete": actual==expected and len(all_results)==len(expected), "missing": sorted(expected-actual),
               "unexpected": sorted(actual-expected), "attempts": len(all_results), "failures": sum(r["status"]!="ok" for r in all_results),
               "accuracy_scored": not args.engineering, "summaries": summaries})
    print(folder,flush=True)


if __name__ == "__main__":
    main()
