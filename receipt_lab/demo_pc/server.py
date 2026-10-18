"""Loopback-only UI for human annotation and confirmed-purchase demonstration."""
import argparse
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from receipt_lab.preboard.common import WORK, read_json
from receipt_lab.preboard.dataset import MANIFEST, annotations
from receipt_lab.preboard.review import adjudicate, submit_human
from .store import Store, publish_pending

_token_path = WORK / "services/ui_token.txt"
_token_path.parent.mkdir(parents=True, exist_ok=True)
if not _token_path.exists():
    _token_path.write_text(secrets.token_urlsafe(32), encoding="ascii")
TOKEN = _token_path.read_text(encoding="ascii").strip()
LOCK = threading.Lock()
STORE = None


def review_generation():
    path = WORK / "annotations/review_session.json"
    return read_json(path)["generation"] if path.exists() else "initial"


class Handler(BaseHTTPRequestHandler):
    def valid_host(self):
        parsed = urlparse("http://"+self.headers.get("Host", ""))
        try:
            return parsed.hostname in {"127.0.0.1", "localhost"} and parsed.port == self.server.server_port
        except ValueError:
            return False

    def output(self, value, status=200, content_type="application/json; charset=utf-8"):
        body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode() if content_type.startswith("application/json") else value
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.valid_host():
            return self.output({"error": "Local host required"}, 403)
        url = urlparse(self.path)
        query = parse_qs(url.query)
        try:
            if url.path in {"/", "/demo"}:
                self.output(Path(__file__).with_name("index.html").read_bytes(), content_type="text/html; charset=utf-8")
            elif url.path == "/review":
                self.output(Path(__file__).with_name("review.html").read_bytes(), content_type="text/html; charset=utf-8")
            elif url.path == "/api/state":
                rows = read_json(MANIFEST)["records"]
                priority = read_json(WORK/"annotations/priority_queue.json")["doc_ids"] if (WORK/"annotations/priority_queue.json").exists() else []
                rows = sorted(rows, key=lambda r: (priority.index(r["doc_id"]) if r["doc_id"] in priority else 999, r["doc_id"]))
                self.output({"token": TOKEN, "review_generation": review_generation(), "documents": [{"doc_id": r["doc_id"], "store": r["store"],
                            "has_saved_transcript": any(e['slot']=='first' for e in annotations(r['doc_id'])),
                            "status": r["annotation_status"], "prior_item_name_status": r["prior_item_name_status"],
                            "rotation": r["rotation_to_read"], "original_pixel_boxes": r["original_pixel_boxes"]} for r in rows],
                            "receipts": STORE.list(),
                            "reviewer_defaults": read_json(WORK/"annotations/reviewer_roster.json") if (WORK/"annotations/reviewer_roster.json").exists() else {}})
            elif url.path == "/api/receipt":
                self.output(STORE.get(query["id"][0]))
            elif url.path == "/api/review-count":
                records = annotations(query["doc_id"][0])
                self.output({"slots": [r["slot"] for r in records], "reviewers": [r["reviewer"] for r in records],
                             "saved_entry": next((r for r in records if r['slot'] == 'first'), None),
                             "review_method": "single_reviewer_single_pass"})
            elif url.path == "/api/ocr-draft":
                doc_id = query["doc_id"][0]
                if doc_id not in {r['doc_id'] for r in read_json(MANIFEST)['records']}:
                    raise ValueError("Unknown document")
                candidates = [WORK/f"runs/{run}/attempts/{doc_id}.json" for run in ['draft-easyocr-all59-v1','draft-tesseract-all59-v2']]
                selected = next((p for p in candidates if p.exists()), None)
                if selected is None:
                    return self.output({"error": "OCR draft not ready yet"}, 409)
                result = read_json(selected)
                self.output({"text": result['text'], "engine": result['engine'], "unreviewed": True,
                             "warning": "OCR draft contains errors. Correct against the image; one human pass is sufficient under the owner instruction."})
            elif url.path == "/api/image":
                row = next(r for r in read_json(MANIFEST)["records"] if r["doc_id"] == query["doc_id"][0])
                path = Path(row["source"])
                if query.get("view", [""])[0] == "reference":
                    from receipt_lab.preboard.ocr import prepare_image
                    path, _ = prepare_image(row, "reference" if len(row["original_pixel_boxes"])==1 else "full")
                self.output(path.read_bytes(), content_type="image/png" if path.suffix==".png" else "image/jpeg")
            elif url.path == "/adjudicate":
                self.output(Path(__file__).with_name("review.html").read_bytes(), content_type="text/html; charset=utf-8")
            elif url.path == "/api/adjudication":
                doc_id = query["doc_id"][0]
                entries = annotations(doc_id)
                if len(entries) != 2:
                    raise ValueError("Two entry rounds are required")
                row = next(r for r in read_json(MANIFEST)["records"] if r["doc_id"]==doc_id)
                self.output({"entries": entries, "metadata": row})
            elif url.path == "/health":
                self.output({"status": "ok", "database": "ok" if STORE.list() is not None else "failed"})
            else:
                self.output({"error": "Not found"}, 404)
        except (KeyError, ValueError, StopIteration):
            self.output({"error": "Unknown document or record"}, 404)

    def do_POST(self):
        expected_origin = f"http://{self.headers.get('Host')}"
        origin = self.headers.get("Origin")
        token_matches = secrets.compare_digest(self.headers.get("X-Seminar-Token", ""), TOKEN)
        # Old tabs remain usable after a task server restart. Browser-supplied
        # exact Origin AND same-origin Fetch Metadata are an alternative CSRF check.
        browser_same_origin = origin == expected_origin and self.headers.get("Sec-Fetch-Site") == "same-origin"
        json_body = self.headers.get("Content-Type", "").split(";")[0].strip() == "application/json"
        if not self.valid_host() or not json_body or (origin is not None and origin != expected_origin) or not (token_matches or browser_same_origin):
            return self.output({"error": "Invalid local request token/origin"}, 403)
        try:
            length = int(self.headers.get("Content-Length", 0))
            if not 0 < length <= 5 * 1024 * 1024:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(length), parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
            with LOCK:
                if self.path in {"/api/annotate", "/api/adjudicate"} and data.get("review_generation", "initial") != review_generation():
                    return self.output({"error": "ข้อมูลการตรวจถูกเริ่มใหม่แล้ว กรุณาปิดหน้าเดิมและเปิด /review ใหม่ก่อนบันทึก"}, 409)
                if self.path == "/api/process":
                    from .pipeline import process
                    rid, result = process(data["doc_id"], STORE, rotation=data.get("rotation", "none"))
                    return self.output({"id": rid, "status": result["status"]})
                if self.path == "/api/confirm":
                    event = STORE.confirm(data["id"], data["extraction"], data["reviewer"], data["revision"])
                    return self.output({"event_id": event, "delivery": publish_pending(STORE)})
                if self.path == "/api/retry":
                    return self.output({"delivery": publish_pending(STORE)})
                if self.path == "/api/reject":
                    STORE.reject(data["id"])
                    return self.output({"rejected": True})
                if self.path == "/api/annotate":
                    return self.output(submit_human(data["doc_id"], data))
                if self.path == "/api/adjudicate":
                    return self.output(adjudicate(data["doc_id"], data))
            self.output({"error": "Not found"}, 404)
        except (ValueError, KeyError, TypeError) as exc:
            self.output({"error": str(exc)}, 400)
        except Exception:
            import traceback
            traceback.print_exc()
            self.output({"error": "Local processing failed; inspect server log"}, 500)

    def log_message(self, fmt, *args):
        print(self.log_date_time_string(), fmt % args, flush=True)


def main():
    global STORE
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8090)
    args = ap.parse_args()
    STORE = Store(WORK / "services/demo.sqlite")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Receipt review: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
