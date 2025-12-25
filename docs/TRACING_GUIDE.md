# OpenTelemetry Tracing Guide – ELION Hyper-Dashboard

## Overview

OpenTelemetry (OTEL) ermöglicht verteilte Tracing über alle Services im ELION-System. Dies hilft bei:

- 🔍 Performance Monitoring
- 🐛 Distributed Debugging
- 📊 Request Flow Visualization
- ⚠️ Error Tracking & Alerting
- 📈 Latency Analysis

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Services                                 │
│ ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│ │ telegram_multi   │  │  opena6_browser  │  │ opena20    │ │
│ │ (port 8000)      │  │ (port 12350)     │  │ (port 12349)
│ │ +OpenTelemetry   │  │ +OpenTelemetry   │  │ +OTEL      │ │
│ └────────┬─────────┘  └────────┬─────────┘  └────────┬───┘ │
└─────────┼────────────────────────┼────────────────────┼─────┘
          │                        │                    │
          │ OTLP HTTP              │ OTLP HTTP          │
          │ (port 4318)            │ (port 4318)        │
          └────────────────┬───────┴────────────────────┘
                           │
                ┌──────────▼──────────┐
                │ OTLP Collector      │
                │ Grafana LGTM        │
                │ - Traces (Tempo)    │
                │ - Logs (Loki)       │
                │ - Metrics (Prom)    │
                └──────────┬──────────┘
                           │
                ┌──────────▼──────────┐
                │  Grafana UI         │
                │  localhost:3000     │
                └─────────────────────┘
```

---

## Quick Start

### 1. Start OTLP Collector

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Option A: Use provided script
./bin/start_tracing_collector.sh

# Option B: Manual docker-compose
docker-compose -f docker-compose.otel.yml up -d

# Option C: Via Makefile
make tracing-up
```

Verify collector is running:

```bash
curl -v http://127.0.0.1:4318/v1/traces
# Expected: 200 OK (empty trace list is fine)
```

### 2. Enable Tracing in Services

Update `.env`:

```env
# Global OpenTelemetry settings
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_SERVICE_NAME=elion-dashboard

# Per-service (if needed):
# telegram_multi service
OTEL_SERVICE_NAME=telegram_multi
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
```

### 3. Restart Services with Tracing

```bash
# Telegram Multi-Bot
cd telegram_multi && docker-compose down && docker-compose up -d

# opena6 Browser Agent
cd 5.opena6_browser && docker-compose down && docker-compose up -d

# Dashboard (opena20)
cd 19.opena20_dashboard_agent && python main_dashboard.py

# Verify
python3 tracing/check_tracing.py
```

Expected output:

```
Tracing enabled: True
```

### 4. Access Grafana

Open browser: **http://localhost:3000**

- Default credentials: `admin` / `admin`
- Navigate to **Explore** → select **Tempo** datasource
- View traces by service name or request ID

---

## Instrumentation Details

### FastAPI Services (telegram_multi, opena6, opena20)

These services use `pkg.observability.init_tracing()`:

```python
# In main.py
from pkg.observability import init_tracing

try:
    init_tracing(app, service_name="telegram_multi")
except Exception as e:
    logger.debug("Tracing not initialized: %s", e)
```

**Instrumented Components:**

- ✅ HTTP requests/responses (FastAPI)
- ✅ External HTTP calls (requests library)
- ✅ Logging events
- ✅ Database queries (if SQLAlchemy instrumented)

### Trace Context Propagation

Traces are automatically propagated via HTTP headers:

```
traceparent: 00-{trace-id}-{span-id}-01
```

Example request path:

```
User Request
  ↓ (traceparent header)
telegram_multi
  ↓ (traceparent + new span)
External API
  ↓ (traceparent + new span)
PostgreSQL
```

---

## Configuration

### Environment Variables

```env
# Enable/disable tracing globally
OTEL_ENABLED=false

# OTLP Collector endpoint
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318

# Service identifier (shown in Grafana)
OTEL_SERVICE_NAME=telegram_multi

# Log level for OTEL components
OTEL_LOG_LEVEL=INFO
```

### Per-Service Configuration

**telegram_multi/.env:**

```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_SERVICE_NAME=telegram_multi_api
```

**5.opena6_browser/.env:**

```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_SERVICE_NAME=opena6_browser
```

**19.opena20_dashboard_agent/.env:**

```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_SERVICE_NAME=opena20_dashboard
```

---

## Querying Traces

### In Grafana Tempo

1. Navigate to **Explore** panel
2. Select **Tempo** datasource
3. Choose query type:

**By Service Name:**

```
{ resource.service.name = "telegram_multi" }
```

