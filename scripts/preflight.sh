#!/usr/bin/env bash

set -euo pipefail

# Simple preflight archive check (optionally extendable)
ACTION="${1:-}" 

case "$ACTION" in
  --archive-check|archive-check|""
    ARCHIV_ROOT="/archivp"
    TODAY_DIR="$ARCHIV_ROOT/$(date +%Y)/$(date +%m)/$(date +%d)"

    echo "Archivordner: $TODAY_DIR"
    if [ -d "$TODAY_DIR" ]; then
      ls -1 "$TODAY_DIR"/*CMD.json "$TODAY_DIR"/*RESP.json 2>/dev/null || echo "⚠️ Keine Safepoints gefunden."

      if command -v jq >/dev/null; then
        # Prüfe alle CMD/RESP Dateien auf "strict": true
        found=false
        for f in "$TODAY_DIR"/*CMD.json "$TODAY_DIR"/*RESP.json; do
          [ -f "$f" ] || continue
          found=true
          if jq -e '.strict == true' "$f" >/dev/null 2>&1; then
            echo "OK: $f contains \"strict\": true"
          else
            echo "WARN: $f does NOT contain \"strict\": true"
          fi
        done
        $found || echo "⚠️ Keine Safepoints zum Prüfen gefunden."
      else
        echo "Hinweis: jq nicht installiert, überspringe 'strict' Prüfung."
      fi
    else
      echo "⚠️ Heutiger Archivordner existiert nicht: $TODAY_DIR"
    fi
    ;;
  *)
    echo "Usage: $0 [--archive-check]"
    exit 2
    ;;
esac
