"""Immutable independent entries and explicit adjudication; no AI attestation."""
import re
import uuid

from json_extraction_scorer import schema_errors
from .common import WORK, object_hash, read_json, utc, write_json
from .dataset import MANIFEST, annotations


def submit_human(doc_id, payload):
    data=read_json(MANIFEST)
    rows = {r["doc_id"]: r for r in data["records"]}
    if doc_id not in rows:
        raise ValueError("Unknown document")
    reviewer = payload.get("reviewer", "").strip()
    if len(reviewer) < 2 or payload.get("attestation") is not True:
        raise ValueError("A human reviewer name and explicit personal attestation are required")
    if not payload.get("transcript", "").strip() and not payload.get('unreadable_regions'):
        raise ValueError("Full transcript is required; mark unreadable regions explicitly")
    errors = schema_errors(payload.get("extraction"))
    if errors:
        raise ValueError("; ".join(errors))
    slot = payload.get("slot")
    if slot not in {"first", "second"}:
        raise ValueError("Choose first or independent second entry")
    if slot == 'second' and payload.get('model_assisted'):
        raise ValueError("Second pass must start blank and be read from the image, without the OCR draft")
    previous = annotations(doc_id)
    existing = next((r for r in previous if r["slot"] == slot), None)
    if existing:
        if existing["reviewer"] == reviewer and existing["transcript"] == payload["transcript"] and existing["extraction"] == payload["extraction"] and existing["unreadable_regions"] == payload.get("unreadable_regions", []):
            return {"saved": True, "entry_id": existing["entry_id"], "entries": len(previous), "already_saved": True}
        # Changed corrections are new immutable revisions; the old entry remains intact.
    # Owner explicitly works alone: blinded second entry by the same person
    # is permitted and reported as a single-reviewer limitation, never as two people.
    record = {"doc_id": doc_id, "source_sha256": rows[doc_id]["sha256"],
              "timestamp": utc(), "reviewer": reviewer, "reviewer_kind": "human",
              "attestation": True, "slot": slot, "transcript": payload["transcript"],
              "extraction": payload["extraction"], "unreadable_regions": payload.get("unreadable_regions", []),
              "note": payload.get("note", ""), "entry_id": uuid.uuid4().hex}
    record['model_assisted_first_entry'] = bool(payload.get('model_assisted'))
    record['draft_engine'] = payload.get('draft_engine')
    record['region_definition_sha256'] = object_hash({'boxes':rows[doc_id].get('original_pixel_boxes'),
                                                     'rotation':rows[doc_id].get('rotation_to_read')})
    record['transcript_lines']=line_records(doc_id,record['transcript'],len(rows[doc_id].get('original_pixel_boxes',[]))==1)
    record['entry_status'] = 'partial_unreadable' if record['unreadable_regions'] else 'human_transcribed'
    record['revision'] = existing.get('revision', 1)+1 if existing else 1
    record['supersedes_entry_id'] = existing['entry_id'] if existing else None
    write_json(WORK / "annotations/human" / doc_id / f"{slot}-{record['entry_id']}.json", record)
    current=[r for r in previous if r['slot']!=slot]+[record]
    rows[doc_id]['annotation_status']='partial_unreadable' if any(r['unreadable_regions'] for r in current) else 'human_transcribed'
    data['version']=data.get('version',0)+1
    write_json(MANIFEST,data)
    return {"saved": True, "entry_id": record["entry_id"], "entries": len(previous)+(0 if existing else 1), 'revision':record['revision']}