**By Span Name:**

```
{ name = "POST /admin/register-bot" }
```

**By Duration (slow requests):**

```
{ duration > 1000ms }
```

**By Status (errors):**

```
{ status = error }
```

### Example: Trace Bot Registration

1. Run registration:

   ```bash
   bash scripts/register_bots.sh http://127.0.0.1:8000
   ```

2. In Grafana, query:

   ```
   { resource.service.name = "telegram_multi" && name = "POST /admin/register-bot" }
   ```

3. View trace details:
   - Total duration
   - Span breakdown (FastAPI → requests → Telegram API)
   - Error messages (if any)

---

## Verification & Testing

### Check Tracing Helper

```bash
python3 tracing/check_tracing.py
```

Output when enabled:

```
Tracing enabled: True
```

Output when disabled or packages missing:

```
Tracing enabled: False
```

### Run Tracing Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tracing presence test
python -m pytest evaluation/tests/test_tracing_presence.py -v

# Run service-specific tests
python -m pytest evaluation/tests/test_tracing_opena8.py -v
```

### Manual OTLP Endpoint Check

```bash
# Check if collector receives traces
curl -s http://127.0.0.1:4318/v1/traces | jq .

# Expected response (can be empty):
# { "resourceSpans": [] }
```

---

## Troubleshooting

### Collector Won't Start

```bash
# Check if port 4318 is in use
lsof -i :4318

# Kill existing process if needed
kill -9 $(lsof -t -i:4318)

# Check docker logs
docker-compose -f docker-compose.otel.yml logs -f grafana-otel

# Verify compose file
cat docker-compose.otel.yml
```

### No Traces Appearing in Grafana

1. **Check if OTEL packages are installed:**

   ```bash
   python3 -c "import opentelemetry; print('OK')"
   ```

2. **Check if OTEL_ENABLED is true:**

   ```bash
   grep OTEL_ENABLED .env
   ```

3. **Check if services are sending to collector:**

   ```bash
   docker-compose logs api | grep -i "otl\|telemetry"
   ```

4. **Verify endpoint is reachable:**
   ```bash
   curl http://127.0.0.1:4318/v1/traces
   ```

### Services Won't Start with OTEL Enabled

**Symptom:** Services crash when OTEL_ENABLED=true

**Fix:**

1. Install OpenTelemetry packages:

   ```bash
   pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-fastapi
   ```

2. Rebuild Docker images:

   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. Check requirements.txt includes:
   ```
   opentelemetry-api==1.21.0
   opentelemetry-sdk==1.21.0
   opentelemetry-exporter-otlp==1.21.0
   ```

---

## Performance Impact

**With OTEL_ENABLED=false:**

- ~0% overhead (OTEL code is lazy-loaded)

**With OTEL_ENABLED=true:**

- ~1-5% latency overhead per request
- ~10-20 MB additional memory (per service)
- Network traffic to collector (~10 KB per trace)

**Recommendation:** Enable only in development/staging. For production, use sampling.

---

## Sampling (For Production)

To reduce trace volume in production:

```python
# In pkg/observability.py
sampler = TraceIdRatioBased(0.1)  # Sample 10% of traces
```

This reduces overhead but maintains full debugging capability.

---

## Advanced Features

### Custom Spans

Add custom spans in your code:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my_operation") as span:
    span.set_attribute("bot_id", bot_id)
    # Your code here
    span.add_event("bot_registered")
```

### Correlate Logs & Traces

All logs automatically include trace context:

```
2025-12-17 06:56:13 [trace_id=a1b2c3d4..., span_id=x1y2z3...] INFO Bot registered
```

This allows log-to-trace correlation in Grafana.

### Metrics Integration

Collector also exports Prometheus metrics:

```bash
curl http://127.0.0.1:8888/metrics | grep otel
```

---

## Cleanup

### Disable Tracing

```env
OTEL_ENABLED=false
```

Restart services. No OTEL overhead without enabled flag.

### Stop Collector

```bash
docker-compose -f docker-compose.otel.yml down
```

### Remove All OTEL Data

```bash
docker-compose -f docker-compose.otel.yml down -v
```

This removes volumes (traces, logs, metrics).

---

## Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Grafana Tempo Docs](https://grafana.com/docs/tempo/latest/)
- [FastAPI + OTEL](https://opentelemetry.io/docs/instrumentation/python/libraries/#fastapi)
- [OTLP Specification](https://github.com/open-telemetry/opentelemetry-specification)

---

**Last Updated:** 2025-12-17
**Version:** 1.0.0
**Maintained by:** ELION Hyper-Dashboard Team
