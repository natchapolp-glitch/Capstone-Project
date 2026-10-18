"""Owner-authorized single-pass text references; never promote skipped JSON to truth.

Freeze the latest saved first entries and both existing OCR outputs before scoring.
This is a descriptive comparison on the existing photos, not a held-out evaluation.
"""
import argparse
import re
from collections import Counter

from .common import REPO, WORK, digest, object_hash, read_json, utc, write_json
from .dataset import MANIFEST, annotations
from .metrics import ocr_metric, summarize

POLICY = {
    'review_method': 'single_reviewer_single_pass',
    'reference_scope': 'human_supplied_transcript_only',
    'structured_json_status': 'unreviewed_not_scorable',
    'second_pass_required': False,
    'text_normalization': 'Remove only numeric [cite: N] annotation markers from both strings, then NFC/whitespace normalization. Raw entries remain unchanged.',
    'authority': 'Owner explicitly requested one pass using the entries just submitted; structured fields mostly skipped.',
}


def scoring_text(text):
    return re.sub(r'\[cite:\s*\d+\s*\]', '', text, flags=re.I)


def eligible(row, entry):
    reasons = []
    if entry.get('reviewer_kind') != 'human' or entry.get('attestation') is not True:
        reasons.append('missing_human_attestation')
    if entry.get('source_sha256') != row['sha256']:
        reasons.append('source_mismatch')
    text = scoring_text(entry.get('transcript', ''))
    if not text.strip():
        reasons.append('empty_transcript')
    if entry.get('unreadable_regions'):
        reasons.append('explicit_partial_unreadable')
    if re.search(r'อ่านไม่ชัด|อ่านไม่ออก|อ่านไม่ได้|ไม่สามารถอ่าน|\[(?:[^\]]*ไม่ชัด|[^\]]*ไม่ทราบ)[^\]]*\]', entry.get('transcript', '')):
        reasons.append('in_text_uncertainty_marker')
    if re.search(r'\[(?:cite:|ลายเซ็น|เอกสาร|บิลใบ)', text, re.I):
        reasons.append('annotation_markup_not_literal_receipt_text')
    if any(line.count('|') >= 3 for line in entry.get('transcript', '').splitlines()):
        reasons.append('reformatted_table_not_literal_reading_order')
    if re.search(r'\d{3,}\.\.\.', entry.get('transcript', '')):
        reasons.append('abbreviated_numeric_text')
    audit_path = REPO/'experiments/preboard/reference_quality_audit.json'
    if audit_path.exists():
        for audit in read_json(audit_path)['records']:
            if (audit['doc_id'] == row['doc_id'] and audit['source_sha256'] == row['sha256']
                    and audit['entry_sha256'] == object_hash(entry)):
                reasons.extend(audit['exclusion_reasons'])
    scope = object_hash({'boxes': row.get('original_pixel_boxes'), 'rotation': row.get('rotation_to_read')})
    if entry.get('region_definition_sha256') != scope:
        reasons.append('unverified_or_changed_display_scope')
    return reasons


def freeze(folder, tesseract_run='draft-tesseract-all59-v2'):
    target = folder / 'snapshot.json'
    if target.exists():
        return read_json(target)
    records, missing = [], []
    data = read_json(MANIFEST)
    for row in data['records']:
        entry = next((e for e in annotations(row['doc_id']) if e['slot'] == 'first'), None)
        if entry is None:
            missing.append(row['doc_id'])
            continue
        if digest(row['source']) != row['sha256']:
            raise ValueError('Source bytes changed: ' + row['doc_id'])
        reasons = eligible(row, entry)
        mode = 'reference' if len(row.get('original_pixel_boxes', [])) == 1 else 'full'
        # Recreate precisely the view presented to the owner and verify old OCR input.
        from .ocr import prepare_image
        _, transform = prepare_image(row, mode)
        predictions = {}
        for engine in ['easyocr', 'tesseract']:
            run = tesseract_run if engine == 'tesseract' else 'draft-easyocr-all59-v1'
            path = WORK / 'runs' / run / 'attempts' / (row['doc_id']+'.json')
            if not path.exists():
                predictions[engine] = {'status': 'missing', 'text': '', 'scope_matches': False}
                continue
            output = read_json(path)
            old = output.get('transform', {})
            matches = (old.get('source_sha256') == row['sha256']
                       and old.get('crop_sha256') == transform['crop_sha256']
                       and output.get('input_sha256') == transform['crop_sha256'])
            predictions[engine] = {'status': output['status'], 'text': output.get('text', ''),
                                   'scope_matches': matches, 'evidence_sha256': digest(path),
                                   'input_sha256': output.get('input_sha256')}
        records.append({'doc_id': row['doc_id'], 'row': row, 'entry': entry,
                        'entry_sha256': object_hash(entry), 'exclusion_reasons': reasons,
                        'crop_mode': mode, 'display_transform': transform, 'predictions': predictions,
                        'structured_json_status': POLICY['structured_json_status']})
    snapshot = {'created_at': utc(), 'policy': POLICY, 'manifest_sha256': digest(MANIFEST), 'tesseract_run': tesseract_run,
                'candidate_photos': len(data['records']), 'missing_doc_ids': missing, 'records': records}
    write_json(target, snapshot)
    return snapshot


