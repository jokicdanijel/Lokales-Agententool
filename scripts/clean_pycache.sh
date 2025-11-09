#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
find "$ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "Pycache bereinigt."
