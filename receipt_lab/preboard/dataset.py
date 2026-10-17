"""Versioned draft audit and independent human annotations. No automatic promotion."""
import argparse
import csv
import itertools
import json
import re
from pathlib import Path

from .common import LAB, WORK, digest, object_hash, read_json, utc, write_json

MANIFEST = WORK / "dataset" / "manifest.json"


def dhash(path):
    from PIL import Image
    image = Image.open(path).convert("L").resize((9, 8))
    pixels = list(image.getdata())
    return sum((pixels[y * 9 + x] > pixels[y * 9 + x + 1]) << (y * 8 + x)
               for y in range(8) for x in range(8))


def initialize():
    if MANIFEST.exists():
        raise FileExistsError("Preserving existing manifest; use the reviewed version, do not reinitialize")
    source = LAB / "reports" / "manifest.csv"
    with source.open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if not r["duplicate_of"] and r["doc_type"] == "itemized_purchase"]
    orientations = {r["doc_id"]: r for r in read_json(LAB / "reports/orientation_skew_59/results.json")}
    roots = [LAB / "yolo_expanded" / s / "labels" for s in ["train", "val"]] + [LAB / "external_scene_6/labels"]
    labels = {p.stem: p for root in roots for p in root.glob("*.txt")}
    incoming = {p.name: p for p in (LAB / "incoming").rglob("*") if p.is_file()}
    records, hashes = [], {}
    for row in rows:
        doc_id = row["doc_id"]
        path = incoming[row["filename"]]
        actual_hash = digest(path)
        if actual_hash != row["sha256"]:
            raise ValueError(f"Source changed: {doc_id}")
        label = labels.get(doc_id) or labels.get(path.stem)
        width, height = int(row["width"]), int(row["height"])
        boxes = []
        if label:
            for line in label.read_text().splitlines():
                cls, x, y, w, h = map(float, line.split())
                boxes.append([max(0, (x-w/2)*width), max(0, (y-h/2)*height),
                              min(width, (x+w/2)*width), min(height, (y+h/2)*height)])
        previous = read_json(LAB / "language_truth_59/records" / f"{doc_id}.json")
        historical = "train" if (LAB / "yolo_expanded/train/labels" / f"{doc_id}.txt").exists() else "val" if (LAB / "yolo_expanded/val/labels" / f"{doc_id}.txt").exists() else "retrospective_external" if label else "excluded_complex"
        record = {"doc_id": doc_id, "source": str(path), "sha256": actual_hash,
                  "width": width, "height": height, "store": row["store_or_source"],
                  "condition": row["condition"], "doc_type": row["doc_type"],
                  "original_pixel_boxes": boxes, "box_status": "draft_ai" if boxes else "needs_multiregion_review",
                  "bbox_exclusion_reason": None if boxes else "Existing single-document protocol cannot represent complex photo; awaiting region review",
                  "rotation_to_read": orientations[doc_id]["rotation_to_read"],
                  "rotation_source": "previous assistant visual audit; not independently reviewed",
                  "historical_yolo_split": historical,
                  "transaction_group_id": None, "group_status": "unresolved",
                  "split": "unassigned", "annotation_status": "draft_ai",
                  "prior_item_name_status": previous["item_names_status"],
                  "prior_item_name_fragments": previous.get("item_names", []),
                  "notes": row["notes"]}
        records.append(record)
        hashes[doc_id] = dhash(path)
        write_json(WORK / "annotations/drafts" / f"{doc_id}.json", {
            "doc_id": doc_id, "source_sha256": actual_hash, "status": "draft_ai",
            "transcript": None, "extraction": None, "unreadable_regions": [],
            "note": "Prior item-name fragments are not a full transcript or JSON ground truth."})
    pairs = []
    for a, b in itertools.combinations(records, 2):
        distance = (hashes[a["doc_id"]] ^ hashes[b["doc_id"]]).bit_count()
        if distance <= 10:
            pairs.append({"a": a["doc_id"], "b": b["doc_id"], "dhash_distance": distance,
                          "decision": "unreviewed", "warning": "Visual similarity does not establish the same transaction"})
    output = {"version": 1, "created_at": utc(), "source_manifest_sha256": digest(source),
              "unit": "photo candidate, not independent transaction", "records": records}
    write_json(MANIFEST, output)
    write_json(WORK / "dataset/duplicate_candidates.json", sorted(pairs, key=lambda p: p["dhash_distance"]))
    return output


def annotations(doc_id, history=False):
    if not re.fullmatch(r"R[A-F0-9]{12}", doc_id):
        raise ValueError("Invalid document ID")
    folder = WORK / "annotations" / "human" / doc_id
    records = [read_json(p) for p in sorted(folder.glob("*.json"))] if folder.exists() else []
    if history:
        return records
    latest = {}
    for record in records:
        slot = record['slot']
        ordering = (record.get('revision', 1), record.get('timestamp', ''), record['entry_id'])
        if slot not in latest or ordering > latest[slot][0]:
            latest[slot] = (ordering, record)
    return [latest[s][1] for s in sorted(latest)]


def fingerprints(rows):
    """Only referenced records/truths invalidate a run, not unrelated new photos."""
    result = {}
    for row in rows:
        truth = WORK / "annotations/adjudicated" / f"{row['doc_id']}.json"
        result[row["doc_id"]] = object_hash({"record": row, "truth_sha256": digest(truth) if truth.exists() else None,
                                            "latest_review_entries": [object_hash(e) for e in annotations(row['doc_id'])]})
    return result


