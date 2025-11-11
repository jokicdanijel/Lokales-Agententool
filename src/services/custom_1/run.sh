#!/usr/bin/env bash
export SERVICE_NAME="custom_1"
export PROGRAM_TARGET="cust1"
export PORT="12363"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
