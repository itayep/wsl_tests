#!/usr/bin/env bash
# =============================================================================
# create_test.sh  —  Scaffold a new test folder in wsl_tests
# =============================================================================
# Usage:
#   ./create_test.sh <number> <short_name> "<description>"
#
# Example:
#   ./create_test.sh 02 rpi_mqtt_simulator "MQTT IMU simulator on Raspberry Pi"
#
# Creates:
#   test_02_rpi_mqtt_simulator/
#     README.md
#     requirements.txt
#     .env.example
#     .gitignore
#     main.py
# =============================================================================

set -euo pipefail

# --- Args ---
NUM="${1:-}"
NAME="${2:-}"
DESC="${3:-No description provided}"

if [[ -z "$NUM" || -z "$NAME" ]]; then
    echo "Usage: $0 <number> <short_name> \"<description>\""
    echo "Example: $0 02 rpi_mqtt_simulator \"MQTT IMU simulator on Raspberry Pi\""
    exit 1
fi

# Zero-pad number to 2 digits
NUM=$(printf "%02d" "$NUM")
FOLDER="test_${NUM}_${NAME}"

if [[ -d "$FOLDER" ]]; then
    echo "[ERROR] Folder '$FOLDER' already exists."
    exit 1
fi

mkdir -p "$FOLDER"
echo "[INFO] Created folder: $FOLDER"

# --- README.md ---
cat > "$FOLDER/README.md" << EOF
# Test ${NUM} — ${DESC}

## Environment
> Describe the target environment here (WSL2 / Raspberry Pi / etc.)

## Setup
\`\`\`bash
pip3 install -r requirements.txt
cp .env.example .env
nano .env
\`\`\`

## Run
\`\`\`bash
export \$(cat .env | xargs) && python3 main.py
\`\`\`

## What it does
> Describe the test here.

## Acceptance Criteria
- [ ] TODO
EOF
echo "[INFO] Created $FOLDER/README.md"

# --- requirements.txt ---
cat > "$FOLDER/requirements.txt" << EOF
# Add Python dependencies here
# Example: paho-mqtt>=2.0.0
EOF
echo "[INFO] Created $FOLDER/requirements.txt"

# --- .env.example ---
cat > "$FOLDER/.env.example" << EOF
# Copy to .env and fill in real values
# .env is gitignored — never commit credentials

# MQTT_HOST=
# MQTT_PORT=
# MQTT_USERNAME=
# MQTT_PASSWORD=
EOF
echo "[INFO] Created $FOLDER/.env.example"

# --- .gitignore ---
cat > "$FOLDER/.gitignore" << EOF
.env
__pycache__/
*.pyc
EOF
echo "[INFO] Created $FOLDER/.gitignore"

# --- main.py starter ---
cat > "$FOLDER/main.py" << EOF
#!/usr/bin/env python3
"""
Test ${NUM} — ${DESC}
"""

import os

def main():
    print("Test ${NUM} starting…")
    # TODO: implement

if __name__ == "__main__":
    main()
EOF
echo "[INFO] Created $FOLDER/main.py"

echo ""
echo "[DONE] Scaffold ready: $FOLDER/"
echo "       Next steps:"
echo "       1. Edit $FOLDER/README.md"
echo "       2. Add dependencies to $FOLDER/requirements.txt"
echo "       3. Implement $FOLDER/main.py"
echo "       4. git add $FOLDER && git commit -m 'Add test ${NUM}'"
