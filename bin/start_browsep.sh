#!/usr/bin/env bash
set -euo pipefail

NAME="browsep"
PORT=12370
LOGFILE="logs/${NAME}.nohup.log"

# Ensure logs dir exists
mkdir -p logs

nohup uvicorn 6.browsep_portier.main_browsep:app --host 127.0.0.1 --port ${PORT} --reload > ${LOGFILE} 2>&1 &

echo "Started ${NAME} on port ${PORT}, logfile: ${LOGFILE}"
