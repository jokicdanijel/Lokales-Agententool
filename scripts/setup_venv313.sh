#!/usr/bin/env bash
set -euo pipefail

BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
VENV="$BASE/1.opena1&2_portier/venv313"

mkdir -p "$BASE/1.opena1&2_portier"

# Systemabhängige Voraussetzungen
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 nicht gefunden." >&2
  exit 1
fi
if ! python3 -m ensurepip --version >/dev/null 2>&1; then
  sudo apt update
  sudo apt install -y python3-venv python3-pip
fi

# venv313 erstellen/aktualisieren
python3 -m venv "$VENV"
source "$VENV/bin/activate"

python -m pip install --upgrade pip
python -m pip install "fastapi==0.115.5" "uvicorn[standard]==0.38.0" "pydantic==2.*"

echo "venv313 bereit unter: $VENV"
python -V
pip -V
