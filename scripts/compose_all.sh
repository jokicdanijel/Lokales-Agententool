#!/usr/bin/env bash
# scripts/compose_all.sh — Build & start all docker-compose projects under a dist directory
# Usage:
#   scripts/compose_all.sh            # iterate dist/* and run docker compose up -d --build
#   scripts/compose_all.sh --dist mydist --service web --no-build

set -euo pipefail

DIST_DIR="dist"
SERVICE=""
NO_BUILD=0

usage() {
  cat <<EOF
Usage: $0 [--dist DIR] [--service NAME] [--no-build] [--help]

Options:
  --dist DIR     Dist directory containing subprojects (default: dist)
  --service NAME Limit compose up to a single service name inside each project
  --no-build     Do not pass --build to docker compose (only up -d)
  --help         Show this help
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dist)
      DIST_DIR="$2"; shift 2;;
    --service)
      SERVICE="$2"; shift 2;;
    --no-build)
      NO_BUILD=1; shift 1;;
    -h|--help)
      usage;;
    *)
      echo "Unknown arg: $1" >&2; usage;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "docker not found in PATH" >&2; exit 3; }

if [ ! -d "$DIST_DIR" ]; then
  echo "Dist directory not found: $DIST_DIR" >&2
  exit 4
fi

for proj in "$DIST_DIR"/*; do
  [ -d "$proj" ] || continue
  # detect compose file
  if [ -f "$proj/docker-compose.yml" ] || [ -f "$proj/docker-compose.yaml" ] || [ -f "$proj/docker-compose.json" ]; then
    echo "\n===== Processing $proj ====="
    pushd "$proj" >/dev/null

    if [ "$NO_BUILD" -eq 1 ]; then
      if [ -n "$SERVICE" ]; then
        docker compose up -d "$SERVICE"
      else
        docker compose up -d
      fi
    else
      if [ -n "$SERVICE" ]; then
        docker compose up -d --build "$SERVICE"
      else
        docker compose up -d --build
      fi
    fi

    popd >/dev/null
  else
    echo "Skipping $proj — no docker-compose file found"
  fi
done

echo "\nAll done."
