import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.preboard.common import object_hash, write_json, read_json
from receipt_lab.preboard.single_pass import POLICY, eligible, evaluate, scoring_text


class SinglePassTests(unittest.TestCase):
    def test_one_attested_text_suffices_but_missing_scope_is_excluded(self):
        row = {'doc_id': 'fixture', 'sha256': 'test', 'original_pixel_boxes': [[0, 0, 10, 10]], 'rotation_to_read': 'none'}
        entry = {'reviewer_kind': 'human', 'attestation': True, 'source_sha256': 'test',
                 'transcript': 'Milk', 'extraction': {'items': []},
                 'region_definition_sha256': object_hash({'boxes': row['original_pixel_boxes'], 'rotation': 'none'})}
        self.assertEqual(eligible(row, entry), [])
        self.assertIn('explicit_partial_unreadable', eligible(row, {**entry, 'unreadable_regions': ['line 1']}))
        self.assertIn('unverified_or_changed_display_scope', eligible(row, {**entry, 'region_definition_sha256': None}))
        self.assertEqual(eligible(row, {**entry, 'transcript':'Milk [cite: 1]'}), [])
        self.assertIn('annotation_markup_not_literal_receipt_text', eligible(row, {**entry, 'transcript':'Milk [cite: unknown]'}))
        self.assertIn('abbreviated_numeric_text', eligible(row, {**entry, 'transcript':'barcode 8851434...'}))

    def test_normalization_only_removes_explicit_numeric_citation_tags(self):
        self.assertEqual(scoring_text('Milk 12 [cite: 14]\nTOTAL [20]'), 'Milk 12 \nTOTAL [20]')
        self.assertEqual(scoring_text('[cite: unknown]'), '[cite: unknown]')

    def test_skipped_json_never_scored_and_paired_denominator_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root / 'run'
            def record(doc, matches, assisted=False):
                return {'doc_id': doc, 'entry_sha256': 'test', 'crop_mode': 'reference',
                        'exclusion_reasons': [], 'entry': {'transcript': 'ABC', 'extraction': {'items': []},
                        'model_assisted_first_entry': assisted}, 'predictions': {
                            'easyocr': {'text': 'ADC', 'status': 'ok', 'scope_matches': matches},
                            'tesseract': {'text': '', 'status': 'failed', 'scope_matches': True}}}
            write_json(folder / 'snapshot.json', {'policy': POLICY, 'candidate_photos': 3,
                       'missing_doc_ids': ['missing'], 'records': [record('one', True, True), record('two', False)]})
            with patch('receipt_lab.preboard.single_pass.REPO', root):
                report = evaluate(folder)
            self.assertEqual(report['scorable_photos'], 1)
            self.assertEqual(report['excluded_photos'], 1)
            self.assertIsNone(report['structured_json_accuracy'])
            self.assertEqual(report['summaries']['all_eligible']['tesseract']['micro_cer'], 1)
            self.assertEqual(report['summaries']['all_eligible']['easyocr']['micro_cer'], 1/3)
            self.assertTrue(all(r['structured_accuracy'] is None for r in report['documents']))
            self.assertEqual(read_json(folder / 'snapshot.json')['records'][0]['entry']['extraction'], {'items': []})


if __name__ == '__main__':
    unittest.main()
