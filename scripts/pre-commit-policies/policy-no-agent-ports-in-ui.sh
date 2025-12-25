#!/usr/bin/env bash
set -euo pipefail

files="$(git diff --cached --name-only | tr "\n" " ")"
[ -z "$files" ] && exit 0

targets="$(echo "$files" | tr " " "\n" | grep -E '^apps/.*\.html$' || true)"
[ -z "$targets" ] && exit 0

bad=0
for f in $targets; do
  c="$(git show ":$f")"
  if echo "$c" | grep -nE ':(123[4-9][0-9]|1239[0-9])' >/dev/null; then
    echo "❌ direct agent-port link detected in $f (must route via opena20)"
    bad=1
  fi
done

exit $bad
