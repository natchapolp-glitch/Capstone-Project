import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

from json_extraction_scorer import schema_errors
from receipt_lab.preboard.common import object_hash, utc


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS receipts (
                  id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, raw_json TEXT NOT NULL,
                  confirmed_json TEXT, status TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS edits (
                  id INTEGER PRIMARY KEY, receipt_id TEXT NOT NULL, revision INTEGER NOT NULL,
                  before_json TEXT, after_json TEXT NOT NULL, actor TEXT NOT NULL, timestamp TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS outbox (
                  event_id TEXT PRIMARY KEY, receipt_id TEXT NOT NULL, revision INTEGER NOT NULL,
                  payload TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                  sent_at TEXT, error TEXT, UNIQUE(receipt_id, revision));
            """)

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path, timeout=20)
        con.row_factory = sqlite3.Row
        try:
            with con:
                yield con
        finally:
            con.close()

    def add(self, doc_id, raw):
        rid = str(uuid.uuid4())
        now = utc()
        with self.connect() as con:
            con.execute("INSERT INTO receipts VALUES (?,?,?,?,?,?,?,?)",
                        (rid, doc_id, json.dumps(raw, ensure_ascii=False, allow_nan=False), None,
                         "pending_review", 0, now, now))
        return rid

    def get(self, rid):
        with self.connect() as con:
            row = con.execute("SELECT * FROM receipts WHERE id=?", (rid,)).fetchone()
        if not row:
            raise KeyError(rid)
        item = dict(row)
        item["raw_result"] = json.loads(item.pop("raw_json"))
        item["confirmed"] = json.loads(item.pop("confirmed_json") or "null")
        return item

    def list(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute("SELECT id,doc_id,status,revision,created_at FROM receipts ORDER BY created_at DESC")]

    def confirm(self, rid, extraction, actor, expected_revision):
        errors = schema_errors(extraction)
        if errors:
            raise ValueError("; ".join(errors))
        if not actor.strip():
            raise ValueError("Reviewer name is required")
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool):
            raise ValueError("Expected revision is required")
        data = json.dumps(extraction, ensure_ascii=False, allow_nan=False)
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM receipts WHERE id=?", (rid,)).fetchone()
            if not row:
                raise KeyError(rid)
            if row["status"] == "rejected":
                raise ValueError("Rejected record cannot be published")
            if row["confirmed_json"] and object_hash(json.loads(row["confirmed_json"])) == object_hash(extraction):
                return con.execute("SELECT event_id FROM outbox WHERE receipt_id=? AND revision=?", (rid, row["revision"])).fetchone()[0]
            if row["revision"] != expected_revision:
                raise ValueError("Stale revision: reload the receipt before editing")
            revision = row["revision"] + 1
            event_id = f"{rid}:{revision}"
            raw = json.loads(row["raw_json"])
            payload = {"event_id": event_id, "transaction_id": rid, "doc_id": row["doc_id"],
                       "revision": revision, "confirmed_at": utc(), "extraction": extraction,
                       "source_sha256": raw.get("source_sha256"),
                       "schema_sha256": raw.get("schema_sha256"),
                       "note": "Confirmed purchase input, not remaining inventory or consumption rate"}
            con.execute("INSERT INTO edits(receipt_id,revision,before_json,after_json,actor,timestamp) VALUES(?,?,?,?,?,?)",
                        (rid, revision, row["confirmed_json"], data, actor, utc()))
            con.execute("INSERT INTO outbox(event_id,receipt_id,revision,payload) VALUES(?,?,?,?)",
                        (event_id, rid, revision, json.dumps(payload, ensure_ascii=False, allow_nan=False)))
            con.execute("UPDATE receipts SET confirmed_json=?,revision=?,status='confirmed',updated_at=? WHERE id=?",
                        (data, revision, utc(), rid))
        return event_id

    def reject(self, rid):
        with self.connect() as con:
            row = con.execute("SELECT status FROM receipts WHERE id=?", (rid,)).fetchone()
            if not row or row["status"] != "pending_review":
                raise ValueError("Only pending receipts can be rejected")
            con.execute("UPDATE receipts SET status='rejected',updated_at=? WHERE id=?", (utc(), rid))

    def pending(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute("SELECT * FROM outbox WHERE sent_at IS NULL ORDER BY rowid")]

    def delivery(self, event_id, error=None):
        with self.connect() as con:
            row = con.execute("SELECT * FROM outbox WHERE event_id=?", (event_id,)).fetchone()
            if not row:
                raise KeyError(event_id)
            if row["sent_at"]:
                return
            con.execute("UPDATE outbox SET attempts=attempts+1,error=?,sent_at=? WHERE event_id=?",
                        (error, None if error else utc(), event_id))
            con.execute("UPDATE receipts SET status=?,updated_at=? WHERE id=? AND revision=?",
                        ("publish_failed" if error else "published", utc(), row["receipt_id"], row["revision"]))


def publish_pending(store, host="127.0.0.1", port=18884):
    import paho.mqtt.client as mqtt
    results = []
    for row in store.pending():
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="seminar-"+uuid.uuid4().hex[:10])
        error = None
        try:
            client.connect(host, port, keepalive=20)
            client.loop_start()
            info = client.publish("seminar/preboard/purchases/latest", row["payload"], qos=1, retain=True)
            info.wait_for_publish(timeout=10)
            if not info.is_published():
                raise TimeoutError("No MQTT PUBACK")
        except (OSError, RuntimeError, TimeoutError) as exc:
            error = str(exc)
        finally:
            client.disconnect()
            client.loop_stop()
        store.delivery(row["event_id"], error)
        results.append({"event_id": row["event_id"], "error": error, "mqtt_puback": error is None})
        if error:
            break  # preserve ordering: an older failed event must not overwrite a newer state later
    return results
