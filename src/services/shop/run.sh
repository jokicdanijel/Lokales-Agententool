#!/usr/bin/env bash
export SERVICE_NAME="shop"
export PROGRAM_TARGET="shopp"
export PORT="12356"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
