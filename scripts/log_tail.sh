#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tail -n 50 -F \
  "$ROOT/logs/dashboard.nohup.log" \
  "$ROOT/logs/opena1.nohup.log" \
  "$ROOT/logs/opena2.nohup.log" \
  "$ROOT/logs/kordp.nohup.log"
