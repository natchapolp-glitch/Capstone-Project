"""Real broker failure/recovery and HA state trace using clearly labelled automation."""
import json
import subprocess
import sys
import time

from receipt_lab.demo_pc.store import Store, publish_pending
from .common import WORK, read_json, utc, write_json
from .services import access_token, request


def main():
    source = Store(WORK/"services/demo.sqlite")
    selected = next(r for r in source.list() if r["doc_id"]=="R4F4EA934251E" and source.get(r["id"])["raw_result"].get("llm",{}).get("schema_valid"))
    raw = source.get(selected["id"])["raw_result"]
    store = Store(WORK/"services/transport-engineering.sqlite")
    rid = store.add(selected["doc_id"], raw)
    extraction = raw["extraction"]
    event_id = store.confirm(rid, extraction, "automated_engineering_test_not_human_ground_truth", 0)
    command = [sys.executable, "-m", "receipt_lab.preboard.services"]
    subprocess.run(command+["stop", "--only", "broker"], check=True)
    time.sleep(1)
    failed = publish_pending(store)
    if not failed or not failed[0]["error"]:
        raise AssertionError("Expected delivery failure when broker is stopped")
    subprocess.run(command+["start", "--only", "broker"], check=True)
    time.sleep(2)
    retried = publish_pending(store)
    if not retried or any(r["error"] for r in retried):
        raise AssertionError("Broker recovery did not deliver")
    replay_event = Store(WORK/"services/transport-engineering.sqlite").confirm(rid, extraction, "automated_test_retry", 0)
    if replay_event != event_id or store.pending():
        raise AssertionError("Repeated confirmation/restart created another pending event")
    token = access_token()
    observed = None
    for _ in range(40):
        states = request("/api/states", token=token)
        observed = [s for s in states if s["entity_id"].startswith("sensor.seminar_") and s["attributes"].get("event_id")==event_id]
        if len(observed)==2:
            break
        time.sleep(0.5)
    if len(observed or []) != 2:
        raise AssertionError("MQTT PUBACK succeeded but two HA states have not confirmed receipt")
    reject_id = store.add(selected["doc_id"], raw)
    store.reject(reject_id)
    invalid_rejected = False
    try:
        store.confirm(store.add(selected["doc_id"], raw), {"bad_key":1}, "automated_test", 0)
    except ValueError:
        invalid_rejected = True
    report = {"timestamp": utc(), "purpose": "real local transport integration test; confirmations automated, not human review",
              "source_pipeline_id": selected["id"], "transaction_id": rid, "event_id": event_id,
              "broker_stopped_delivery_failed": bool(failed[0]["error"]), "broker_restarted_delivery": retried,
              "repeat_confirmation_same_event": replay_event==event_id, "restart_no_pending_event": not store.pending(),
              "invalid_schema_blocked": invalid_rejected, "rejected_receipt_status": store.get(reject_id)["status"],
              "ha_states": observed, "mqtt_qos": 1, "retained_state": True,
              "delivery_semantics": "at least once; event_id dedup plus state overwrite, no additive inventory counting"}
    traces = [{"doc_id":selected["doc_id"], "source_pipeline_id":selected["id"], "event_id":event_id,
               "ha_entities":[s["entity_id"] for s in observed]}]
    examples = WORK/"runs/demo-engineering-v2/records.json"
    if examples.exists():
        for example in read_json(examples):
            if example["doc_id"] == selected["doc_id"]:
                continue
            candidate = source.get(example["id"])["raw_result"]
            if not candidate.get("llm",{}).get("schema_valid") or candidate["llm"]["status"]!="ok":
                continue
            new_id = store.add(example["doc_id"], candidate)
            event = store.confirm(new_id, candidate["extraction"], "automated_engineering_test_not_human_ground_truth", 0)
            delivery = publish_pending(store)
            if any(r["error"] for r in delivery):
                raise AssertionError("Additional real pipeline example delivery failed")
            for _ in range(40):
                current = [s for s in request("/api/states",token=token) if s["entity_id"].startswith("sensor.seminar_") and s["attributes"].get("event_id")==event]
                if len(current)==2:
                    break
                time.sleep(.5)
            if len(current)!=2:
                raise AssertionError("Additional pipeline event not observed in HA")
            traces.append({"doc_id":example["doc_id"],"source_pipeline_id":example["id"],"event_id":event,
                           "ha_entities":[s["entity_id"] for s in current],"ha_states":current})
    report["real_photo_traces"] = traces
    report["transaction_grouping_limitation"] = "Photo IDs differ; independent transaction grouping still requires human review"
    write_json(WORK/"runs/delivery-integration/evidence.json", report)
    print(json.dumps({k:report[k] for k in ["event_id","broker_stopped_delivery_failed","repeat_confirmation_same_event","invalid_schema_blocked"]}))


if __name__ == "__main__":
    main()
