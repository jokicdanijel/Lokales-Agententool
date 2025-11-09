#!/usr/bin/env bash
# [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
# ELION Stack Status Badge – Phase 4.1 (strict:true)
# Einzeiler-Badge für Statusleisten/Prompts
set -euo pipefail

ok=0
total=0

probe(){
  local p=$1
  timeout 1 curl -fsS "http://127.0.0.1:$p/health" >/dev/null 2>&1 && return 0 || return 1
}

for p in 12344 12345 12346 12349 12351; do
  total=$((total+1))
  probe "$p" 2>/dev/null && ok=$((ok+1)) || true
done

echo "ELION: $ok/$total services up | strict:true"
