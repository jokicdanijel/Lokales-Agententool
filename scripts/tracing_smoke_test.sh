#!/usr/bin/env bash
set -euo pipefail

# Smoke test: verify Jaeger collector reachable and an agent emits a span via init_tracing
COLLECTOR_HTTP="http://localhost:16686"
OTLP_HTTP="http://localhost:4318/v1/traces"
OTLP_GRPC="localhost:4317"

echo "Checking Jaeger UI at $COLLECTOR_HTTP..."
if ! curl -sSf "$COLLECTOR_HTTP" >/dev/null; then
  echo "Jaeger UI not reachable at $COLLECTOR_HTTP" >&2
  exit 2
fi

# Use python to import pkg.observability and emit a test span
python3 - <<'PY'
import os, time, sys
sys.path.insert(0, 'src')
from pkg.observability import init_tracing
from opentelemetry import trace

# Prefer gRPC if available
endpoint = os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', os.environ.get('OTLP', 'localhost:4317'))
print('Using endpoint:', endpoint)
ok = init_tracing(service_name='tracing_smoke_test', enabled=True, endpoint=endpoint)
print('init_tracing ok:', ok)
if not ok:
    sys.exit(3)
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span('smoke-test-span'):
    time.sleep(0.1)
print('span emitted')
PY

sleep 2

# Query Jaeger for the test service
echo "Querying Jaeger for tracing_smoke_test spans..."
res=$(curl -sS "$COLLECTOR_HTTP/api/traces?service=tracing_smoke_test&limit=10")
if echo "$res" | grep -q 'smoke-test-span'; then
  echo "Smoke test success: span found in Jaeger"
  exit 0
else
  echo "Smoke test warning: span not found in Jaeger (may be delayed)" >&2
  echo "$res" | head -n 50
  exit 4
fi
