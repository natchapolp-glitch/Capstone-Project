import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.preboard import evidence_checks as checks
from receipt_lab.preboard.common import write_json, digest, object_hash


class EvidenceChecksTests(unittest.TestCase):
    def test_llm_summary_requires_intact_raw_and_same_selected_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); folder=root/'runs/fixture'
            entry={'slot':'first','transcript':'test'}
            write_json(folder/'manifest.json',{'samples':[{'doc_id':'fixture','reference_entry_sha256':object_hash(entry)}]})
            raw=folder/'attempts/a.json'; write_json(raw,{'fixture':True})
            report={'manifest_sha256':digest(folder/'manifest.json'),'attempts':1,
                    'evidence':[{'attempt_key':'a','sha256':digest(raw)}]}
            write_json(folder/'completion.json',report)
            with patch.object(checks,'WORK',root),patch.object(checks,'annotations',return_value=[entry]) as ann:
                self.assertTrue(checks.check_llm(report))
                self.assertFalse(checks.check_llm({**report,'attempts':288}))
                ann.return_value=[{**entry,'transcript':'changed'}]
                self.assertFalse(checks.check_llm(report))
                ann.return_value=[entry]
                write_json(raw,{'fixture':'changed raw'})
                self.assertFalse(checks.check_llm(report))

    def test_missing_pc_summary_is_not_measured_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(checks,'WORK',Path(tmp)):
                self.assertFalse(checks.check_pc({'attempts':9}))

    def test_pc_rejects_changed_public_numbers_even_with_valid_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); folder=root/'runs/fixture'
            write_json(folder/'manifest.json',{'fixture':True})
            raw=folder/'a.json'; write_json(raw,{'fixture':True})
            summary={'attempts':1,'failures':0,'raw_evidence_sha256':{'a.json':digest(raw)}}
            write_json(folder/'summary.json',summary)
            report={**summary,'manifest_sha256':digest(folder/'manifest.json'),
                    'private_summary_sha256':digest(folder/'summary.json')}
            with patch.object(checks,'WORK',root):
                self.assertTrue(checks.check_pc(report))
                self.assertFalse(checks.check_pc({**report,'failures':9}))


if __name__=='__main__': unittest.main()
