#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source ../../1.portier_openai/venv313/bin/activate
PORT=${1:-12350}
exec uvicorn main_agent:app --host 127.0.0.1 --port "$PORT"
