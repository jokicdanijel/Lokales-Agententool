# Phase 17: Monitoring Dashboard

**Start:** 2025-11-11 12:40 UTC
**Status:** 🟡 Planning
**Objective:** Real-time service monitoring with Prometheus + Grafana

---

## 📊 Current System State

| Component               | Status            | Port        | Entries |
| ----------------------- | ----------------- | ----------- | ------- |
| Portier (Coordinator)   | ✅ Online         | 12344       | -       |
| OpenA2 (Archive)        | ✅ Online         | 12345       | 172     |
| Telegram (Messaging)    | ✅ Online         | 12346       | -       |
| Inference (llama-stack) | ✅ Online         | 12346       | -       |
| Generated Services      | 🟡 Template Ready | 12349-12365 | -       |

**Archive Backup:** ✅ Created at `1.opena1&2_portier/archivp_store.backup.2025-11-11`

---

## 🎯 Phase 17 Deliverables

### **1. Prometheus Metrics Exporter** (New Service)

- **Location:** `19.opena20_dashboard_agent/metrics_exporter.py`
- **Port:** 9090 (Prometheus scrape endpoint)
- **Metrics to Collect:**
  - Service health (up/down binary)
  - Request latency (p50, p95, p99)
  - Request count (total, errors, success rate)
  - Archive size (entries, disk usage)
  - Memory usage (per service)
  - CPU usage (per service)

### **2. Grafana Dashboard** (Visualization)

- **Location:** `19.opena20_dashboard_agent/grafana/`
- **Port:** 3001 (Grafana UI)
- **Dashboards:**
  - System Overview (20 services at a glance)
  - Service Health (individual status pages)
  - Archive Analytics (entry types, growth rate)
  - Performance Heatmap (latency distribution)
  - Alert Status (active alerts)

### **3. Alert Rules** (Prometheus AlertManager)

- **Location:** `configs/alert_rules.yaml`
- **Rules:**
  - Service Down (unavailable > 30s)
  - High Latency (p95 > 1000ms)
  - Archive Growing Too Fast (> 50 MB/day)
  - Memory Threshold Exceeded (> 80% per service)
  - Error Rate High (> 5%)

### **4. Integration with Portier** (Coordinator)

- **New Endpoint:** `GET /metrics` (Prometheus text format)
- **Safepoint Logging:** Enhanced with metrics events
- **Service Registry:** Metrics metadata (service name, port, tags)

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Monitoring Stack                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Prometheus (9090) - Time Series DB              │  │
│  │  ├─ Scrapes /metrics from all services (30s)    │  │
│  │  ├─ Stores metrics for 7 days (configurable)    │  │
│  │  └─ Evaluates alert rules every 15s             │  │
│  └──────────────────────────────────────────────────┘  │
│           ↑                          ↓                  │
│    [Metrics Exporter]        [AlertManager]            │
│         (pulls)                    (routes)             │
│           ↑                          ↓                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Grafana (3001) - Dashboards & Visualizations   │  │
│  │  ├─ System Overview                             │  │
│  │  ├─ Service Health                              │  │
│  │  ├─ Archive Analytics                           │  │
│  │  └─ Performance Heatmaps                        │  │
│  └──────────────────────────────────────────────────┘  │
│           ↑                                              │
│    [Queries Prometheus]                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
           ↑
    ┌──────┴─────────────────────────────────────────────┐
    │     Services (12344-12365) + Archive (12345)        │
    │     ├─ /health                                      │
    │     ├─ /metrics (new)                               │
    │     └─ Safepoint logging (enhanced)                 │
    └─────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Checklist

### **Step 1: Create Metrics Exporter** (1-2 hours)

- [ ] Create `19.opena20_dashboard_agent/metrics_exporter.py` (300 LOC)
- [ ] Implement Prometheus client library integration
- [ ] Add health check endpoints for all services
- [ ] Add request latency tracking (timing middleware)
- [ ] Add archive size/entry monitoring
- [ ] Test `/metrics` endpoint format
- [ ] Verify Prometheus can scrape

### **Step 2: Set up Prometheus** (30 min)

- [ ] Create `configs/prometheus.yaml` config file
- [ ] Define scrape targets (12344-12365, 9090)
- [ ] Set scrape interval to 30 seconds
- [ ] Define retention to 7 days
- [ ] Create `scripts/start_prometheus.sh`
- [ ] Test Prometheus UI at http://localhost:9090

### **Step 3: Create Grafana Dashboards** (2-3 hours)

- [ ] Set up Grafana datasource (Prometheus)
- [ ] Create "System Overview" dashboard (4 panels)
- [ ] Create "Service Health" dashboard (20 service panels)
- [ ] Create "Archive Analytics" dashboard (growth, types)
- [ ] Create "Performance" dashboard (latency heatmap)
- [ ] Create "Alerts" dashboard (active + historical)

