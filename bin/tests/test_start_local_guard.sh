#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ROOT_DIR/bin/start_opena_local.sh"

echo "Testing CI guard (should exit 2)..."
CI=1 bash "$SCRIPT" . 2>/dev/null || rc=$?
if [ "${rc:-0}" -ne 2 ]; then
  echo "CI guard failed: expected exit 2, got $rc" >&2
  exit 1
fi
echo "CI guard OK"

echo "Testing opt-in guard (should exit 3)..."
unset CI
bash "$SCRIPT" . 2>/dev/null || rc=$?
if [ "${rc:-0}" -ne 3 ]; then
  echo "Opt-in guard failed: expected exit 3, got $rc" >&2
  exit 2
fi
echo "Opt-in guard OK"

echo "Guard tests passed ✅"
