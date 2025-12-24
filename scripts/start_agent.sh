#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source ../../1.opena1&2_portier/venv313/bin/activate
PORT=${1:-12348}
exec uvicorn main_agent:app --host 127.0.0.1 --port "$PORT"
