# Agent Fleet Inventory Report

**Generated:** 2025-12-24 10:32:30 UTC

**Total Services:** 1

## 📊 Change Summary

- ❌ **Removed:** 51 services
  - otel-collector
  - prometheus
  - grafana
  - portier
  - archivator
  - ... and 46 more
- 🔄 **Modified:** 1 services
  - opena20-dashboard

---

## opena20-dashboard

- **Image:** `opena20-dashboard:local`
- **Container:** `opena20-dashboard`
- **Compose File:** `docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Health Check:** ['CMD-SHELL', 'curl -f http://localhost:12349/health || exit 1']

---
