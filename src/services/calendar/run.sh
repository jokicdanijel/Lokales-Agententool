#!/usr/bin/env bash
export SERVICE_NAME="calendar"
export PROGRAM_TARGET="kalp"
export PORT="12354"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