def evaluate(folder):
    snapshot = freeze(folder)
    rows = []
    for record in snapshot['records']:
        entry = record['entry']
        # Both engines use exactly the same denominator. Partial references stay visible.
        reasons = record['exclusion_reasons'][:]
        if not all(p['scope_matches'] for p in record['predictions'].values()):
            reasons.append('missing_or_mismatched_ocr_input')
        result = {'doc_id': record['doc_id'], 'entry_sha256': record['entry_sha256'],
                  'transcript_sha256': object_hash(entry['transcript']),
                  'model_assisted': entry.get('model_assisted_first_entry', False),
                  'crop_mode': record['crop_mode'], 'exclusion_reasons': reasons,
                  'structured_accuracy': None, 'metrics': {}}
        if not reasons:
            for engine, output in record['predictions'].items():
                result['metrics'][engine] = ocr_metric(scoring_text(entry['transcript']), scoring_text(output['text']), output['status'])
        result['ocr_evidence_sha256'] = {e: p.get('evidence_sha256') for e, p in record['predictions'].items()}
        rows.append(result)
    included = [r for r in rows if not r['exclusion_reasons']]
    cohorts = {
        'all_eligible': included,
        'without_declared_ocr_assistance': [r for r in included if not r['model_assisted']],
        'declared_ocr_assistance': [r for r in included if r['model_assisted']],
        'single_document_crop': [r for r in included if r['crop_mode'] == 'reference'],
        'complex_full_image': [r for r in included if r['crop_mode'] == 'full'],
    }
    report = {'created_at': utc(), 'purpose': 'descriptive_ocr_against_single_pass_owner_text',
              'valid_for_reporting': True, 'reference_completeness_certified': False,
              'policy': POLICY, 'snapshot_sha256': digest(folder / 'snapshot.json'),
              'evaluator_sha256': digest(__file__),
              'candidate_photos': snapshot['candidate_photos'], 'saved_photos': len(rows),
              'missing_doc_ids': snapshot['missing_doc_ids'], 'scorable_photos': len(included),
              'excluded_photos': len(rows) - len(included),
              'declared_assisted_photos': sum(r['model_assisted'] for r in rows),
              'exclusion_reason_counts': dict(Counter(reason for r in rows for reason in r['exclusion_reasons'])),
              'structured_json_accuracy': None,
              'summaries': {name: {engine: summarize([r['metrics'][engine] for r in group])
                                  for engine in ['easyocr', 'tesseract']} for name, group in cohorts.items()},
              'limitations': [
                  'One reviewer, one pass; reference transcription errors remain possible.',
                  'Automatic uncertainty/formatting flags and one visual scope spot-check do not certify completeness of unflagged references.',
                  'Assistance flag is self-reported; unflagged entries are not proven independent.',
                  'Existing OCR outputs were available during annotation: exploratory comparison, not held-out accuracy.',
                  'Photographs are not verified distinct transactions; no transaction-level confidence interval.',
                  'Reference crops/rotation are previous operator metadata, not newly human-verified detection labels.',
                  'CER counts Unicode code points after NFC and whitespace normalization, including line breaks; may exceed 100%.',
                  'No controlled runtime comparison from old OCR assistance runs.',
                  'Blank and populated JSON fields are not certified complete; no semantic JSON score.',
              ], 'documents': rows}
    write_json(folder / 'report.json', report)
    write_json(REPO / 'reports/preboard/single_pass_ocr.json', report)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default='single-pass-owner-v4')
    args = ap.parse_args()
    if not args.run_id.replace('-', '').replace('_', '').isalnum():
        ap.error('Use a simple run ID')
    folder = WORK / 'runs' / args.run_id
    report = evaluate(folder)
    print({k: report[k] for k in ['saved_photos', 'scorable_photos', 'excluded_photos', 'missing_doc_ids', 'summaries']}, flush=True)


if __name__ == '__main__':
    main()
