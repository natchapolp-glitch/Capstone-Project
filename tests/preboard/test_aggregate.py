"""Statistics preserve failed documents and separate repetitions from accuracy."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from json_extraction_scorer import score, failed_result
from receipt_lab.preboard.aggregate import aggregate, summarize_condition
from receipt_lab.preboard.field_metrics import field_metrics
from receipt_lab.preboard.common import REPO, digest, write_json
from receipt_lab.preboard.gates import has_aggregate


class AggregateTests(unittest.TestCase):
    def test_failed_documents_remain_and_repetitions_do_not_inflate_accuracy(self):
        truth={'merchant':None,'transaction_date':None,'grand_total':100,'currency':None,'items':[]}
        rows=[]
        for rep in range(3):
            for doc in ['R000000000001','R000000000002']:
                fail=doc.endswith('2')
                pred=None if fail else {**truth,'grand_total':100 if rep==0 else 150}
                rows.append({'doc_id':doc,'transaction_group_id':'one-synthetic-transaction','repetition':rep,
                             'status':'request_failed' if fail else 'ok','parse_valid':not fail,'schema_valid':not fail,
                             'score':failed_result(0,['synthetic failure']) if fail else score(truth,pred),
                             'fields':field_metrics(truth,pred),'measurement':{'wall_seconds':len(rows)+1,
                             'sampled_peak_rss_bytes':100,'memory_metric':'synthetic fixture RSS'}})
        result=summarize_condition(rows,'scored_evaluation')
        self.assertEqual(result['documents'],2)
        self.assertEqual(result['transaction_groups'],1)
        self.assertEqual(result['attempts'],6)
        self.assertEqual(result['failed_attempts'],3)
        self.assertEqual(result['macro_document_f1'],0.5)
        self.assertEqual(result['raw_parse_valid_rate'],0.5)
        self.assertEqual(result['field_accuracy']['grand_total']['accuracy'],0.5)
        self.assertEqual(result['money']['grand_total']['coverage'],0.5)
        self.assertEqual(result['money']['grand_total']['mae'],0)
        self.assertEqual(result['wall_seconds_all_attempts']['median'],3.5)
        self.assertEqual(result['wall_seconds_all_attempts']['p95'],5.75)
        with self.assertRaises(ValueError):summarize_condition(rows+[copy.deepcopy(rows[0])],'scored_evaluation')

    def test_engineering_outputs_cannot_be_published_as_accuracy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            write_json(root/'manifest.json',{'purpose':'engineering_only_no_accuracy_claim'})
            write_json(root/'completion.json',{'complete':True})
            with self.assertRaises(ValueError):aggregate(root,publish=True)
            self.assertFalse((root/'aggregate.json').exists())

    def test_gate_requires_summary_of_the_current_raw_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest={'purpose':'scored_evaluation','expected_attempts':1}
            write_json(root/'manifest.json',manifest);write_json(root/'completion.json',{'complete':True})
            attempt=root/'attempts/fixture.json';write_json(attempt,{'synthetic_fixture':0})
            self.assertFalse(has_aggregate(root,manifest))
            write_json(root/'aggregate.json',{'manifest_sha256':digest(root/'manifest.json'),
                       'completion_sha256':digest(root/'completion.json'),
                       'aggregator_sha256':digest(REPO/'receipt_lab/preboard/aggregate.py'),
                       'documents':[{'raw_evidence_sha256':digest(attempt)}]})
            self.assertTrue(has_aggregate(root,manifest))
            write_json(attempt,{'synthetic_fixture':1})
            self.assertFalse(has_aggregate(root,manifest))

    def test_completed_run_produces_reproducible_tables_in_isolated_test_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);run=root/'fixture-run';repo=root/'isolated-repo';repo.mkdir()
            (repo/'json_extraction_scorer.py').write_bytes((REPO/'json_extraction_scorer.py').read_bytes())
            doc='R000000000001';snapshot={doc:'synthetic-test-only'}
            manifest={'purpose':'scored_evaluation','split':'development','dataset_snapshot':snapshot,
                      'asset_registry_sha256':'synthetic-assets',
                      'expected_attempts':3,'scorer_sha256':digest(repo/'json_extraction_scorer.py'),
                      'matrix':{'models':['fixture-not-a-real-model'],'sources':['reference'],'grammar':[True],'repetitions':3}}
            write_json(run/'manifest.json',manifest);write_json(run/'completion.json',{'complete':True})
            write_json(root/'dataset.json',{'records':[{'doc_id':doc,'transaction_group_id':'synthetic-test-transaction'}]})
            truth={'merchant':None,'transaction_date':None,'grand_total':100,'currency':None,'items':[]}
            for rep in range(3):
                write_json(run/'attempts'/f'fixture-r{rep}.json',{'doc_id':doc,'model':{'id':'fixture-not-a-real-model'},
                           'source_kind':'reference','grammar':True,'repetition':rep,'status':'ok','parse_valid':True,'schema_valid':True,
                           'score':score(truth,truth),'fields':field_metrics(truth,truth),'measurement':{'wall_seconds':rep+1}})
            with patch('receipt_lab.preboard.aggregate.REPO',repo),patch('receipt_lab.preboard.aggregate.MANIFEST',root/'dataset.json'),patch('receipt_lab.preboard.aggregate.validate',return_value=[]),patch('receipt_lab.preboard.aggregate.require_registry',return_value='synthetic-assets'),patch('receipt_lab.preboard.aggregate.fingerprints',return_value=snapshot):
                result=aggregate(run,publish=True)
            self.assertEqual(len(result['documents']),3)
            self.assertEqual(next(iter(result['conditions'].values()))['macro_document_f1'],1)
            self.assertTrue(has_aggregate(run,manifest))
            for suffix in ['json','csv','md']:
                self.assertTrue((repo/f'reports/preboard/scored/fixture-run.{suffix}').exists())


if __name__=='__main__':unittest.main()
