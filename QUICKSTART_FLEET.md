# Quick Start: Agent Fleet Observatory

## 🚀 Launch in 3 Steps

### Step 1: Scan Services (with all features)
```bash
cd /path/to/Gesamtprojekt
python3 scripts/agent_scanner_compose.py --auto-discover

# With resource monitoring (slower)
python3 scripts/agent_scanner_compose.py --auto-discover --resource-stats
```

### Step 2: Start Backend
```bash
cd 19.opena20_dashboard_agent/webpanel
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Step 3: Open UI
```
http://localhost:8000/agents_fleet.html
```

## 📊 What You'll See

- **🟢 Live Status**: Real-time running/stopped/exited container states
- **📊 Change Summary**: Added/removed/modified services since last scan
- **⚠️ Port Conflicts**: Duplicate port assignments (33 detected!)
- **💻 Resource Metrics**: CPU/Memory usage with color-coding (if --resource-stats enabled)
- **Total Services**: All Docker services across compose files (185 discovered)
- **Port Mappings**: Host:Container port assignments
- **Network Topology**: Service network memberships
- **Health Checks**: Container health status
- **Historical Snapshots**: Last 10 scans archived automatically

## 🔍 Search & Filter

- Type service name, image, or port number to filter
- Use dropdown to filter by restart policy
- Click refresh to re-scan after compose file changes

## 🛠️ Advanced Usage

### Scan Specific Files
```bash
python3 scripts/agent_scanner_compose.py \
  --compose-files docker-compose.yml docker-compose.prod.yml
```

### Disable Specific Features
```bash
# Without live Docker status
python3 scripts/agent_scanner_compose.py --auto-discover --no-live-status

# Without change tracking
python3 scripts/agent_scanner_compose.py --auto-discover --no-track-changes
```

### Include Resource Metrics
```bash
# Add CPU/Memory stats (slower, only for running containers)
python3 scripts/agent_scanner_compose.py --auto-discover --resource-stats
```

### Custom Output Directory
```bash
python3 scripts/agent_scanner_compose.py \
  --auto-discover \
  --output-dir /custom/path
```

### Automated Scanning (Cron)
```bash
# Add to crontab: scan every 6 hours
0 */6 * * * cd /path/to/repo && python3 scripts/agent_scanner_compose.py --auto-discover
```

## 📁 Output Files

- **JSON**: `19.opena20_dashboard_agent/artifacts/agent_fleet/agent_inventory.json`
- **Markdown**: `19.opena20_dashboard_agent/artifacts/agent_fleet/agent_fleet_report.md`
- **History**: `19.opena20_dashboard_agent/artifacts/agent_fleet/history/` (last 10 snapshots)

## 🔐 Security Note

- Scanner sanitizes secrets (passwords, tokens, API keys)
- Docker SDK optional (graceful degradation without it)
- Read-only operations only (except for optional service controls)
- Change tracking maintains audit trail

---

**Questions?** See [README.md](19.opena20_dashboard_agent/artifacts/agent_fleet/README.md) for full documentation.
