#!/usr/bin/env bash
# [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
# ELION Env Probe – Phase 4.1 (strict:true)
# Prüft .env-Schlüssel (maskiert Werte!)
set -euo pipefail

BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"

need_file(){
  local f="$1"
  if [[ -f "$f" ]]; then
    echo "✅ vorhanden: $f"
    return 0
  else
    echo "❌ fehlt: $f"
    return 1
  fi
}

mask_present(){
  local k="$1" file="$2"
  if grep -qE "^${k}=" "$file" 2>/dev/null; then
    echo "  ✅ $k → gesetzt"
  else
    echo "  ❌ $k → FEHLT"
  fi
}

echo "╔════════════════════════════════════════╗"
echo "║       ELION ENV PROBE                  ║"
echo "╚════════════════════════════════════════╝"

echo ""
echo "=== Dashboard .env ==="
DENV="$BASE/19.dashboard_agent/.env"

if need_file "$DENV"; then
  mask_present "DASHBOARD_ADMIN_TOKEN" "$DENV"
  mask_present "TELEGRAM_BOT_TOKEN" "$DENV" || true
  mask_present "TELEGRAM_WEBHOOK_SECRET" "$DENV" || true
  mask_present "TELEGRAM_ALLOWED_USERS" "$DENV" || true
else
  echo "ERROR: .env nicht gefunden. Bitte erstellen:"
  echo "  cp 19.dashboard_agent/.env.example 19.dashboard_agent/.env"
  echo "  # Dann Token/Secrets setzen"
  exit 1
fi

echo ""
echo "strict:true"
