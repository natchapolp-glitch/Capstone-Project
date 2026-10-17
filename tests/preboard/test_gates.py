"""Acceptance gates must distinguish a text matrix from the full PC pipeline."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.preboard import gates
from receipt_lab.preboard.common import digest, write_json


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.rows = [{"doc_id": f"R{i:012X}", "annotation_status": "adjudicated",
                      "transaction_group_id": f"test-group-{i}", "store": f"test-store-{i % 2}",
                      "split": "challenge", "challenge_candidate": True, "capture_conditions_status":"owner_confirmed"} for i in range(6)]
        self.snapshot = {r["doc_id"]: "synthetic-test-fingerprint" for r in self.rows}
        write_json(self.root / "dataset.json", {"records": self.rows})
        write_json(self.root / "selection.json", {"engine": "tesseract"})
        self.selection_hash = digest(self.root / "selection.json")
        self.patches = [patch.object(gates, "WORK", self.root),
                        patch.object(gates, "MANIFEST", self.root / "dataset.json"),
                        patch.object(gates, "validate", return_value=[]),
                        patch.object(gates, "fingerprints", return_value=self.snapshot)]
        for p in self.patches:
            p.start()
        self.add_matrix("evaluation-matrix", "evaluation")

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()

    def add_matrix(self, name, split):
        folder = self.root / "runs" / name
        write_json(folder / "manifest.json", {"purpose": "scored_evaluation", "split": split,
                   "dataset_snapshot": self.snapshot, "selection_sha256": self.selection_hash,
                   "expected_attempts": 288, "matrix": {"models": ["a", "b", "c", "d"],
                   "sources": ["reference", "tesseract"], "grammar": [True, False], "repetitions": 3}})
        write_json(folder / "completion.json", {"complete": True, "accuracy_scored": 288})

    def add_pipeline(self):
        folder = self.root / "runs" / "full-pipeline"
        write_json(folder / "manifest.json", {"purpose": "scored_final_pipeline_challenge",
                   "dataset_snapshot": self.snapshot, "selection_sha256": self.selection_hash,
                   "expected_attempts": 18})
        write_json(folder / "completion.json", {"complete": True})
        for row in self.rows:
            for rep in range(3):
                write_json(folder / "attempts" / f"{row['doc_id']}-r{rep}.json",
                           {"doc_id": row["doc_id"], "repetition": rep, "fields": {}, "runtime_reused":True,
                            "measurement": {"sampled_peak_rss_bytes": 100}})
        return folder

    def test_text_only_challenge_cannot_pass_pipeline_gate(self):
        self.add_matrix("challenge-matrix", "challenge")
        report = gates.build_report()
        self.assertEqual(report["gates"][2]["status"], "PASS_IMPLEMENTATION")
        self.assertEqual(report["gates"][4]["status"], "WAITING_DATA")
        self.assertFalse(report["overall_complete"])

    def test_pipeline_needs_each_document_and_repetition(self):
        folder = self.add_pipeline()
        self.assertEqual(gates.build_report()["gates"][4]["status"], "PASS_IMPLEMENTATION")
        # Keep 18 files but duplicate one document/repetition: this is not a complete run.
        write_json(folder / "attempts" / f"{self.rows[0]['doc_id']}-r2.json",
                   {"doc_id": self.rows[0]["doc_id"], "repetition": 1, "fields": {},
                    "measurement": {"sampled_peak_rss_bytes": 100}})
        self.assertEqual(gates.build_report()["gates"][4]["status"], "WAITING_DATA")

    def test_changed_frozen_selection_invalidates_evaluation(self):
        write_json(self.root / "selection.json", {"engine": "easyocr"})
        self.assertEqual(gates.build_report()["gates"][2]["status"], "IN_PROGRESS")


if __name__ == "__main__":
    unittest.main()
