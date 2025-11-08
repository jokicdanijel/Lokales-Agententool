#!/usr/bin/env bash
set -euo pipefail

# --- Settings (bindend) ---
PY_VER="${PY_VER:-3.13}"
VENV_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.portier_openai/venv313"

echo "[VENV] Bootstrap für Python ${PY_VER} → ${VENV_DIR}"

# 1) Systemvoraussetzungen (nur falls nötig)
if ! command -v python3 >/dev/null 2>&1; then
  echo "[VENV] python3 fehlt – Installation abbrechen (manuell bereitstellen)."
  exit 1
fi

# ensurepip/venv bereitstellen (Debian/Ubuntu benötigt *-venv Paket)
if ! python3 -c "import venv" >/dev/null 2>&1; then
  echo "[VENV] python3-venv wird installiert (sudo erforderlich)…"
  sudo apt update
  sudo apt install -y "python${PY_VER}-venv" python3-pip
fi

# 2) Neu anlegen oder aktualisieren
if [ -d "${VENV_DIR}" ]; then
  echo "[VENV] Bestehendes venv gefunden."
else
  echo "[VENV] Erstelle venv…"
  "python${PY_VER}" -m venv "${VENV_DIR}"
fi

# 3) Aktivieren
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# 4) Pip upgraden und Kernpakete installieren
python -V
pip install --upgrade pip wheel setuptools

# Portier-Minimalabhängigkeiten (FastAPI-Bridge auf Port-Policy-Ports nutzbar)
pip install "fastapi==0.115.5" "uvicorn[standard]==0.38.0" "pydantic==2.*"

echo
echo "[VENV] Fertig. Aktivieren mit:"
echo "source ${VENV_DIR}/bin/activate"
echo
echo "[VENV] Beispielstart einer lokalen Bridge (Port-Policy-konform, NICHT 8080):"
cat <<'CMD'
uvicorn portier_fs_bridge:app --host 127.0.0.1 --port 12346
CMD

