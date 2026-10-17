"""Start/stop local services and configure an isolated HA instance without leaking tokens."""
import argparse
import json
import secrets
import subprocess
import time
import urllib.parse
import urllib.request

from .common import REPO, WORK, read_json, utc, write_json
from .ocr import wsl_path

BASE = "http://127.0.0.1:8123"
AUTH = WORK / "services/ha_auth.json"


def request(path, data=None, token=None, form=False, method=None):
    headers = {}
    if token:
        headers["Authorization"] = "Bearer "+token
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode() if form else json.dumps(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    req = urllib.request.Request(BASE+path, body, headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def access_token():
    auth = read_json(AUTH)
    reply = request("/auth/token", {"grant_type": "refresh_token", "refresh_token": auth["refresh_token"], "client_id": BASE+"/"}, form=True)
    return reply["access_token"]


def configure():
    # This path is a new, isolated dev instance; never onboard or reconfigure an existing user's HA.
    for attempt in range(90):
        try:
            steps = request("/api/onboarding")
            break
        except OSError:
            time.sleep(1)
    else:
        raise TimeoutError("HA startup not ready; inspect the private ha.log")
    if not AUTH.exists():
        if any(s["step"] == "user" and s["done"] for s in steps):
            raise RuntimeError("HA already has a user but no task credentials; refusing to overwrite it")
        credentials = {"name": "Seminar Local Demo", "username": "seminar_local", "password": secrets.token_urlsafe(32),
                       "client_id": BASE+"/", "language": "en"}
        reply = request("/api/onboarding/users", credentials)
        auth = request("/auth/token", {"grant_type": "authorization_code", "code": reply["auth_code"], "client_id": BASE+"/"}, form=True)
        # Stored only outside the repository; never log the password or bearer tokens.
        write_json(AUTH, {"username": credentials["username"], "password": credentials["password"],
                          "refresh_token": auth["refresh_token"], "created_at": utc()})
    token = access_token()
    config = request("/api/config", token=token)
    if config["location_name"] != "Seminar Preboard Local":
        raise RuntimeError("Unexpected HA instance; refusing to configure")
    confirm = subprocess.run(["wsl", "-d", "Ubuntu", "--exec", "/home/natchapol/SeminarLab/preboard-ha/bin/python",
                              wsl_path(REPO/"receipt_lab/preboard/ha_confirm_linux.py")],
                             input=json.dumps({"access_token": token}), text=True, capture_output=True)
    if confirm.returncode:
        raise RuntimeError("Cannot confirm local HA HTTP config: "+confirm.stderr[-400:])
    write_json(WORK/"services/ha_http_confirmation.json", json.loads(confirm.stdout))
    entries = request("/api/config/config_entries/entry", token=token)
    if not any(e["domain"] == "mqtt" for e in entries):
        flow = request("/api/config/config_entries/flow", {"handler": "mqtt", "show_advanced_options": False}, token)
        for _ in range(5):
            if flow["type"] in {"create_entry", "abort"}:
                break
            if flow.get("step_id") == "user":
                data = {"broker": "127.0.0.1", "port": 18884, "protocol": "5", "username": "", "password": "",
                        "other_settings": {"set_client_cert": False, "set_ca_cert": "off", "transport": "tcp"}}
            elif flow.get("step_id") in {"options", "broker"}:
                data = {"broker": "127.0.0.1", "port": 18884, "protocol": "5", "username": "", "password": "",
                        "other_settings": {"set_client_cert": False, "set_ca_cert": "off", "transport": "tcp"}}
            else:
                raise RuntimeError("Unexpected MQTT config step: "+str(flow.get("step_id")))
            flow = request("/api/config/config_entries/flow/"+flow["flow_id"], data, token)
        write_json(WORK / "services/ha_mqtt_setup.json", {"timestamp": utc(), "version": config["version"],
                   "flow_type": flow["type"], "reason": flow.get("reason"), "step": flow.get("step_id")})
    print(json.dumps({"ha_version": config["version"], "instance": config["location_name"], "auth": "stored privately"}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["start", "stop", "status", "configure", "states"])
    ap.add_argument("--only", choices=["all", "broker", "ha"], default="all")
    args = ap.parse_args()
    if args.command in {"start", "stop", "status"}:
        subprocess.run(["wsl", "-d", "Ubuntu", "--exec", "python3", wsl_path(REPO/"receipt_lab/preboard/services_linux.py"), args.command, "--only", args.only], check=True)
    elif args.command == "configure":
        configure()
    else:
        states = request("/api/states", token=access_token())
        result = [s for s in states if s["entity_id"].startswith("sensor.seminar_")]
        write_json(WORK / "services/ha_states.json", {"timestamp": utc(), "states": result})
        print(json.dumps({"entities": [s["entity_id"] for s in result], "count": len(result)}))


if __name__ == "__main__":
    main()
