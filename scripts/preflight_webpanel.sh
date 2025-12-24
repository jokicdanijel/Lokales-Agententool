#!/usr/bin/env bash
set -euo pipefail

# Wrapper around scripts/preflight_webpanel.py
ROOT="${ROOT:-.}"
OUT_DIR="${OUT_DIR:-artifacts}"
PY="${PYTHON:-python3}"

exec "$PY" "scripts/preflight_webpanel.py" --root "$ROOT" --out-dir "$OUT_DIR" "$@"
