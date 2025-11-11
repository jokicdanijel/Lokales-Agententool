#!/usr/bin/env bash
export SERVICE_NAME="phone"
export PROGRAM_TARGET="phonep"
export PORT="12353"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
