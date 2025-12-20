# OpenTelemetry Tracing Setup für ELION Hyper-Dashboard

**Status:** ✅ **Installed & Configured**

## 🚀 Quick Start

### 1. Starte Tracing Stack (Docker)

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Starte OpenTelemetry Collector, Jaeger, Prometheus, Grafana
docker-compose -f docker-compose.tracing.yml up -d

# Prüfe Status
docker-compose -f docker-compose.tracing.yml ps
```

### 2. Jaeger UI öffnen

```
http://localhost:16686
```

Visualisiert Multi-Agent Workflows in Echtzeit.

### 3. Prometheus UI

```
http://localhost:9090
```

Metrics-Browser und PromQL Queries.

### 4. Grafana Dashboards

```
http://localhost:3000  # admin/admin
```

Pre-built Dashboards für Agent-Performance.

---

## 🔧 Konfiguration

### Environment Variables

```bash
# .env oder export
ENABLE_TRACING=true                    # Enable/Disable Tracing
OTLP_ENDPOINT=http://localhost:4317    # gRPC endpoint
OTLP_HTTP_ENDPOINT=http://localhost:4318  # HTTP endpoint
ENABLE_SENSITIVE_DATA=true             # Capture prompts/completions
TRACE_SAMPLE_RATE=1.0                  # 0.0-1.0, default: all traces
```

### Datei-Struktur

```
src/observability/
├── tracing_config.py           # Tracing setup functions
├── __init__.py

docker/
├── otel-collector-config.yaml  # OTEL Collector config
├── prometheus.yaml             # Prometheus scrape config

docker-compose.tracing.yml      # Full stack (OTEL + Jaeger + Prometheus + Grafana)
```

---

## 📊 Was wird getrackt?

### Automatisch (agent-framework):
- ✅ FastAPI request/response lifecycle
- ✅ Agent invocations
- ✅ Workflow steps
- ✅ Tool calls & responses
- ✅ Error traces & exceptions

### Manuell (Optional):
```python
from src.observability.tracing_config import TracingContext

# Erstelle Custom Span
with TracingContext("agent_dispatch", {"agent_id": "opena1"}):
    # Your code here
    pass
```

---

## 🎯 Use Cases

### 1. Multi-Agent Workflow Visualization
- Siehe alle Agenten-Interaktionen im DAG
- Latenz-Analyse pro Agent
- Fehler-Tracking durch die Chain

### 2. Performance Monitoring
- Request Latency (p50, p95, p99)
- Service Health
- Error Rates

### 3. Debugging
- Vollständige Request Traces
- Prompts & Completions (wenn enabled)
- Stack Traces für Errors

---

## 🚀 Integration mit Dashboard

**main_dashboard.py** hat bereits Tracing integriert:

```python
# Automatic on startup
if _TRACING_AVAILABLE:
    setup_observability(
        otlp_endpoint="http://localhost:4317",
        enable_sensitive_data=True
    )
```

**Result:**
- ✅ Alle Dashboard-Requests werden automatisch getraced
- ✅ Agent Registry Operationen sind sichtbar
- ✅ SSE Events haben Trace IDs

---

## 📈 Prometheus Metrics

Verfügbare Metriken:

```
# Agent Performance
elion_agent_latency_seconds{}
elion_agent_requests_total{}
elion_agent_errors_total{}

# Workflow Metrics
elion_workflow_duration_seconds{}
elion_workflow_steps_total{}

# System Health
otel_receiver_accepted_spans_total{}
otel_exporter_sent_spans_total{}
```

Query-Beispiele:

```promql
# Avg agent latency
avg(rate(elion_agent_latency_seconds_sum[5m]) / rate(elion_agent_latency_seconds_count[5m]))

# Error rate
rate(elion_agent_errors_total[5m])

# p99 latency
histogram_quantile(0.99, rate(elion_agent_latency_seconds_bucket[5m]))
```

---

## 🔗 Jaeger Queries

Beispiele:

```
# Alle Dashboard Traces
Service: opena20
Operation: POST /api/agent/register

# Agent-zu-Agent Calls
Service: opena1
Tag: workflow_id=<id>

# Error Traces
Service: *
Tag: error=true
```

---

## 🛠️ Troubleshooting

### OTEL Collector startet nicht
```bash
docker-compose -f docker-compose.tracing.yml logs otel-collector
```

### Traces nicht in Jaeger sichtbar
1. Prüfe OTLP Endpoint: `curl http://localhost:4317`
2. Prüfe Collector Logs
3. Verifiziere `ENABLE_TRACING=true` in `.env`

### Performance-Impact
- Tracing hat minimal overhead (~1-2%)
- Mit `TRACE_SAMPLE_RATE=0.1` auf 10% reduzieren für große Scale

---

## 📚 Weitere Ressourcen

- [OpenTelemetry Docs](https://opentelemetry.io/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Queries](https://prometheus.io/docs/prometheus/latest/querying/)
- [Agent Framework Observability](https://github.com/microsoft/agent-framework)

---

## 🎬 Next Steps

1. ✅ Start stack: `docker-compose -f docker-compose.tracing.yml up -d`
2. ✅ Visit Jaeger: http://localhost:16686
3. ✅ Trigger workflows in Dashboard
4. ✅ View traces in real-time
5. ✅ Analyze metrics in Grafana

**Viel Erfolg mit der Tracing! 🚀**
