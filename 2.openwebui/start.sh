#!/usr/bin/env bash
set -euo pipefail

# ins Compose-Verzeichnis wechseln
cd "$(dirname "$0")"

# Start/OpenWebUI
docker compose up -d

# Status zeigen
docker compose ps

echo "OpenWebUI läuft unter: http://127.0.0.1:8080"
