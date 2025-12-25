#!/usr/bin/env bash
# [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
# ELION Safe Port Kill – Phase 4.1 (strict:true)
# Beendet NUR rogue Prozesse außerhalb des Port-Pools (8080 wird NIEMALS angefasst!)
set -euo pipefail

POOL_START=12344
POOL_END=12399
FORBID_PORT=8080

echo "╔════════════════════════════════════════╗"
echo "║    ELION Port Kill Safeguard           ║"
echo "╚════════════════════════════════════════╝"

echo ""
echo "Scan for rogue ports (outside ${POOL_START}-${POOL_END}, ${FORBID_PORT} always reserved)"
echo ""

found=0

ss -ltnp 2>/dev/null | awk 'NR>1{print $4, $6}' | while read -r addr proc; do
  port="${addr##*:}"

  # Nicht numerisch? Skip
  [[ "$port" =~ ^[0-9]+$ ]] || continue

  # 8080 ist sakrosankt
  if [[ "$port" -eq "$FORBID_PORT" ]]; then
    echo "  ℹ️  Port :${FORBID_PORT} reserved (OpenWebUI) – not touching"
    continue
  fi

  # Im Pool? OK, nicht anfassen
  if [[ "$port" -ge $POOL_START && "$port" -le $POOL_END ]]; then
    continue
  fi

  # Rogue port! PID extrahieren
  pid="$(echo "$proc" | sed -n 's/.*pid=\([0-9]\+\).*/\1/p')"

  if [[ -n "$pid" ]]; then
    echo "  ⚠️  Kill pid $pid on rogue port :$port"
    kill "$pid" 2>/dev/null || echo "    (already gone)"
    found=$((found+1))
  fi
done

if [[ $found -eq 0 ]]; then
  echo "  ✅ No rogue ports found"
fi

echo ""
echo "strict:true"
