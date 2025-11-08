#!/usr/bin/env bash
# [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
# ELION Health Matrix – Phase 4.1 (strict:true)
# Kompakte Ampel-Übersicht über /health-Endpunkte
set -euo pipefail

check(){
  local port="$1" name="$2"
  local status
  
  status=$(timeout 1 curl -fsS "http://127.0.0.1:${port}/health" 2>/dev/null \
    | sed -E 's/.*"status":"?([^",}]+).*/\1/' || echo "down")
  
  if [[ "$status" =~ healthy|ok ]]; then
    printf "  ✅ %-12s :%-5s  %s\n" "$name" "$port" "$status"
  else
    printf "  ❌ %-12s :%-5s  %s\n" "$name" "$port" "$status"
  fi
}

echo "╔════════════════════════════════════════╗"
echo "║       ELION HEALTH MATRIX              ║"
echo "╚════════════════════════════════════════╝"

check 12344 "opena1"
check 12345 "opena2"
check 12346 "kordp"
check 12349 "dashboard"
check 12351 "bridge"

echo "  strict:true"
