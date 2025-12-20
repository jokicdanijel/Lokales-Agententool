#!/usr/bin/env bash
set -euo pipefail

# Installs OpenTelemetry packages into each agent virtualenv (if present)
# and prints instructions for manual steps.

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
AGENTS=(
  "2.opena3_openwebui"
  "5.opena6_browser"
  "6.opena7_email"
  "7.opena8_whatsapp"
  "8.opena9_telephone"
  "9.opena10_call_tracking"
  "10.opena11_unlock"
  "11.opena12_social_media"
  "12.opena13_influencer"
  "13.opena14_calendar"
  "14.opena15_html"
  "15.opena16_shop"
  "16.opena17_homepagecreator"
)

PKGS=(
  "opentelemetry-api"
  "opentelemetry-sdk"
  "opentelemetry-exporter-otlp"
  "opentelemetry-instrumentation-fastapi"
  "opentelemetry-instrumentation-requests"
  "opentelemetry-instrumentation-logging"
)

for a in "${AGENTS[@]}"; do
  echo "\n--- $a ---"
  if [ -d "$ROOT_DIR/$a/.venv" ]; then
    VENV="$ROOT_DIR/$a/.venv/bin/python"
    echo "Using venv: $VENV"
    "$VENV" -m pip install --upgrade pip setuptools wheel || true
    "$VENV" -m pip install "${PKGS[@]}" || {
      echo "Failed installing into $a venv; try manually: $VENV -m pip install ${PKGS[*]}"
      continue
    }
    echo "Installed OTEL packages into $a/.venv"
  else
    echo "No .venv found in $a; skipping. If agent uses system python, consider manual install in that env."
  fi
done

cat <<'EOF'

Done. Next steps (developer):
 - Start local collector (bin/start_tracing_collector.sh) or ensure OTLP endpoint reachable.
 - Set env vars for agent(s): OTEL_ENABLED=true and OTEL_EXPORTER_OTLP_ENDPOINT=localhost:4317 (grpc) or http://localhost:4318/v1/traces
 - Restart agents (e.g., bin/ops.sh restart or individual start scripts) so they pick up the venv and env.
 - Run smoke test: scripts/tracing_smoke_test.sh

EOF
