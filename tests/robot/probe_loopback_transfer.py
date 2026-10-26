"""Diagnose local HTTP framing using synthetic bytes, without receipt data."""
import http.client
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

results=[]
for protocol in ['HTTP/1.0','HTTP/1.1']:
    class Handler(BaseHTTPRequestHandler):
        protocol_version=protocol
        def do_GET(self):
            data=b'x' * 2000000
            self.send_response(200)
            self.send_header('Content-Type','application/octet-stream')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    client=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=10)
    start=time.monotonic()
    try:
        client.request('GET','/synthetic-test')
        response=client.getresponse()
        read=0
        while True:
            chunk=response.read(65536)
            if not chunk:break
            read+=len(chunk)
        results.append({'protocol':protocol,'bytes':read,'elapsed':time.monotonic()-start})
    except Exception as exc:
        results.append({'protocol':protocol,'bytes':read,'error':str(exc),'elapsed':time.monotonic()-start})
    finally:
        client.close();server.shutdown();server.server_close()
print(json.dumps(results,indent=2))
