#!/usr/bin/env bash
# ============================================================================
# verify_baseline_and_discovery.sh
# Gate für PORTIER 3.0 / ELION Hyper-Dashboard
#
# Aufgaben:
# - Prüft Existenz der system_baseline.yaml
# - Führt deterministische Agenten-Discovery aus
# - Bricht bei JEDEM Fehler hart ab (Exit 1)
# - Erzeugt reproduzierbare Artefakte
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASELINE="${ROOT}/system_baseline.yaml"
DISCOVER="${ROOT}/scripts/discover_agents.py"
ARTIFACTS="${ROOT}/artifacts"

echo "[GATE] ROOT=${ROOT}"

if [[ ! -f "${BASELINE}" ]]; then
  echo "[GATE][FAIL] Missing system_baseline.yaml at ${BASELINE}" >&2
  exit 1
fi

if [[ ! -f "${DISCOVER}" ]]; then
  echo "[GATE][FAIL] Missing discovery script at ${DISCOVER}" >&2
  exit 1
fi

mkdir -p "${ARTIFACTS}"

echo "[GATE] Running deterministic agent discovery…"
python3 "${DISCOVER}"

echo "[GATE] OK — Baseline & Discovery verified"
