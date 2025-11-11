#!/usr/bin/env bash
export SERVICE_NAME="custom_2"
export PROGRAM_TARGET="cust2"
export PORT="12364"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
