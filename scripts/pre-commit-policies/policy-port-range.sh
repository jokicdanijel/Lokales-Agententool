#!/usr/bin/env bash
set -euo pipefail

files="$(git diff --cached --name-only | tr "\n" " ")"
[ -z "$files" ] && exit 0

targets="$(echo "$files" | tr " " "\n" | grep -E '^(docker-compose.*\.ya?ml|infrastructure/nginx/.*\.conf)$' || true)"
[ -z "$targets" ] && exit 0

bad=0
for f in $targets; do
  if git show ":$f" | grep -nE '(^|[^0-9])8080(:|[^0-9])' >/dev/null; then
    echo "❌ Forbidden port 8080 detected in $f"
    bad=1
  fi

  while read -r line; do
    host="$(echo "$line" | sed -nE 's/.*- *"?([0-9]{2,5}):([0-9]{2,5}).*/\1/p')"
    [ -z "$host" ] && continue
    if [ "$host" -lt 12344 ] || [ "$host" -gt 12399 ]; then
      echo "❌ Host port out of range (12344-12399): $host in $f"
      bad=1
    fi
  done < <(git show ":$f" | grep -nE '^- *"?[0-9]{2,5}:[0-9]{2,5}' | cut -d: -f2-)
done

exit $bad
