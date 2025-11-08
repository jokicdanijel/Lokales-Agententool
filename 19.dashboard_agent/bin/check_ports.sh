#!/usr/bin/env bash
set -euo pipefail
for p in 12344 12345 12346 12349 8080; do
  echo "---- :$p"
  ss -ltnp "sport = :$p" || true
done
