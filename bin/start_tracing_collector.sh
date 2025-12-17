#!/usr/bin/env bash
set -euo pipefail

echo "Starting local OpenTelemetry collector (docker-compose.otel.yml)..."
docker compose -f "$(dirname "$0")/../docker-compose.otel.yml" up -d

echo "Collector started. Exposed ports: 4317 (gRPC), 4318 (HTTP OTLP)"
