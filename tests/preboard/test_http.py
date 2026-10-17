import json
import threading
import unittest
import urllib.error
import urllib.request
import tempfile
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from receipt_lab.demo_pc.server import Handler, TOKEN


class RequestProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_port
        cls.base = f"http://127.0.0.1:{cls.port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, headers):
        headers = {"Content-Type": "application/json", **headers}
        req = urllib.request.Request(self.base+"/not-a-mutation", b"{}", headers)
        try:
            with urllib.request.urlopen(req) as response:
                return response.status
        except urllib.error.HTTPError as exc:
            return exc.code

    def test_stale_tab_with_browser_same_origin_remains_usable(self):
        self.assertEqual(self.post({"X-Seminar-Token":"old-token", "Origin":self.base, "Sec-Fetch-Site":"same-origin"}),404)

    def test_stale_unverified_request_is_rejected(self):
        self.assertEqual(self.post({"X-Seminar-Token":"old-token"}),403)

    def test_external_origin_rejected_even_with_token(self):
        self.assertEqual(self.post({"X-Seminar-Token":TOKEN,"Origin":"https://outside.example","Sec-Fetch-Site":"cross-site"}),403)

    def test_local_api_client_with_fresh_token(self):
        self.assertEqual(self.post({"X-Seminar-Token":TOKEN}),404)

    def test_rebinding_host_rejected(self):
        self.assertEqual(self.post({"X-Seminar-Token":TOKEN,"Host":f"outside.example:{self.port}",
                                   "Origin":f"http://outside.example:{self.port}","Sec-Fetch-Site":"same-origin"}),403)

    def test_annotation_saves_without_processing_demo_receipt(self):
        # Regression for the user's confused workflow: annotation needs no demo/current receipt.
        from receipt_lab.preboard.common import write_json,read_json
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);manifest=folder/'manifest.json'
            write_json(manifest,{'records':[{'doc_id':'R123456789ABC','sha256':'synthetic'}]})
            payload={'doc_id':'R123456789ABC','reviewer':'synthetic-test-person','slot':'first','attestation':True,
                     'transcript':'synthetic text','extraction':{'merchant':'shop','transaction_date':None,'grand_total':None,'currency':None,'items':[]}}
            with patch('receipt_lab.demo_pc.server.WORK',folder),patch('receipt_lab.preboard.review.WORK',folder),patch('receipt_lab.preboard.review.MANIFEST',manifest),patch('receipt_lab.preboard.dataset.WORK',folder):
                req=urllib.request.Request(self.base+'/api/annotate',json.dumps(payload).encode(),
                                           {'Content-Type':'application/json','X-Seminar-Token':TOKEN})
                with urllib.request.urlopen(req) as response:
                    result=json.load(response)
                    self.assertTrue(result['saved'])
                    self.assertEqual(response.status,200)
                self.assertEqual(len(list((folder/'annotations/human/R123456789ABC').glob('*.json'))),1)

    def test_old_tab_cannot_restore_annotations_after_owner_reset(self):
        with patch('receipt_lab.demo_pc.server.review_generation',return_value='new-review-session'),patch('receipt_lab.demo_pc.server.submit_human',return_value={'saved':True}) as submit:
            for generation,expected in [('initial',409),('new-review-session',200)]:
                payload={'doc_id':'R123456789ABC','review_generation':generation}
                req=urllib.request.Request(self.base+'/api/annotate',json.dumps(payload).encode(),
                                           {'Content-Type':'application/json','X-Seminar-Token':TOKEN})
                try:
                    with urllib.request.urlopen(req) as response:status=response.status
                except urllib.error.HTTPError as exc:status=exc.code
                self.assertEqual(status,expected)
            submit.assert_called_once()


if __name__=="__main__":unittest.main()
