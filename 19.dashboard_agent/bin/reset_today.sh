#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
find "$ROOT/archiv/$(date +%Y)/$(date +%m)/$(date +%d)" -type f 2>/dev/null || echo "Heute noch keine Dateien gefunden."
