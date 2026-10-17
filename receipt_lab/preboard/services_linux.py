"""Run inside WSL; isolated development HA Core and loopback MQTT broker."""
import argparse
import json
import os
import signal
import subprocess
from pathlib import Path

ROOT = Path.home() / "SeminarLab/preboard-services"
CONFIG = """homeassistant:
  name: Seminar Preboard Local
  latitude: 0
  longitude: 0
  elevation: 0
  time_zone: Asia/Bangkok
  unit_system: metric
http:
  server_host: 127.0.0.1
  server_port: 8123
api:
websocket_api:
frontend:
config:
onboarding:
person:
recorder:
  purge_keep_days: 7
history:
mqtt:
  sensor:
    - name: Seminar latest purchase total
      unique_id: seminar_preboard_latest_total
      state_topic: seminar/preboard/purchases/latest
      value_template: '{{ value_json.extraction.grand_total }}'
      json_attributes_topic: seminar/preboard/purchases/latest
    - name: Seminar latest item count
      unique_id: seminar_preboard_latest_item_count
      state_topic: seminar/preboard/purchases/latest
      value_template: '{{ value_json.extraction["items"] | length }}'
      json_attributes_topic: seminar/preboard/purchases/latest
"""


def start(name, command):
    pidfile = ROOT / f"{name}.pid"
    if pidfile.exists():
        pid = int(pidfile.read_text())
        try:
            if str(ROOT).encode() in Path(f"/proc/{pid}/cmdline").read_bytes():
                return {"service": name, "pid": pid, "status": "already_running"}
        except FileNotFoundError:
            pass
    log = (ROOT / f"{name}.log").open("ab")
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    log.close()
    pidfile.write_text(str(process.pid))
    return {"service": name, "pid": process.pid, "status": "started"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["start", "stop", "status"])
    ap.add_argument("--only", choices=["all", "broker", "ha"], default="all")
    args = ap.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    config = ROOT / "ha"
    config.mkdir(exist_ok=True)
    target = config / "configuration.yaml"
    if not target.exists():
        target.write_text(CONFIG)
    broker = ROOT / "mosquitto.conf"
    broker.write_text("listener 18884 127.0.0.1\nallow_anonymous true\npersistence true\npersistence_location "+str(ROOT)+"/\n")
    if args.command == "start":
        commands = {"broker": ["mosquitto", "-c", str(broker)],
                    "ha": [str(Path.home()/"SeminarLab/preboard-ha/bin/hass"), "-c", str(config)]}
        print(json.dumps([start(name, cmd) for name, cmd in commands.items() if args.only in {"all", name}]))
    else:
        results = []
        for name in ["ha", "broker"]:
            if args.only not in {"all", name}:
                continue
            pidfile = ROOT / f"{name}.pid"
            pid = int(pidfile.read_text()) if pidfile.exists() else None
            active = bool(pid and Path(f"/proc/{pid}/cmdline").exists() and str(ROOT).encode() in Path(f"/proc/{pid}/cmdline").read_bytes())
            if args.command == "stop" and active:
                os.kill(pid, signal.SIGTERM)
            results.append({"service": name, "pid": pid, "active": active})
        print(json.dumps(results))


if __name__ == "__main__":
    main()
