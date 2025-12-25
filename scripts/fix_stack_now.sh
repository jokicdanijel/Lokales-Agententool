#!/usr/bin/env bash
# [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
# ELION Fix Stack Now – Phase 4.1 (strict:true)
# Startet Kern-Dienste in Reihenfolge, validiert Ports, prüft Health
set -Eeuo pipefail

BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
DASH="$BASE/19.dashboard_agent"
LOG="$DASH/logs/fix_stack_now.log"
mkdir -p "$DASH/logs"

POOL_START=12344
POOL_END=12399
FORBID_PORT=8080

# === UTILITIES ===
ts(){ date +"%Y-%m-%dT%H:%M:%S%z"; }
log(){ echo "[$(ts)] $*" | tee -a "$LOG"; }

need(){
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: Missing command: $1" >&2
    exit 127
  }
}

in_pool(){
  local p=$1
  [[ $p -ge $POOL_START && $p -le $POOL_END ]]
}

port_free(){
  ! ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$1\$" 2>/dev/null || return 1
}

health(){
  local p=$1 name=$2
  timeout 1 curl -fsS "http://127.0.0.1:$p/health" 2>/dev/null \
    | sed -E 's/.*"status":"?([^",}]+).*/\1/' || echo "down"
}

# === CHECKS ===
need curl
need ss
need awk
need grep
need timeout

policy_check(){
  log "Policy-Check: Pool ${POOL_START}-${POOL_END}, Port ${FORBID_PORT} verboten"

  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${FORBID_PORT}\$"; then
    log "❌ VERSTOSS: Port ${FORBID_PORT} bereits belegt!"
    log "Port ${FORBID_PORT} ist exklusiv für OpenWebUI (Loopback). Bitte sofort beenden."
    return 2
  fi

  log "✅ Port-Policy OK: 8080 frei"
}

start_if_missing(){
  local port="$1" name="$2" script="$3"
  local st

  # Health prüfen (nonblocking)
  st="$(health "$port" "$name" 2>/dev/null || echo "down")"

  if [[ "$st" =~ healthy|ok ]]; then
    log "✅ $name bereits online (:$port, status: $st)"
    return 0
  fi

  # Port-Policy
  if ! in_pool "$port"; then
    log "❌ POLICY FAIL: $name Port $port außerhalb Pool ${POOL_START}-${POOL_END}"
    return 3
  fi

  # Port belegt?
  if ! port_free "$port"; then
    log "ℹ️  Port :$port belegt (vermutlich von $name selbst). Überspringe Start."
    return 0
  fi

  log "▶️  Starte $name …"
  if ! (cd "$DASH/bin" && bash "$script"); then
    log "❌ Start-Script $script fehlgeschlagen"
    return 4
  fi

  # Warte auf Health
  for i in {1..12}; do
    sleep 0.8
    st="$(health "$port" "$name" 2>/dev/null || echo "down")"
    if [[ "$st" =~ healthy|ok ]]; then
      log "✅ $name up nach $((i * 80))ms (:$port)"
      return 0
    fi
  done

  log "❌ $name bleibt down nach 10s (:$port, last status: $st)"
  return 1
}

tail_logs(){
  local f
  echo -e "\n=== LOG TAILS ===" | tee -a "$LOG"

  for f in "$DASH/logs/"*.log "$DASH/logs/"*.out "$DASH/logs/"*.err; do
    [[ -f "$f" ]] || continue
    echo -e "\n--- $(basename "$f") (last 40 lines) ---" | tee -a "$LOG"
    tail -n 40 "$f" 2>/dev/null | tee -a "$LOG" || true
  done
}

print_health_matrix(){
  echo -e "\n╔═══════════════════════════════════════╗" | tee -a "$LOG"
  echo "║        ELION HEALTH MATRIX             ║" | tee -a "$LOG"
  echo "╚═══════════════════════════════════════╝" | tee -a "$LOG"

  local status
  for row in "opena1:12344" "opena2:12345" "kordp:12346" "dashboard:12349" "bridge:12351"; do
    local name="${row%%:*}"
    local port="${row##*:}"
    status="$(health "$port" "$name" 2>/dev/null || echo "down")"

    if [[ "$status" =~ healthy|ok ]]; then
      printf "  ✅ %-12s :%-5s → %s\n" "$name" "$port" "$status" | tee -a "$LOG"
    else
      printf "  ❌ %-12s :%-5s → %s\n" "$name" "$port" "$status" | tee -a "$LOG"
    fi
  done

  echo "║ strict:true                            ║" | tee -a "$LOG"
  echo "╚═══════════════════════════════════════╝" | tee -a "$LOG"
}

# === MAIN ===
main(){
  log "╔════════════════════════════════════════╗"
  log "║   ELION fix_stack_now (Phase 4.1)      ║"
  log "║   strict:true | Append-only Logs       ║"
  log "╚════════════════════════════════════════╝"

  # Policy
  if ! policy_check; then
    log "FATAL: Port-Policy verletzt"
    exit 2
  fi

  # System Mode anzeigen
  log ""
  log "=== System Mode Status ==="
  if [[ -x "$BASE/bin/system_mode_switch.sh" ]]; then
    (cd "$BASE" && bash bin/system_mode_switch.sh show 2>&1 || true) | sed 's/^/  /' | tee -a "$LOG" || true
  else
    log "  (system_mode_switch.sh nicht gefunden)"
  fi

  # Startup-Reihenfolge
  log ""
  log "=== Startup Sequence (Reihenfolge: opena2 → opena1 → kordp → dashboard → bridge) ==="

  start_if_missing 12345 "opena2"                   "start_opena2.sh"                   || true
  start_if_missing 12344 "opena1"                   "start_opena1.sh"                   || true
  start_if_missing 12346 "kordp"                    "start_kordp.sh"                    || true
  start_if_missing 12349 "dashboard (opena19)"      "start_opena19.sh"                  || true

  if [[ -x "$DASH/bin/start_openwebui_adapter.sh" ]]; then
    start_if_missing 12351 "bridge (openwebui-adapter)" "start_openwebui_adapter.sh" || true
  else
    log "  (openwebui_adapter.sh nicht vorhanden – überspringe)"
  fi

  # Health Matrix
  print_health_matrix

  # Port-Sanity
  log ""
  log "=== Port Sanity Check ==="
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${FORBID_PORT}\$"; then
    log "❌ WARNUNG: Immer noch ein Dienst auf Port ${FORBID_PORT}!"
  else
    log "✅ Port ${FORBID_PORT} frei (gut)"
  fi

  # Logs
  tail_logs

  log ""
  log "=== FIX COMPLETE ==="
  log "Logs append-only: $LOG"
  log "strict:true"
}

main "$@"
