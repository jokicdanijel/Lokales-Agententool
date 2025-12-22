#!/usr/bin/env bash
set -euo pipefail

BASE=${BASE:-http://127.0.0.1:12349}

echo "Checking opena20 /health..."
if curl -sSf "$BASE/health" >/dev/null; then
  echo "/health OK"
else
  echo "/health FAILED" >&2
  exit 2
fi

echo "Checking dashboard HTML at /..."
if curl -sSf "$BASE/" | grep -q "<html"; then
  echo "/ OK"
else
  echo "/ FAILED" >&2
  exit 3
fi

echo "Smoke tests passed"
