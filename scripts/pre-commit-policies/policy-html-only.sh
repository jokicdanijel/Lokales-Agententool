#!/usr/bin/env bash
set -euo pipefail

files="$(git diff --cached --name-only | tr "\n" " ")"
[ -z "$files" ] && exit 0

targets="$(echo "$files" | tr " " "\n" | grep -E '^apps/.*\.html$' || true)"
[ -z "$targets" ] && exit 0

bad=0
for f in $targets; do
  c="$(git show ":$f")"
  echo "$c" | grep -qi "<script" && echo "❌ <script> forbidden in $f" && bad=1
  echo "$c" | grep -qi "style=" && echo "❌ inline style= forbidden in $f" && bad=1
  echo "$c" | grep -qi "<link[^>]*rel=[\"'']stylesheet" && echo "❌ stylesheet link forbidden in $f" && bad=1
done

exit $bad
