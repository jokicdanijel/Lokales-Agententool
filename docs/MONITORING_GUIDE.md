# Phase 17: Monitoring Guide

**Status:** ✅ Complete
**Date:** 2025-11-11
**Components:** Prometheus + Grafana + Alert Rules

---

## Quick Start

### 1. Ensure Services Are Running

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
ps aux | grep -E "portier|opena2|telegram|inference"
```

### 2. View Metrics Endpoints

**Prometheus Text Format (Port 12344):**

```bash
curl http://127.0.0.1:12344/metrics | head -50
```

**JSON Health API (Port 12344):**

```bash
curl http://127.0.0.1:12344/api/health/metrics | jq .
```

### 3. Access Prometheus UI (Port 9090)

```
http://localhost:9090
```

**Key Pages:**

- **Graph:** http://localhost:9090/graph
  - Query any metric (e.g., `up`, `elion_archive_size_bytes`)
- **Targets:** http://localhost:9090/targets
  - Shows which services Prometheus scrapes from
- **Rules:** http://localhost:9090/rules
  - Shows alert conditions

### 4. Access Grafana Dashboards (Port 3000)

```
http://localhost:3000
```

**Default Credentials:**

- Username: `admin`
- Password: `admin`

**Setup Steps:**

1. Login with admin/admin
2. Click "Add Data Source"
3. Select "Prometheus"
4. URL: `http://prometheus-elion:9090`
5. Save & Test
6. Import dashboards from `configs/grafana-*.json`

---

## Available Metrics

### Service Metrics (per service)

```
elion_service_up{service="portier", port="12344"}
  # 1 = up, 0 = down

elion_service_response_time_seconds{service="portier"}
  # Request latency histogram (p50, p95, p99)

elion_service_requests_total{service="portier", status="200"}
  # Total requests per status code

elion_service_memory_bytes{service="portier"}
  # Memory usage in bytes

elion_service_cpu_percent{service="portier"}
  # CPU usage 0-100%
```

### Archive Metrics

```
elion_archive_entries_total{kind="CHAT_COMPLETION"}
  # Number of entries by type

elion_archive_size_bytes
  # Total archive size in bytes (~90 KB typical)

elion_archive_growth_entries_per_hour
  # Entry growth rate
```

### System Metrics

```
elion_services_online
  # Number of services currently up (0-20)

elion_services_total
  # Total service slots (fixed at 20)

elion_requests_per_second
  # System-wide throughput

elion_error_rate_percent
  # System-wide error rate 0-100%
```

---

## Alert Conditions

### Critical (🔴)

**ServiceDown:** Service offline for 30+ seconds

- Runbook: Restart service via `bin/ops.sh restart <service>`

### Warning (🟡)

| Alert                  | Condition                | Action                 |
| ---------------------- | ------------------------ | ---------------------- |
| HighLatency            | P95 latency > 1s         | Check load/connections |
| ArchiveGrowthTooFast   | > 100 entries/hour       | Review content volume  |
| HighMemoryUsage        | > 512 MB for 2m          | Restart service        |
| HighErrorRate          | > 5% for 1m              | Check logs             |
| ArchiveSizeCritical    | > 1 GB                   | Prune old entries      |
| LowServiceAvailability | < 2 services online      | Start services         |
| ZeroThroughput         | 0 req/s with services up | Check Portier health   |

**View Active Alerts:**

```bash
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[]'
```

---

## Common Queries (PromQL)

```promql
# Service uptime percentage
(1 - (1 - avg(elion_service_up{service="portier"}))*100)

# Average latency across all services
avg(elion_service_response_time_seconds)

# Archive growth rate (entries per minute)
rate(elion_archive_entries_total[5m])

# Total memory usage
sum(elion_service_memory_bytes)

# Error rate by service
sum(rate(elion_service_requests_total{status!="200"}[1m])) /
sum(rate(elion_service_requests_total[1m])) * 100
```

---

## Troubleshooting

### Prometheus Not Scraping

```bash
# Check if Portier is running
curl http://127.0.0.1:12344/health

# Check if /metrics endpoint works
curl http://127.0.0.1:12344/metrics | head -20

# View Prometheus targets UI
# http://localhost:9090/targets
```

### Grafana Can't Connect to Prometheus

```bash
# Inside Grafana container, test Prometheus connection
docker exec grafana-elion curl -s http://prometheus-elion:9090/api/v1/query?query=up

# If fails, check Docker network
docker network ls
docker inspect bridge
```

### No Metrics Appearing

- **Wait 30s:** Prometheus scrapes every 30s
- **Check Portier logs:** `tail -50 logs/portier.log`
- **Verify prometheus-client installed:** `pip show prometheus-client`

### Alert Rules Not Loading

```bash
# Check Prometheus logs
docker logs prometheus-elion | grep -i error

# Validate YAML syntax
curl -X POST -d @configs/alert_rules.yaml http://localhost:9090/api/v1/rules
```

---

## Docker Commands

**Restart Services:**

```bash
# Stop all monitoring containers
docker stop prometheus-elion grafana-elion

# Start again
docker start prometheus-elion grafana-elion

# View logs
docker logs prometheus-elion
docker logs grafana-elion
```

**Persistent Data:**

```bash
# Prometheus data directory (inside container)
/prometheus/

# Grafana provisioning (inside container)
/etc/grafana/provisioning/
```

---

## Performance Notes

| Component        | CPU      | Memory     | Storage                 |
| ---------------- | -------- | ---------- | ----------------------- |
| Prometheus       | ~2%      | ~100 MB    | 7 days retention ~50 MB |
| Grafana          | Variable | ~50-200 MB | SQLite ~10 MB           |
| Portier Exporter | <1%      | ~5 MB      | N/A                     |

**Total:** ~300 MB memory (acceptable)

---

## Production Recommendations

1. **Authentication:**
   - Prometheus: Use reverse proxy with auth
   - Grafana: Set strong password (not "admin")

2. **Retention:**
   - Prometheus: Adjust `--storage.tsdb.retention` flag
   - Archive: Keep 30 days of metrics minimum

3. **Alerting:**
   - Set up AlertManager for routing
   - Configure email/Slack notifications

4. **Scaling:**
   - Use Prometheus remote storage for long-term metrics
   - Consider Victoria Metrics for larger deployments

---

## Next Steps

1. ✅ Deploy Prometheus
2. ✅ Deploy Grafana
3. Import custom dashboards (JSON files in `configs/`)
4. Test alert rules manually (stop a service)
5. Integrate with Phase 18 (Production Deployment)

---

**Documentation Date:** 2025-11-11
**Maintained by:** ELION Team
