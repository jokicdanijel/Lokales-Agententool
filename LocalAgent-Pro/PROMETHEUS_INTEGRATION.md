# LocalAgent-Pro Prometheus Integration - README

## ✅ Integration erfolgreich implementiert!

### 📊 Verfügbare Metriken

#### Request Metrics
- `localagent_requests_total{endpoint, status}` - Anzahl API-Requests
- `localagent_request_duration_seconds{endpoint}` - Request-Latenz (Histogram)
- `localagent_active_requests` - Aktuell aktive Requests

#### Ollama Integration
- `localagent_ollama_calls_total{model, status}` - Ollama API Calls
  - Labels: `model=llama3.1`, `status=success|failed`

#### Security & Stability
- `localagent_loop_detections_total` - Loop-Protection Aktivierungen
- `localagent_shell_executions_total{status}` - Shell-Command Executions
  - Status: `success|failed|blocked_sandbox|blocked_dangerous|timeout|error`

#### Tool Usage
- `localagent_tool_executions_total{tool, status}` - Tool-Aufrufe
  - Tools: `write_file`, `read_file`, `list_files`, etc.
- `localagent_sandbox_operations_total{operation}` - Sandbox-Dateoperationen
  - Operations: `write`, `read`, `delete`

### 🔧 Prometheus-Konfiguration

1. **Füge zu prometheus.yml hinzu:**
```yaml
scrape_configs:
  - job_name: 'localagent-pro'
    metrics_path: '/metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['host.docker.internal:8001']  # Für Docker
        # ODER
      - targets: ['localhost:8001']  # Für Host
```

2. **Vollständige Config:**
Siehe `config/prometheus_localagent.yml`

3. **Prometheus neu laden:**
```bash
docker exec prometheus-elion kill -HUP 1
# ODER
curl -X POST http://localhost:9090/-/reload
```

### 📈 Grafana Dashboard

1. **Dashboard importieren:**
   - Öffne Grafana: http://localhost:3001
   - Gehe zu "Dashboards" → "Import"
   - Lade `config/grafana_dashboard_localagent.json` hoch

2. **Manuelle Erstellung:**
```
Panel 1: Request Rate
Query: rate(localagent_requests_total[5m])

Panel 2: Error Rate
Query: rate(localagent_requests_total{status="error"}[5m])

Panel 3: Response Time (P95)
Query: histogram_quantile(0.95, rate(localagent_request_duration_seconds_bucket[5m]))

Panel 4: Loop Detections
Query: increase(localagent_loop_detections_total[1m])

Panel 5: Ollama Latency
Query: rate(localagent_ollama_calls_total[5m])
```

### 🧪 Test-Metriken generieren

```bash
# Health Check (generiert localagent_requests_total)
curl http://127.0.0.1:8001/health

# Chat Request (generiert ollama_calls, request_duration)
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'

# Tool Execution (generiert tool_executions, sandbox_operations)
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Erstelle Datei test.txt mit Hello"}'

# Metriken abrufen
curl http://127.0.0.1:8001/metrics | grep localagent_
```

### 🔍 Wichtige PromQL-Queries

#### Performance
```promql
# Requests pro Sekunde
rate(localagent_requests_total[5m])

# Durchschnittliche Response Time
rate(localagent_request_duration_seconds_sum[5m]) / rate(localagent_request_duration_seconds_count[5m])

# P50, P95, P99 Latenz
histogram_quantile(0.50, rate(localagent_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(localagent_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(localagent_request_duration_seconds_bucket[5m]))
```

#### Error Tracking
```promql
# Error Rate (%)
100 * rate(localagent_requests_total{status="error"}[5m]) / rate(localagent_requests_total[5m])

# Shell Command Fehler
rate(localagent_shell_executions_total{status=~"failed|timeout|error"}[5m])

# Loop Detections (letzte 5 Min)
increase(localagent_loop_detections_total[5m])
```

#### Ollama Performance
```promql
# Ollama Success Rate
rate(localagent_ollama_calls_total{status="success"}[5m]) / rate(localagent_ollama_calls_total[5m])

# Ollama Calls pro Minute
increase(localagent_ollama_calls_total[1m])
```

#### Resource Usage
```promql
# Memory Usage (MB)
process_resident_memory_bytes / 1024 / 1024

# CPU Usage (%)
rate(process_cpu_seconds_total[1m]) * 100

# Open File Descriptors
process_open_fds
```

### 🚨 Alert-Regeln (Optional)

Erstelle `alert_rules_localagent.yml`:

```yaml
groups:
  - name: localagent_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(localagent_requests_total{status="error"}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "LocalAgent-Pro Error Rate > 10%"
          description: "{{ $value }} errors/s"
      
      - alert: LoopDetection
        expr: increase(localagent_loop_detections_total[1m]) > 0
        annotations:
          summary: "Loop Protection aktiviert!"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(localagent_request_duration_seconds_bucket[5m])) > 5
        for: 2m
        annotations:
          summary: "Response Time > 5s (P95)"
      
      - alert: OllamaFailures
        expr: rate(localagent_ollama_calls_total{status="failed"}[5m]) > 0.2
        for: 3m
        annotations:
          summary: "Ollama Failure Rate > 20%"
```

### 📡 Endpoints

- **Metrics:** http://127.0.0.1:8001/metrics
- **Health:** http://127.0.0.1:8001/health
- **Prometheus UI:** http://127.0.0.1:9090
- **Grafana:** http://127.0.0.1:3001

### 💡 Nächste Schritte

1. ✅ **Metriken testen** - Requests senden, Metriken prüfen
2. 📊 **Grafana Dashboard** importieren
3. 🔔 **Alerts konfigurieren** (optional)
4. 📈 **Baseline etablieren** - Normal-Werte über 24h sammeln
5. 🎯 **Custom Queries** - Spezifische Queries für dein System

### 🎉 Was du jetzt hast

✅ Vollständiges Prometheus Monitoring  
✅ 8 Metric-Kategorien (Requests, Ollama, Tools, Security)  
✅ Loop-Protection Tracking  
✅ Shell Execution Monitoring  
✅ Sandbox Operations Insights  
✅ Performance Metriken (Latenz, Throughput)  
✅ Resource Usage (CPU, Memory)  
✅ Grafana-Dashboard Vorlage

**Dein LocalAgent-Pro ist jetzt production-ready mit vollem Observability-Stack!** 🚀
