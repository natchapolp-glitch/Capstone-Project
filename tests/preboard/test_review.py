import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.preboard.common import write_json, read_json, digest
from receipt_lab.preboard.review import submit_human, adjudicate, reconcile_statuses
from receipt_lab.preboard.dataset import validate
from receipt_lab.preboard.field_metrics import field_metrics


def blank():
    return {'merchant':None,'transaction_date':None,'grand_total':None,'currency':None,'items':[]}


class HumanReviewTests(unittest.TestCase):
    def test_same_human_two_rounds_and_idempotent_save(self):
        # Synthetic attestation exists only in temporary test data, never in lab annotations.
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            manifest=folder/'manifest.json'
            write_json(manifest,{'records':[{'doc_id':'R123456789ABC','sha256':'synthetic_hash'}]})
            payload={'reviewer':'synthetic-test-person','attestation':True,'transcript':'synthetic test text',
                     'extraction':blank(),'slot':'first','unreadable_regions':[]}
            with patch('receipt_lab.preboard.review.WORK',folder),patch('receipt_lab.preboard.review.MANIFEST',manifest),patch('receipt_lab.preboard.dataset.WORK',folder):
                first=submit_human('R123456789ABC',payload)
                retry=submit_human('R123456789ABC',payload)
                self.assertEqual(first['entry_id'],retry['entry_id'])
                second=submit_human('R123456789ABC',{**payload,'slot':'second'})
                self.assertEqual(second['entries'],2)
                self.assertNotEqual(first['entry_id'],second['entry_id'])
                changed=submit_human('R123456789ABC',{**payload,'transcript':'changed'})
                self.assertEqual(changed['revision'],2)
                self.assertEqual(len(list((folder/'annotations/human/R123456789ABC').glob('*.json'))),3)
                self.assertEqual(read_json(manifest)['records'][0]['annotation_status'],'human_transcribed')
                data=read_json(manifest);data['records'][0]['annotation_status']='draft_ai';write_json(manifest,data)
                history={p.name:digest(p) for p in (folder/'annotations/human/R123456789ABC').glob('*.json')}
                self.assertEqual(reconcile_statuses(),1)
                self.assertEqual(read_json(manifest)['records'][0]['annotation_status'],'human_transcribed')
                self.assertTrue(all(digest(folder/'annotations/human/R123456789ABC'/name)==value for name,value in history.items()))

    def test_ai_or_unattested_entry_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest=Path(tmp)/'manifest.json'
            write_json(manifest,{'records':[{'doc_id':'R123456789ABC','sha256':'synthetic_hash'}]})
            with patch('receipt_lab.preboard.review.MANIFEST',manifest):
                with self.assertRaises(ValueError):
                    submit_human('R123456789ABC',{'reviewer':'synthetic','attestation':False})


class FieldTests(unittest.TestCase):
    def test_large_money_error_is_serializable_and_keeps_decimal_evidence(self):
        import json
        from decimal import Decimal
        result=field_metrics({**blank(),'grand_total':100},{**blank(),'grand_total':10**400})
        error=result['numeric_absolute_errors_on_present_matched_fields'][0]
        self.assertIsNone(error['absolute_error'])
        self.assertTrue(error['outside_float_range'])
        self.assertEqual(Decimal(error['absolute_error_decimal']),Decimal(10**400-100))
        json.dumps(result,allow_nan=False)

    def test_invalid_prediction_not_zero_money_error_success(self):
        truth={**blank(),'grand_total':100}
        result=field_metrics(truth,None)
        self.assertEqual(result['counts']['grand_total'],{'correct':0,'defined_reference':1})
        self.assertEqual(result['numeric_absolute_errors_on_present_matched_fields'],[])

    def test_missing_items_count_as_failed_fields(self):
        truth={**blank(),'items':[{'name':'milk','quantity':1,'unit':None,'unit_price':10,'line_total':10}]}
        result=field_metrics(truth,blank())
        self.assertEqual(result['counts']['items.name'],{'correct':0,'defined_reference':1})
        self.assertEqual(result['missing_items'],1)


class AdjudicationTests(unittest.TestCase):
    def test_same_scope_required_and_legacy_entry_kept_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);manifest=folder/'manifest.json';doc='R123456789ABC'
            row={'doc_id':doc,'source':__file__,'sha256':digest(__file__),'width':100,'height':200,
                 'original_pixel_boxes':[[0,0,100,200]],'rotation_to_read':'none','split':'unassigned',
                 'transaction_group_id':None,'group_status':'unresolved','box_status':'draft_ai','annotation_status':'draft_ai'}
            write_json(manifest,{'version':1,'records':[row]})
            truth={**blank(),'merchant':'test shop','items':[{'name':'milk','quantity':1,'unit':None,'unit_price':None,'line_total':10}],'grand_total':10}
            with patch('receipt_lab.preboard.review.WORK',folder),patch('receipt_lab.preboard.review.MANIFEST',manifest),patch('receipt_lab.preboard.dataset.WORK',folder):
                payload={'reviewer':'synthetic-test-person','attestation':True,'transcript':'test shop\nmilk 1 10\nTotal 10',
                         'extraction':truth,'slot':'first','unreadable_regions':[]}
                first=submit_human(doc,payload)
                second=submit_human(doc,{**payload,'slot':'second'})
                adjudication={'adjudicator':'synthetic-test-person','attestation':True,'region_attestation':True,'transcript':payload['transcript'],
                    'extraction':truth,'metadata':{'original_pixel_boxes':[[1,0,100,200]],'transaction_group_id':'TX_001','split':'development'}}
                with self.assertRaises(ValueError):adjudicate(doc,adjudication)
                first_path=next((folder/'annotations/human'/doc).glob('first-*.json'))
                legacy=read_json(first_path);legacy.pop('region_definition_sha256')
                write_json(first_path,legacy) # emulate the old fixture format, not a live human record
                before=digest(first_path)
                adjudication['metadata']['original_pixel_boxes']=[[0,0,100,200]]
                with self.assertRaises(ValueError):adjudicate(doc,{**adjudication,'region_attestation':False})
                adjudicate(doc,adjudication)
                result=read_json(folder/'annotations/adjudicated'/f'{doc}.json')
                self.assertEqual(result['review_method'],'single_reviewer_double_entry')
                self.assertEqual(result['legacy_entries_without_recorded_scope'],[first['entry_id']])
                self.assertEqual(digest(first_path),before)
                self.assertEqual(validate(read_json(manifest),require_review=True),[])
                # A candidate cannot become new-photo evidence without owner provenance.
                data=read_json(manifest)
                data['records'][0].update(challenge_candidate=True,capture_conditions={k:'synthetic test only' for k in ['device','lighting','background','capture_source']})
                write_json(manifest,data)
                adjudication['metadata']['split']='challenge'
                with self.assertRaises(ValueError):adjudicate(doc,adjudication)
                adjudication['new_scene_attestation']=True
                adjudicate(doc,adjudication)
                self.assertEqual(validate(read_json(manifest),require_review=True),[])
                self.assertEqual(len(list((folder/'annotations/adjudication_history'/doc).glob('*.json'))),1)


if __name__=='__main__':unittest.main()
