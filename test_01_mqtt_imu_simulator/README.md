# Test 01 — MQTT IMU Simulator

Refs: [GitHub Issue #1](https://github.com/itayep/wsl_tests/issues/1)

## Environment
Run on **Ubuntu WSL2 on `itaymini`** (not Windows PowerShell).

## Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Copy and fill in credentials
cp .env.example .env
nano .env
```

## Run
```bash
python3 mqtt_imu_simulator.py
```

## What it does
- Publishes fake IMU JSON to `esp32s3/imu` at **10 Hz**
- Publishes heartbeat to `esp32s3/status` every 5 seconds
- Subscribes to `esp32s3/lcd` and prints incoming messages
- Stops on `Ctrl+C`

## Verify on Android
Open any MQTT client app → connect to same broker → subscribe to `esp32s3/imu`.
