#!/usr/bin/env bash
export SERVICE_NAME="whatsapp"
export PROGRAM_TARGET="whatp"
export PORT="12352"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
