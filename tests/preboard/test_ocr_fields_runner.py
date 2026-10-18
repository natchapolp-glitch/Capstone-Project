"""The controlled extractor compares both crops, retains failures and resumes."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.preboard import evaluate_ocr_fields as runner
from receipt_lab.preboard.common import read_json, write_json
from receipt_lab.preboard.aggregate import aggregate


class FixedExtractorTests(unittest.TestCase):
    def test_both_engines_and_crops_have_three_warm_attempts_without_retrying(self):
        truth={'merchant':None,'transaction_date':None,'grand_total':100,'currency':None,'items':[]}
        class Model:
            loads=0;calls=0
            def __init__(self,model):
                Model.loads+=1;self.load={'wall_seconds':0.1,'synthetic_fixture':True}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def extract(self,text,grammar):
                assert grammar is True
                Model.calls+=1
                return {'status':'ok','parse_valid':True,'schema_valid':True,'parsed_output':truth,
                        'model':{'id':'synthetic-test-model'},'measurement':{'wall_seconds':1,'sampled_peak_rss_bytes':100}}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);doc='R000000000001';source=root/'source-ocr';manifest=root/'dataset.json'
            write_json(manifest,{'records':[{'doc_id':doc,'split':'development','transaction_group_id':'synthetic-transaction'}]})
            write_json(source/'manifest.json',{'doc_ids':[doc],'purpose':'synthetic fixture only'})
            write_json(source/'completion.json',{'complete':True})
            write_json(root/'annotations/adjudicated'/f'{doc}.json',{'extraction':truth})
            for engine in ['easyocr','tesseract']:
                for mode in ['reference','predicted']:
                    failed=engine=='easyocr' and mode=='predicted'
                    write_json(source/'attempts'/f'{doc}-{engine}-{mode}-r0.json',
                               {'status':'failed' if failed else 'ok','text':'' if failed else 'SYNTHETIC TOTAL 100'})
            argv=['fields','--split','development','--model','synthetic-test-model','--ocr-run',str(source),'--run-id','fixture-fields']
            with patch.object(runner,'WORK',root),patch.object(runner,'MANIFEST',manifest),patch.object(runner,'validate',return_value=[]),patch.object(runner,'fingerprints',return_value={doc:'synthetic'}),patch.object(runner,'checked_ocr_run',return_value=source),patch.object(runner,'require_registry',return_value='synthetic-assets'),patch.object(runner,'environment',return_value={'device':'synthetic fixture'}),patch.object(runner,'LocalLLM',Model),patch.object(sys,'argv',argv),contextlib.redirect_stdout(io.StringIO()):
                runner.main();runner.main()
            folder=root/'runs/fixture-fields'
            self.assertEqual(Model.loads,1)
            self.assertEqual(Model.calls,13) # one excluded warm-up + twelve measured calls
            completion=read_json(folder/'completion.json')
            self.assertTrue(completion['complete']);self.assertEqual(completion['attempts'],12)
            attempts=[read_json(p) for p in (folder/'attempts').glob('*.json')]
            self.assertEqual(sum(r['score']['f1']==0 for r in attempts),3)
            with patch('receipt_lab.preboard.aggregate.MANIFEST',manifest),patch('receipt_lab.preboard.aggregate.WORK',root),patch('receipt_lab.preboard.aggregate.validate',return_value=[]),patch('receipt_lab.preboard.aggregate.require_registry',return_value='synthetic-assets'),patch('receipt_lab.preboard.aggregate.fingerprints',return_value={doc:'synthetic'}):
                report=aggregate(folder)
            self.assertEqual(len(report['conditions']),4)
            self.assertEqual(sum(r['primary_failed_documents'] for r in report['conditions'].values()),1)


if __name__=='__main__':unittest.main()
