#!/usr/bin/env bash
set -euo pipefail

# Konfiguration
HOST="127.0.0.1"
PORT="8001"
BASE="http://${HOST}:${PORT}"
USE_JQ=true

# Hilfsfunktion: Tools sicherstellen
ensure_tools() {
  if ! command -v curl >/dev/null; then
    echo "curl nicht gefunden. Installiere es mit: sudo apt update && sudo apt install -y curl"
    exit 1
  fi
  if command -v jq >/dev/null; then
    USE_JQ=true
  else
    USE_JQ=false
  fi
}

ensure_tools

echo "==== LocalAgent-Pro Backend-Check (Port ${PORT}) ===="

# 1) Port lauscht prüfen
if ss -ltnp 2>/dev/null | grep -q -- "\:${PORT}"; then
  echo "✓ Port ${PORT} lauscht."
else
  echo "⚠ Port ${PORT} lauscht NICHT. Starte ggf den Server neu."
fi

# 2) Health-Check
HEALTH_JSON=""
if HEALTH_JSON=$(curl -sS "${BASE}/health" 2>/dev/null || true); then
  if [ -n "$HEALTH_JSON" ]; then
    if command -v jq >/dev/null; then
      echo "Health (formatted):"
      echo "$HEALTH_JSON" | jq .
    else
      echo "Health (raw):"
      echo "$HEALTH_JSON"
    fi
  else
    echo "Warn: Health-Antwort leer."
  fi
else
  echo "Warn: Health-Endpunkt nicht erreichbar."
fi

# 3) Modell-Endpunkt prüfen
MODELS_JSON=""
if MODELS_JSON=$(curl -sS "${BASE}/v1/models" 2>/dev/null || true); then
  if [ -n "$MODELS_JSON" ]; then
    if command -v jq >/dev/null; then
      echo "Models:"
      echo "$MODELS_JSON" | jq .
    else
      echo "Models (raw):"
      echo "$MODELS_JSON"
    fi
  else
    echo "Warn: Models-Endpunkt leer."
  fi
fi

# 4) Chat API testen
CHAT_JSON=""
CHAT_PAYLOAD='{"messages":[{"role":"user","content":"Hallo LocalAgent-Pro!"}]}'
CHAT_JSON=$(curl -sS -X POST "${BASE}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "$CHAT_PAYLOAD" 2>/dev/null || true)
if [ -n "$CHAT_JSON" ]; then
  if command -v jq >/dev/null; then
    echo "Chat-Antwort (OpenAI-kompatibel):"
    echo "$CHAT_JSON" | jq .
  else
    echo "Chat-Antwort (raw):"
    echo "$CHAT_JSON"
  fi
else
  echo "Warn: Chat-Endpunkt nicht erreichbar oder Antwort leer."
fi

# 5) Tool-Test-Endpunkt
TOOL_JSON=""
TOOL_PAYLOAD='{"prompt": "Liste Verzeichnis . auf"}'
TOOL_JSON=$(curl -sS -X POST "${BASE}/test" \
  -H "Content-Type: application/json" \
  -d "$TOOL_PAYLOAD" 2>/dev/null || true)
if [ -n "$TOOL_JSON" ]; then
  if command -v jq >/dev/null; then
    echo "Test-Endpunkt (Tool-Ausgabe):"
    echo "$TOOL_JSON" | jq .
  else
    echo "Test-Endpunkt (raw):"
    echo "$TOOL_JSON"
  fi
else
  echo "Warn: Test-Endpunkt nicht erreichbar."
fi

echo "==== Ende ===="