### **Step 4: Configure Alert Rules** (1 hour)

- [ ] Create `configs/alert_rules.yaml`
- [ ] Define 5 alert conditions (see above)
- [ ] Set up AlertManager routing (email, Slack optional)
- [ ] Test alert triggering manually

### **Step 5: Integration & Testing** (1-2 hours)

- [ ] Add `/metrics` endpoint to Portier
- [ ] Enhance safepoint logging with metrics events
- [ ] Create `scripts/load_test_with_monitoring.py` (extended test)
- [ ] Run load test and verify dashboard updates
- [ ] Document monitoring usage

### **Step 6: Documentation** (30 min)

- [ ] Create `docs/MONITORING_GUIDE.md`
- [ ] Add quick-start: "How to view dashboards"
- [ ] Document metric definitions
- [ ] Document alert conditions

---

## 🔧 Key Decisions

### **Why Prometheus + Grafana?**

✅ Standard monitoring stack for distributed systems
✅ Lightweight (single binary for Prometheus)
✅ No external dependencies (runs locally)
✅ Great for time-series data
✅ Open-source and well-documented

### **Why NOT Elastic Stack or Datadog?**

❌ Elasticsearch: Too heavy for single-machine setup
❌ Datadog: Requires external service (cloud), not offline
❌ CloudWatch: AWS-specific

---

## 📊 Expected Metrics

### **Service Metrics (Per Service)**

```
elion_service_up{service="portier", port="12344"}                   = 1 (1=up, 0=down)
elion_service_request_total{service="portier", endpoint="/health"}  = 1234
elion_service_request_errors{service="portier"}                     = 5
elion_service_request_duration_seconds{service="portier", quantile="0.95"} = 0.042
elion_service_memory_bytes{service="portier"}                       = 52428800 (50MB)
elion_service_cpu_percent{service="portier"}                        = 2.5
```

### **Archive Metrics**

```
elion_archive_entries_total{kind="CHAT_COMPLETION"}                 = 102
elion_archive_entries_total{kind="MODEL_LIST"}                      = 41
elion_archive_size_bytes                                            = 90774
elion_archive_growth_entries_per_hour                               = 15.2
```

### **System Metrics**

```
elion_services_online                                               = 4
elion_services_total                                                = 20
elion_requests_per_second                                           = 27.74
elion_error_rate_percent                                            = 0.5
```

---

## 🚀 Success Criteria

✅ Prometheus scrapes all services successfully
✅ Grafana dashboard loads without errors
✅ Real-time updates reflect latency < 5 seconds
✅ Archive growth tracked accurately
✅ Alerts trigger correctly on test conditions
✅ Can visualize Phase 15 load-test (27.74 req/s peak)
✅ Documentation complete and tested

---

## 📅 Phase 17 Timeline

| Task                  | Estimated    | Status         |
| --------------------- | ------------ | -------------- |
| Metrics Exporter      | 2h           | 🟡 Not Started |
| Prometheus Setup      | 0.5h         | 🟡 Not Started |
| Grafana Dashboards    | 3h           | 🟡 Not Started |
| Alert Rules           | 1h           | 🟡 Not Started |
| Testing & Integration | 2h           | 🟡 Not Started |
| Documentation         | 0.5h         | 🟡 Not Started |
| **TOTAL**             | **~9 hours** | 🟡 Not Started |

**Possible Completion:** Next 4-5 hours if continuous work
**Realistic Completion:** 2025-11-11 18:00-20:00 UTC

---

## 📦 Dependencies to Install

```bash
# Python packages (add to requirements.txt)
prometheus-client==0.21.0      # Prometheus metrics library
python-multipart==0.0.6        # Form data handling

# External services (Docker or local)
prometheus:latest              # Metrics aggregator
grafana/grafana:latest         # Dashboard UI

# Installation command
pip install prometheus-client python-multipart
docker pull prom/prometheus
docker pull grafana/grafana
```

---

## 🔗 Quick Links (After Phase 17)

- **Prometheus UI:** http://localhost:9090
- **Grafana Dashboards:** http://localhost:3001
- **Metrics Endpoint:** http://localhost:12344/metrics
- **Alert Rules:** `configs/alert_rules.yaml`
- **Monitoring Guide:** `docs/MONITORING_GUIDE.md`

---

## 🎯 Next Steps

**To Start Phase 17, choose:**

**A** – Implement Metrics Exporter (Step 1)
**B** – Set up Prometheus + Grafana (Steps 2-3)
**C** – Create Dashboards (Step 3)
**D** – Jump to all steps (Fast-track)
**E** – Review plan first (Skip Phase 17 for now)

---

**Plan created by:** Archive Analysis → Phase 17 Transition
**Backup Status:** ✅ Safe (172 entries backed up)
**Ready to proceed:** Yes
