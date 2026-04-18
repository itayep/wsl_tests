#!/usr/bin/env python3
"""
ESP32-S3 IMU MQTT Simulator
===========================
Simulates the MQTT publishing behaviour of the ESP32-S3-LCD-BLE-MQTT firmware.

Topics:
  PUBLISH  esp32s3/imu     {"ax":…,"ay":…,"az":…,"gx":…,"gy":…,"gz":…,"t":…}
  PUBLISH  esp32s3/status  {"status":"alive","uptime":…,"seq":…}
  SUBSCRIBE esp32s3/lcd    plain text (printed to console)

Credentials are read from environment variables.
Copy .env.example to .env and fill in the values, then:
  export $(cat .env | xargs) && python3 mqtt_imu_simulator.py
"""

import json
import os
import random
import signal
import sys
import time

import paho.mqtt.client as mqtt

# ---------------------------------------------------------------------------
# Configuration — read from environment (set via .env file)
# ---------------------------------------------------------------------------
BROKER_HOST = os.environ.get("MQTT_HOST",      "itayep.com")
BROKER_PORT = int(os.environ.get("MQTT_PORT",  "2183"))
USERNAME    = os.environ.get("MQTT_USERNAME",  "iotdevice")
PASSWORD    = os.environ.get("MQTT_PASSWORD",  "")
CLIENT_ID   = os.environ.get("MQTT_CLIENT_ID", "esp32-simulator")

TOPIC_IMU    = "esp32s3/imu"
TOPIC_STATUS = "esp32s3/status"
TOPIC_LCD    = "esp32s3/lcd"
QOS          = 1

PUBLISH_INTERVAL_S   = 0.1   # 10 Hz  — same as real ESP32
HEARTBEAT_INTERVAL_S = 5.0

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
_running    = True
_seq        = 0
_start_time = time.time()


# ---------------------------------------------------------------------------
# IMU simulation
# ---------------------------------------------------------------------------
def simulate_imu() -> dict:
    """Return a dict mimicking the QMI8658 sensor output."""
    return {
        "ax": round(random.gauss(0.0,  0.05), 3),
        "ay": round(random.gauss(0.0,  0.05), 3),
        "az": round(random.gauss(9.81, 0.05), 3),  # gravity on Z
        "gx": round(random.gauss(0.0,  0.02), 3),
        "gy": round(random.gauss(0.0,  0.02), 3),
        "gz": round(random.gauss(0.0,  0.02), 3),
        "t":  round(random.gauss(25.0, 0.1),  2),
    }


# ---------------------------------------------------------------------------
# MQTT callbacks
# ---------------------------------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[MQTT] Connected to {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_LCD, QOS)
        client.publish(TOPIC_STATUS, json.dumps({"status": "online"}), qos=QOS)
    else:
        print(f"[MQTT] Connection failed — reason_code={reason_code}")
        sys.exit(1)


def on_disconnect(client, userdata, reason_code, properties=None):
    print(f"[MQTT] Disconnected (reason_code={reason_code})")


def on_message(client, userdata, msg):
    print(f"[LCD ] ← {msg.payload.decode(errors='replace')}")


# ---------------------------------------------------------------------------
# Signal handling
# ---------------------------------------------------------------------------
def _handle_signal(sig, frame):
    global _running
    print("\n[INFO] Shutting down…")
    _running = False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    global _seq

    if not PASSWORD:
        print("[ERROR] MQTT_PASSWORD is not set.")
        print("        Copy .env.example to .env, fill in the password, then run:")
        print("        export $(cat .env | xargs) && python3 mqtt_imu_simulator.py")
        sys.exit(1)

    signal.signal(signal.SIGINT,  _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv5)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.on_message    = on_message

    print(f"[INFO] Connecting to {BROKER_HOST}:{BROKER_PORT} as '{CLIENT_ID}' …")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=30)
    client.loop_start()

    last_heartbeat = time.time()

    while _running:
        now     = time.time()
        payload = simulate_imu()
        client.publish(TOPIC_IMU, json.dumps(payload), qos=QOS)
        print(f"[IMU ] → {json.dumps(payload)}")
        _seq += 1

        if now - last_heartbeat >= HEARTBEAT_INTERVAL_S:
            uptime = round(now - _start_time, 1)
            hb = {"status": "alive", "uptime": uptime, "seq": _seq}
            client.publish(TOPIC_STATUS, json.dumps(hb), qos=QOS)
            print(f"[BEAT] → {json.dumps(hb)}")
            last_heartbeat = now

        time.sleep(PUBLISH_INTERVAL_S)

    client.loop_stop()
    client.disconnect()
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
