#!/usr/bin/env bash
export SERVICE_NAME="local_archiv"
export PROGRAM_TARGET="locp"
export PORT="12362"
exec python3 "$(dirname "${BASH_SOURCE[0]}")/main.py" "$@"