def adjudicate(doc_id, payload):
    evidence = annotations(doc_id)
    if len(evidence) != 2 or {r["slot"] for r in evidence} != {"first", "second"}:
        raise ValueError("Two human entries must exist before adjudication")
    if not payload.get("adjudicator", "").strip() or payload.get("attestation") is not True:
        raise ValueError("Human adjudicator attestation is required")
    extraction = payload["extraction"]
    errors = schema_errors(extraction)
    if errors:
        raise ValueError("; ".join(errors))
    if not payload.get("transcript", "").strip() or payload.get("unreadable_regions"):
        raise ValueError("Incomplete truth cannot be promoted to fully adjudicated")
    metadata = payload["metadata"]
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,80}", metadata.get("transaction_group_id", "")):
        raise ValueError("Reviewed transaction group ID required")
    if metadata.get("split") not in {"development", "evaluation", "challenge"}:
        raise ValueError("Reviewed split required")
    if len(metadata.get('original_pixel_boxes',[]))!=1:
        raise ValueError('Set one document region before both entries; complex photos remain excluded from this scored protocol')
    from .dataset import validate
    data = read_json(MANIFEST)
    row = next(r for r in data["records"] if r["doc_id"] == doc_id)
    if row.get('challenge_candidate'):
        conditions=row.get('capture_conditions',{})
        if metadata['split']!='challenge' or payload.get('new_scene_attestation') is not True or not isinstance(conditions,dict) or not all(isinstance(conditions.get(k),str) and conditions[k].strip() for k in ['device','lighting','background','capture_source']):
            raise ValueError('New-photo capture conditions and explicit owner confirmation are required')
        row['capture_conditions_status']='owner_confirmed'
    reviewed_scope = object_hash({'boxes':metadata['original_pixel_boxes'],'rotation':row['rotation_to_read']})
    if any(e.get('region_definition_sha256') is not None and e.get('region_definition_sha256') != reviewed_scope for e in evidence):
        raise ValueError('Crop/rotation differs from the two reviewed entries; review the same image scope before adjudication')
    for key in ["original_pixel_boxes", "transaction_group_id", "split"]:
        row[key] = metadata[key]
    row.update({"box_status": "reviewed", "group_status": "reviewed", "annotation_status": "adjudicated"})
    # Validate all structural constraints before writing the truth or manifest.
    temporary = {**data, "records": [{**r, "annotation_status": "draft_ai"} if r["doc_id"] == doc_id else r for r in data["records"]]}
    errors = validate(temporary, check_hashes=True)
    if errors:
        raise ValueError("; ".join(errors))
    truth = {"doc_id": doc_id, "source_sha256": row["sha256"], "timestamp": utc(),
             "adjudicator": payload["adjudicator"], "transcript": payload["transcript"],
             "extraction": extraction, "unreadable_regions": [],
             "review_record_hashes": [object_hash(e) for e in evidence], "note": payload.get("note", "")}
    truth["review_method"] = "single_reviewer_double_entry"
    truth['transcript_lines']=line_records(doc_id,truth['transcript'],True)
    if row.get('challenge_candidate'):
        truth['new_scene_attestation']=True
        truth['capture_conditions_sha256']=object_hash(row['capture_conditions'])
    truth['region_definition_sha256'] = reviewed_scope
    truth['legacy_entries_without_recorded_scope'] = [e['entry_id'] for e in evidence if e.get('region_definition_sha256') is None]
    truth['scope_confirmation'] = 'Human final adjudication confirms current displayed region; legacy entries retain their original immutable contents'
    target=WORK / "annotations/adjudicated" / f"{doc_id}.json"
    if target.exists():
        old=read_json(target)
        truth['supersedes_truth_sha256']=object_hash(old)
        write_json(WORK/'annotations/adjudication_history'/doc_id/(object_hash(old)+'.json'),old)
    write_json(target, truth)
    data["version"] += 1
    write_json(MANIFEST, data)
    return {"adjudicated": True, "doc_id": doc_id}


def line_records(doc_id,text,single_region):
    region=doc_id+(':region-1' if single_region else ':full-image-draft')
    return [{'region_id':region,'line_id':f'{region}:line-{i:04d}','text':line,
             'location_source':'human-provided reading order; no line-level pixel box'}
            for i,line in enumerate(text.splitlines(),1)]


def reconcile_statuses():
    """Migrate pending status labels from immutable human evidence, never create truth."""
    data=read_json(MANIFEST);changed=0
    for row in data['records']:
        entries=[e for e in annotations(row['doc_id']) if e.get('reviewer_kind')=='human' and e.get('attestation') is True and e.get('source_sha256')==row['sha256']]
        if not entries:continue
        target=WORK/'annotations/adjudicated'/f"{row['doc_id']}.json"
        if row['annotation_status']=='adjudicated' and len(entries)==2 and target.exists() and set(read_json(target).get('review_record_hashes',[]))=={object_hash(e) for e in entries}:
            continue
        status='partial_unreadable' if any(e['unreadable_regions'] for e in entries) else 'human_transcribed'
        if row['annotation_status']!=status:
            row['annotation_status']=status;changed+=1
    if changed:
        data['version']=data.get('version',0)+1;write_json(MANIFEST,data)
    return changed
