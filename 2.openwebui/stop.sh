#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

sg docker -c 'docker compose down'
echo "✅ OpenWebUI gestoppt"
