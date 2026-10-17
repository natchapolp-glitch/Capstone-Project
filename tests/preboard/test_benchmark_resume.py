"""An interrupted OCR benchmark retains every finished trial, including failures."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.preboard import benchmark_ocr, experiment
from receipt_lab.preboard.common import digest, read_json, write_json


class ResumeTests(unittest.TestCase):
    def test_resume_preserves_failed_trial_and_finishes_missing_trials(self):
        class Engine:
            calls=0
            interrupt=True
            def __init__(self,name):
                self.name=name;self.version='synthetic-test';self.load_measurement=None
            def run(self,image):
                Engine.calls+=1
                if Engine.interrupt and Engine.calls==4:raise KeyboardInterrupt()
                return {'status':'failed' if Engine.calls==2 else 'ok','text':'fixture',
                        'wall_seconds':1,'fixture_only':True}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest=root/'dataset.json'
            write_json(manifest,{'records':[{'doc_id':'R123456789ABC','transaction_group_id':None}]})
            argv=['benchmark','--engineering','--run-id','test-resume']
            with patch.object(benchmark_ocr,'WORK',root),patch.object(benchmark_ocr,'MANIFEST',manifest),patch.object(benchmark_ocr,'fingerprints',return_value={'fixture':'test'}),patch.object(benchmark_ocr,'environment',return_value={'fixture_only':True}),patch.object(benchmark_ocr,'OCREngine',Engine),patch.object(benchmark_ocr,'prepare_image',return_value=(root/'fixture.png',{})),patch.object(sys,'argv',argv),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(KeyboardInterrupt):benchmark_ocr.main()
                attempts=root/'runs/test-resume/attempts'
                before={p.name:digest(p) for p in attempts.glob('*.json')}
                self.assertEqual(len(before),2)
                Engine.interrupt=False
                benchmark_ocr.main()
                self.assertTrue(all(digest(attempts/name)==value for name,value in before.items()))
                completion=read_json(root/'runs/test-resume/completion.json')
                self.assertTrue(completion['complete'])
                self.assertEqual(completion['attempts'],12)
                self.assertEqual(completion['failures'],1)


class ArtifactTests(unittest.TestCase):
    def test_only_completed_scored_ocr_from_same_checked_truth_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest={'purpose':'scored_ocr_evaluation','split':'evaluation','dataset_snapshot':{'fixture':'old'}}
            write_json(root/'manifest.json',manifest)
            write_json(root/'completion.json',{'complete':True,'accuracy_scored':True})
            with patch.object(experiment,'fingerprints',return_value={'fixture':'current'}):
                with self.assertRaises(ValueError):experiment.checked_ocr_run(root,[],'evaluation')
                manifest['dataset_snapshot']={'fixture':'current'}
                write_json(root/'manifest.json',manifest)
                self.assertEqual(experiment.checked_ocr_run(root,[],'evaluation'),root)
                with self.assertRaises(ValueError):experiment.checked_ocr_run(root,[],'development')
                write_json(root/'completion.json',{'complete':True,'accuracy_scored':False})
                with self.assertRaises(ValueError):experiment.checked_ocr_run(root,[],'evaluation')


if __name__=='__main__':unittest.main()
