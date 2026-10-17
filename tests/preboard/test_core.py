import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.demo_pc.store import Store
from receipt_lab.preboard.dataset import validate
from receipt_lab.preboard.metrics import ocr_metric, summarize
from receipt_lab.preboard.common import write_json
from receipt_lab.preboard import experiment
from receipt_lab.demo_pc.pipeline import amount_warning
from receipt_lab.demo_pc import pipeline


def receipt():
    return {"merchant": "shop", "transaction_date": "2026-10-18", "currency": "THB", "grand_total": 20,
            "items": [{"name": "milk", "quantity": 2, "unit": "box", "unit_price": 10, "line_total": 20}]}


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/"state.sqlite"
        self.store = Store(self.path)
        self.rid = self.store.add("R123456789ABC", {"extraction": receipt(), "source_sha256": "hash"})

    def tearDown(self):
        self.tmp.cleanup()

    def test_pending_does_not_publish(self):
        self.assertEqual(self.store.pending(), [])

    def test_confirm_retry_restart_produces_one_event(self):
        event = self.store.confirm(self.rid, receipt(), "synthetic-test-actor", 0)
        restarted = Store(self.path)
        again = restarted.confirm(self.rid, receipt(), "synthetic-test-actor", 0)
        self.assertEqual(event, again)
        self.assertEqual(len(restarted.pending()), 1)
        restarted.delivery(event, "connection refused")
        self.assertEqual(restarted.get(self.rid)["status"], "publish_failed")
        restarted.delivery(event)
        self.assertEqual(Store(self.path).pending(), [])
        self.assertEqual(Store(self.path).get(self.rid)["status"], "published")

    def test_changed_revision_and_stale_write(self):
        self.store.confirm(self.rid, receipt(), "test", 0)
        changed = receipt(); changed["grand_total"] = 30
        with self.assertRaises(ValueError):
            self.store.confirm(self.rid, changed, "test", 0)
        self.store.confirm(self.rid, changed, "test", 1)
        self.assertEqual(self.store.get(self.rid)["revision"], 2)

    def test_invalid_cannot_reach_outbox(self):
        for data in [{"total": 20}, {**receipt(), "grand_total": True}, {**receipt(), "grand_total": float("nan")}]:
            with self.assertRaises(ValueError):
                self.store.confirm(self.rid, data, "test", 0)
        self.assertEqual(self.store.pending(), [])

    def test_reject_cannot_confirm(self):
        self.store.reject(self.rid)
        with self.assertRaises(ValueError):
            self.store.confirm(self.rid, receipt(), "test", 0)

    def test_total_difference_warns_without_blocking_vat_or_discounts(self):
        data=receipt();data['grand_total']=21.4
        self.assertTrue(amount_warning(data))
        self.store.confirm(self.rid,data,'test',0)
        data['items'][0]['line_total']=None
        self.assertIsNone(amount_warning(data))


class MetricTests(unittest.TestCase):
    def test_failure_kept_as_full_deletion(self):
        rows = [ocr_metric("abc", "abc"), ocr_metric("abc", None, "missing_output")]
        summary = summarize(rows)
        self.assertEqual(summary["attempts"], 2)
        self.assertEqual(summary["failures"], 1)
        self.assertEqual(summary["micro_cer"], 0.5)

    def test_insertions_can_exceed_one(self):
        self.assertGreater(ocr_metric("a", "bcdef")["cer"], 1)

    def test_empty_and_normalization(self):
        self.assertIsNone(ocr_metric("", "x")["cer"])
        self.assertEqual(ocr_metric("  cafe\u0301 \r\n a ", "caf\u00e9\na")["cer"], 0)
        self.assertEqual(ocr_metric('น้ำตาล\r\n  ราคา  20','น้ำตาล\nราคา 20')['cer'],0)
        self.assertGreater(ocr_metric('ข้าว','ข่าว')['cer'],0)


class DatasetTests(unittest.TestCase):
    def row(self):
        return {"doc_id": "R123456789ABC", "source": __file__, "sha256": "abc", "width": 100, "height": 200,
                "original_pixel_boxes": [[0, 0, 100, 200]], "bbox_exclusion_reason": None,
                "split": "development", "transaction_group_id": "group1", "group_status": "reviewed",
                "annotation_status": "draft_ai", "box_status": "draft_ai"}

    def test_leakage_and_bbox(self):
        a, b = self.row(), self.row()
        b.update(doc_id="R123456789ABD", sha256="def", split="evaluation", original_pixel_boxes=[[0, 0, 101, 201]])
        errors = validate({"records": [a, b]}, check_hashes=False)
        self.assertTrue(any("leakage" in e for e in errors))
        self.assertTrue(any("bbox" in e for e in errors))

    def test_ai_draft_never_counts_as_reviewed(self):
        errors = validate({"records": [self.row()]}, require_review=True, check_hashes=False)
        self.assertTrue(any("not adjudicated" in e for e in errors))


class ExperimentInputTests(unittest.TestCase):
    def test_failed_crop_without_input_hash_stays_in_matrix_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = "R123456789ABC"
            write_json(root / "manifest.json", {"records": [{"doc_id": doc,
                       "split": "development", "transaction_group_id": None},
                       {'doc_id':'R123456789ABD','split':'unassigned','challenge_candidate':True}]})
            write_json(root / "ocr/tesseract" / f"{doc}-predicted.json",
                       {"text": "", "status": "failed", "error": "no document detected"})
            with patch.object(experiment, "WORK", root), patch.object(experiment, "MANIFEST", root / "manifest.json"):
                samples = experiment.inputs(None, "development", True, "tesseract", "predicted")
            self.assertEqual(len(samples), 1)
            self.assertEqual(samples[0]["source_status"], "failed")
            self.assertIsNone(samples[0]["ocr_input_sha256"])
            self.assertIsNone(samples[0]["truth"])
            with patch.object(pipeline,'WORK',root),patch.object(pipeline,'MANIFEST',root/'manifest.json'):
                with self.assertRaises(ValueError):pipeline.process('R123456789ABD',None)


if __name__ == "__main__":
    unittest.main()