def validate(data, require_review=False, check_hashes=True):
    errors, seen, splits, sha_seen = [], set(), {}, set()
    from json_extraction_scorer import schema_errors
    for row in data["records"]:
        doc = row["doc_id"]
        if doc in seen:
            errors.append(f"{doc}: duplicate ID")
        seen.add(doc)
        path = Path(row["source"])
        if not path.is_file():
            errors.append(f"{doc}: missing source image")
        elif check_hashes and digest(path) != row["sha256"]:
            errors.append(f"{doc}: source hash mismatch")
        if row["sha256"] in sha_seen:
            errors.append(f"{doc}: duplicate source SHA")
        sha_seen.add(row["sha256"])
        for box in row["original_pixel_boxes"]:
            if len(box) != 4 or not (0 <= box[0] < box[2] <= row["width"] and 0 <= box[1] < box[3] <= row["height"]):
                errors.append(f"{doc}: invalid original-coordinate bbox")
        if not row["original_pixel_boxes"] and not row.get("bbox_exclusion_reason"):
            errors.append(f"{doc}: no bbox or exclusion reason")
        split, group = row["split"], row["transaction_group_id"]
        if split not in {"unassigned", "development", "evaluation", "challenge", "excluded"}:
            errors.append(f"{doc}: unknown split")
        if group and split not in {"unassigned", "excluded"}:
            if group in splits and splits[group] != split:
                errors.append(f"{doc}: transaction leakage: {group}")
            splits[group] = split
        verified = row["annotation_status"] == "adjudicated"
        if require_review or verified:
            if not verified:
                errors.append(f"{doc}: not adjudicated")
                continue
            evidence = annotations(doc)
            reviewers = {r.get("reviewer") for r in evidence if r.get("attestation") is True and r.get("reviewer_kind") == "human" and r.get("source_sha256") == row["sha256"] and r.get("timestamp")}
            valid_entries = [r for r in evidence if r.get("attestation") is True and r.get("reviewer_kind") == "human" and r.get("source_sha256") == row["sha256"] and r.get("timestamp") and r.get("reviewer")]
            if {r.get('slot') for r in valid_entries} != {"first", "second"}:
                errors.append(f"{doc}: missing two human entry rounds (single reviewer allowed by owner)")
            target = WORK / "annotations/adjudicated" / f"{doc}.json"
            if not target.exists():
                errors.append(f"{doc}: missing adjudication file")
            else:
                truth = read_json(target)
                if truth.get('source_sha256') != row['sha256'] or truth.get('doc_id') != doc:
                    errors.append(f'{doc}: adjudicated source identity mismatch')
                if row.get('challenge_candidate') and (truth.get('new_scene_attestation') is not True or row.get('capture_conditions_status')!='owner_confirmed' or truth.get('capture_conditions_sha256')!=object_hash(row.get('capture_conditions'))):
                    errors.append(f'{doc}: new-photo provenance not confirmed by owner')
                if len(row['original_pixel_boxes'])!=1:
                    errors.append(f'{doc}: single-region scored protocol cannot use a complex/unconfigured image')
                errors += [f"{doc}: {e}" for e in schema_errors(truth.get("extraction"))]
                if truth.get("unreadable_regions") or not truth.get("transcript"):
                    errors.append(f"{doc}: incomplete full-document truth")
                if len(truth.get("review_record_hashes", [])) != 2 or not set(truth["review_record_hashes"]) <= {object_hash(e) for e in evidence}:
                    errors.append(f"{doc}: missing or stale adjudication review evidence")
                scope = object_hash({'boxes':row['original_pixel_boxes'],'rotation':row['rotation_to_read']})
                legacy_ids = {e['entry_id'] for e in valid_entries if e.get('region_definition_sha256') is None}
                if legacy_ids != set(truth.get('legacy_entries_without_recorded_scope', [])):
                    errors.append(f'{doc}: legacy review scope not disclosed at adjudication')
                if truth.get('region_definition_sha256') != scope or any(e.get('region_definition_sha256') is not None and e.get('region_definition_sha256') != scope for e in valid_entries):
                    errors.append(f'{doc}: transcript scope differs from current OCR region/rotation')
            if row["group_status"] != "reviewed" or not group:
                errors.append(f"{doc}: unresolved transaction grouping")
            if row["box_status"] != "reviewed":
                errors.append(f"{doc}: unreviewed regions")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["init", "validate"])
    ap.add_argument("--require-reviewed", action="store_true")
    args = ap.parse_args()
    data = initialize() if args.command == "init" else read_json(MANIFEST)
    errors = validate(data, args.require_reviewed)
    result = {"photo_candidates": len(data["records"]), "errors": errors,
              "status_counts": {s: sum(r["annotation_status"] == s for r in data["records"])
                                for s in sorted({r["annotation_status"] for r in data["records"]})},
              "adjudicated_transactions": len({r["transaction_group_id"] for r in data["records"] if r["annotation_status"] == "adjudicated" and r["transaction_group_id"]}),
              "manifest_sha256": digest(MANIFEST)}
    write_json(WORK / "dataset/validation.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
