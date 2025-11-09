#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo "Erzeuge neuen Token in .env ..."
  python3 - <<'PY'
import secrets, sys
open(".env","w").write(secrets.token_urlsafe(32))
print("OK")
PY
fi
cat "$ROOT_DIR/.env"
