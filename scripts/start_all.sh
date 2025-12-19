#!/usr/bin/env bash
set -euo pipefail
# Robustes .env-Parsing (safe für Keys mit = Zeichen)

# --- feste Pfade ---
BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier"
VENV="$BASE/venv313"
PY="$VENV/bin/python3"
PIP="$VENV/bin/pip"
LOGDIR="$BASE/logs"
SYSD="$HOME/.config/systemd/user"

# --- Ports (Policy) ---
# 8080 NUR für OpenWebUI erlaubt
PORT_N8N=12344
PORT_CODEGEN=12347

mkdir -p "$LOGDIR" "$SYSD"

# --- Vorflight: venv & OpenAI-Key prüfen ---
if [[ ! -x "$PY" ]]; then
  echo "[FEHLER] venv313 nicht gefunden unter $PY"
  exit 1
fi
if [[ -f "$BASE/.env" ]]; then
  # shellcheck disable=SC1091
  source "$BASE/.env"
fi
: "${OPENAI_API_KEY:?[FEHLER] OPENAI_API_KEY nicht gesetzt (in .env oder Environment).}"

# --- Systemd-Units schreiben/aktualisieren (User-Session) ---

# OpenWebUI (Port 8080 erlaubt)
cat > "$SYSD/openwebui.service" <<'UNIT'
[Unit]
Description=OpenWebUI
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/env open-webui serve --host 127.0.0.1 --port 8080
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
UNIT

# n8n (Port-Policy-konform)
cat > "$SYSD/n8n.service" <<UNIT
[Unit]
Description=n8n Workflow Automation (Port $PORT_N8N)
After=network.target

[Service]
Type=simple
Environment=WEBHOOK_URL=http://127.0.0.1:$PORT_N8N/
Environment=N8N_HOST=127.0.0.1
Environment=N8N_PORT=$PORT_N8N
Environment=EXECUTIONS_MODE=regular
Environment=NODE_FUNCTION_ALLOW_BUILTIN=*
Environment=NODE_FUNCTION_ALLOW_EXTERNAL=*
ExecStart=/usr/bin/env n8n start
Restart=on-failure

[Install]
WantedBy=default.target
UNIT

# Portier Code-Generator (OpenAI-gestützt)
cat > "$SYSD/portier-codegen.service" <<UNIT
[Unit]
Description=Portier Code Generator API (FastAPI, OpenAI) auf Port $PORT_CODEGEN
After=network.target

[Service]
Type=simple
WorkingDirectory=$BASE/services
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=$BASE/.env
ExecStart=$PY -m uvicorn code_generator:app --host 127.0.0.1 --port $PORT_CODEGEN
Restart=on-failure

[Install]
WantedBy=default.target
UNIT

# Hinweis: opena1 läuft bereits als eigener Dienst (Koordinator).
# Optional: falls vorhanden, weitere Portier-Dienste aktivieren
if systemctl --user list-unit-files | grep -q '^opena1\.service'; then
  WANT_OPENA1=1
else
  WANT_OPENA1=0
fi

# --- Services-Verzeichnis & Abhängigkeiten ---
mkdir -p "$BASE/services"

# Code-Generator sicherstellen (Dependencies minimal)
if [[ ! -f "$BASE/services/code_generator.py" ]]; then
  echo "[INFO] code_generator.py fehlt – wird NICHT automatisch erzeugt. Bitte Datei bereitstellen."
fi

# --- Python-Dependencies (nur falls nötig, ohne 8080) ---
$PIP -q install --upgrade pip wheel >/dev/null
$PIP -q install fastapi "uvicorn[standard]" "pydantic>=2" openai >/dev/null || {
  echo "[WARN] Python-Abhängigkeiten konnten nicht vollständig installiert werden."
}

# --- systemd daemon reload ---
systemctl --user daemon-reload

# --- Dienste starten/aktivieren ---
systemctl --user enable --now openwebui.service   2>&1 | tee -a "$LOGDIR/openwebui.boot.log"
systemctl --user enable --now n8n.service         2>&1 | tee -a "$LOGDIR/n8n.boot.log"
systemctl --user enable --now portier-codegen.service 2>&1 | tee -a "$LOGDIR/codegen.boot.log"

if (( WANT_OPENA1 == 1 )); then
  systemctl --user enable --now opena1.service   2>&1 | tee -a "$LOGDIR/opena1.boot.log"
fi

# --- Statusübersicht ---
echo
echo "== STATUS =="
systemctl --user --no-pager --plain status openwebui.service | sed -n '1,8p' || true
systemctl --user --no-pager --plain status n8n.service       | sed -n '1,8p' || true
systemctl --user --no-pager --plain status portier-codegen.service | sed -n '1,8p' || true
if (( WANT_OPENA1 == 1 )); then
  systemctl --user --no-pager --plain status opena1.service | sed -n '1,8p' || true
fi

echo
echo "[OK] Stack gestartet:"
echo " - OpenWebUI        -> http://127.0.0.1:8080  (nur OpenWebUI nutzt 8080)"
echo " - n8n              -> http://127.0.0.1:$PORT_N8N"
echo " - Code-Generator   -> http://127.0.0.1:$PORT_CODEGEN/docs"
echo " - Koordinator      -> opena1.service (falls vorhanden)"
echo
echo "Hinweis: 'Unllama' wird nicht verwendet. Agenten laufen über OpenAI-API."

