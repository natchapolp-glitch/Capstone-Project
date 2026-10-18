"""Resumable LLM matrix. Engineering runs never become accuracy results."""
import argparse
import itertools
import json
import random
import uuid
from pathlib import Path

from json_extraction_scorer import failed_result, score
from .common import REPO, WORK, digest, environment, object_hash, read_json, utc, write_json
from .dataset import MANIFEST, validate, fingerprints
from .llm import LocalLLM
from .field_metrics import field_metrics
from .assets import require_registry


def checked_ocr_run(folder, rows, split):
    folder=Path(folder)
    manifest=read_json(folder/'manifest.json')
    completion=read_json(folder/'completion.json')
    if manifest.get('purpose')!='scored_ocr_evaluation' or manifest.get('split')!=split or not completion.get('complete') or not completion.get('accuracy_scored'):
        raise ValueError('Use a completed scored OCR run from the same split')
    if manifest.get('asset_registry_sha256')!=require_registry():raise ValueError('OCR runtime assets changed after benchmark')
    wanted=fingerprints(rows)
    if any(manifest.get('dataset_snapshot',{}).get(doc)!=value for doc,value in wanted.items()):
        raise ValueError('OCR evidence does not match the checked input records/truth')
    return folder


def inputs(doc_ids, split, engineering, engine, crop, ocr_run=None):
    data = read_json(MANIFEST)
    rows = [r for r in data["records"] if (not doc_ids or r["doc_id"] in doc_ids)
            and (engineering or r["split"] == split) and (not engineering or not r.get('challenge_candidate'))]
    if not engineering:
        errors = validate({**data, "records": rows}, require_review=True)
        if errors:
            raise ValueError("Dataset not ready: "+"; ".join(errors))
        if not rows:
            raise ValueError("No adjudicated records in the requested split")
        if ocr_run is None:
            raise ValueError('Specify --ocr-run pointing to the completed benchmark; mutable OCR cache is not scored evidence')
        ocr_run=checked_ocr_run(ocr_run,rows,split)
    result = []
    for row in rows:
        doc = row["doc_id"]
        ocr_path = Path(ocr_run)/'attempts'/f'{doc}-{engine}-{crop}-r0.json' if ocr_run else WORK / "ocr" / engine / f"{doc}-{crop}.json"
        ocr = read_json(ocr_path)
        if not engineering:
            truth_path = WORK / "annotations/adjudicated" / f"{doc}.json"
            truth = read_json(truth_path)
            result.append({"doc_id": doc, "source_kind": "reference", "text": truth["transcript"],
                           "truth": truth["extraction"], "truth_sha256": digest(truth_path), "transaction_group_id": row["transaction_group_id"]})
        result.append({"doc_id": doc, "source_kind": engine, "text": ocr["text"],
                       "truth": None if engineering else truth["extraction"],
                       "truth_sha256": None if engineering else digest(truth_path),
                       "ocr_input_sha256": ocr.get("input_sha256"), "source_status": ocr["status"],
                       "source_evidence_sha256": digest(ocr_path), "transaction_group_id": row["transaction_group_id"]})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc-id", action="append")
    ap.add_argument("--split", choices=["development", "evaluation", "challenge"], default="development")
    ap.add_argument("--engineering", action="store_true")
    ap.add_argument("--engine", choices=["easyocr", "tesseract"], default="tesseract")
    ap.add_argument("--crop", choices=["reference", "predicted"], default="reference")
    ap.add_argument("--ocr-run", type=Path)
    ap.add_argument("--repetitions", type=int, default=3)
    ap.add_argument("--run-id")
    args = ap.parse_args()
    if args.repetitions < 1:
        ap.error("repetitions must be positive")
    if not args.engineering and args.split != "development":
        selection = WORK / "selection.json"
        if not selection.exists():
            ap.error("Freeze OCR/config selection using development data before evaluation/challenge")
        chosen = read_json(selection)
        if chosen.get("engine") != args.engine or not chosen.get("frozen_at") or not chosen.get("development_evidence_sha256"):
            ap.error("Missing or mismatched frozen development selection")
        for key,path in [('model_registry_sha256',WORK/'model_registry.json'),('scorer_sha256',REPO/'json_extraction_scorer.py'),('schema_sha256',REPO/'receipt_schema.json'),('llm_driver_sha256',REPO/'receipt_lab/preboard/llm.py')]:
            if chosen.get(key)!=digest(path):ap.error('Frozen development version changed: '+key)
    samples = inputs(args.doc_id, args.split, args.engineering, args.engine, args.crop, args.ocr_run)
    if not samples:
        ap.error("No inputs")
    registry = read_json(WORK/"model_registry.json")
    run_id = args.run_id or ("engineering-" if args.engineering else "evaluation-")+uuid.uuid4().hex[:12]
    folder = WORK / "runs" / run_id
    manifest = {"run_id": run_id, "created_at": utc(), "purpose": "engineering_only_no_accuracy_claim" if args.engineering else "scored_evaluation",
                "dataset_sha256": digest(MANIFEST), "schema_sha256": digest(REPO/"receipt_schema.json"),
                "environment": environment(), "matrix": {"models": [m["id"] for m in registry["models"]],
                "grammar": [True, False], "sources": sorted({s["source_kind"] for s in samples}),
                "repetitions": args.repetitions, "doc_ids": sorted({s["doc_id"] for s in samples})},
                "expected_attempts": len(samples)*len(registry["models"])*2*args.repetitions,
                "normalization": "raw response; no JSON repair", "selection_sha256": digest(WORK/"selection.json") if (WORK/"selection.json").exists() else None}
    manifest["model_registry_sha256"] = digest(WORK/"model_registry.json")
    manifest['asset_registry_sha256']=require_registry() if not args.engineering else None
    manifest['scorer_sha256']=digest(REPO/'json_extraction_scorer.py')
    manifest['driver_sha256']={name:digest(REPO/'receipt_lab/preboard'/name) for name in ['experiment.py','llm.py','field_metrics.py']}
    manifest["split"] = args.split
    manifest["dataset_snapshot"] = fingerprints([r for r in read_json(MANIFEST)["records"] if r["doc_id"] in {s["doc_id"] for s in samples}])
    manifest["input_samples"] = [{"doc_id": s["doc_id"], "source_kind": s["source_kind"],
                                  "text_sha256": object_hash(s["text"]), "truth_sha256": s.get("truth_sha256"),
                                  "source_status": s.get("source_status", "ok"),
                                  "source_evidence_sha256": s.get("source_evidence_sha256")} for s in samples]
    if (folder/"manifest.json").exists():
        old = read_json(folder/"manifest.json")
        for k in ["dataset_snapshot", "schema_sha256", "matrix", "purpose", "selection_sha256", "input_samples", "model_registry_sha256", "split", "scorer_sha256", "driver_sha256", "asset_registry_sha256"]:
            if old[k] != manifest[k]:
                raise ValueError("Cannot resume with changed inputs/config")
        manifest = old
    else:
        write_json(folder/"manifest.json", manifest)
    rng = random.Random(20261018)
    models = registry["models"].copy(); rng.shuffle(models)
    session=folder/'sessions'/uuid.uuid4().hex
    for info in models:
        model_jobs = list(itertools.product(samples, [True, False], range(args.repetitions)))
        rng.shuffle(model_jobs)
        def attempt_path(sample,grammar,rep):
            return folder/'attempts'/f"{sample['doc_id']}-{sample['source_kind']}-{info['id']}-{'grammar' if grammar else 'free'}-r{rep}.json"
        if all(attempt_path(*job).exists() for job in model_jobs):
            continue
        with LocalLLM(info["id"]) as llm:
            write_json(session/f"load-{info['id']}.json", llm.load)
            # Warm-up excluded from reported attempts; actual, separately retained response.
            warmup = llm.extract("RECEIPT\nSHOP SAMPLE\nMilk 1 20.00\nTOTAL 20.00 THB", grammar=True)
            write_json(session/f"warmup-{info['id']}.json", {"synthetic": True, "included_in_metrics": False, **warmup})
            for sample, grammar, rep in model_jobs:
                key = f"{sample['doc_id']}-{sample['source_kind']}-{info['id']}-{'grammar' if grammar else 'free'}-r{rep}"
                path = folder/"attempts"/f"{key}.json"
                if path.exists():
                    continue
                result = llm.extract(sample["text"], grammar=grammar)
                result.update({"attempt_key": key, "doc_id": sample["doc_id"], "transaction_group_id": sample["transaction_group_id"],
                               "source_kind": sample["source_kind"], "repetition": rep, "truth_sha256": sample.get("truth_sha256"),
                               "purpose": manifest["purpose"], "accuracy_scored": sample["truth"] is not None})
                result["upstream_status"] = sample.get("source_status", "ok")
                if result["upstream_status"] != "ok":
                    result["model_request_status"] = result["status"]
                    result["status"] = "upstream_ocr_failed"
                if sample["truth"] is not None:
                    result["score"] = score(sample["truth"], result["parsed_output"]) if result["parse_valid"] else failed_result(0, ["raw output parse failed"])
                    if result["status"] != "ok":
                        result["score"] = failed_result(int(result["parse_valid"]), [result["status"]])
                    result['fields']=field_metrics(sample['truth'],result['parsed_output'] if result['status']=='ok' and result['parse_valid'] else None)
                write_json(path, result)
                print(key, result["status"], result["schema_valid"], round(result["measurement"]["wall_seconds"], 2), flush=True)
    attempts = [read_json(p) for p in (folder/"attempts").glob("*.json")]
    expected_keys = {f"{sample['doc_id']}-{sample['source_kind']}-{model['id']}-{'grammar' if grammar else 'free'}-r{rep}"
                     for sample, model, grammar, rep in itertools.product(samples, registry["models"], [True, False], range(args.repetitions))}
    actual_keys = [a["attempt_key"] for a in attempts]
    write_json(folder/"completion.json", {"expected": manifest["expected_attempts"], "actual": len(attempts),
                "complete": set(actual_keys)==expected_keys and len(actual_keys)==len(set(actual_keys)),
                "missing_attempts": sorted(expected_keys-set(actual_keys)), "unexpected_attempts": sorted(set(actual_keys)-expected_keys),
                "failed_requests": sum(a["status"]!="ok" for a in attempts),
                "schema_valid": sum(a["schema_valid"] for a in attempts), "accuracy_scored": sum(a["accuracy_scored"] for a in attempts)})
    print(folder, flush=True)


if __name__ == "__main__":
    main()
