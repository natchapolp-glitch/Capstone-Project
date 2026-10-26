"""Large binary responses remain complete across sequential browser-style requests."""
import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from receipt_lab.demo_pc.server import Handler


class TransferTests(unittest.TestCase):
    def test_two_large_binary_responses_on_one_connection(self):
        payload=bytes(range(256))*8192

        class BinaryHandler(Handler):
            def do_GET(self):
                self.output(payload, content_type='application/octet-stream')
            def log_message(self,*args):
                pass

        server=ThreadingHTTPServer(('127.0.0.1',0),BinaryHandler)
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        client=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=10)
        try:
            for _ in range(2):
                client.request('GET','/synthetic-binary')
                response=client.getresponse()
                self.assertEqual(response.status,200)
                self.assertFalse(response.will_close)
                self.assertEqual(int(response.getheader('Content-Length')),len(payload))
                self.assertEqual(response.read(),payload)
        finally:
            client.close()
            server.shutdown()
            server.server_close()
            worker.join()
