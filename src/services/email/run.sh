#!/usr/bin/env bash
export SERVICE_NAME="email"
export PROGRAM_TARGET="emailp"
export PORT="12351"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
