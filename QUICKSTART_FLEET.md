# Quick Start: Agent Fleet Observatory

## 🚀 Launch in 3 Steps

### Step 1: Scan Services
```bash
cd /path/to/Gesamtprojekt
python3 scripts/agent_scanner_compose.py --auto-discover
```

### Step 2: Start Backend
```bash
cd 19.opena20_dashboard_agent/webpanel
python3 app.py
```

### Step 3: Open UI
```
http://localhost:8000/agents_fleet.html
```

## 📊 What You'll See

- **Total Services**: All Docker services across compose files
- **Port Mappings**: Host:Container port assignments
- **Network Topology**: Service network memberships
- **Restart Policies**: Auto-restart configuration
- **Health Checks**: Configured health check commands

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

## 🔐 Security Note

- Scanner sanitizes secrets (passwords, tokens, API keys)
- Read-only operations only
- No Docker daemon access required

---

**Questions?** See [README.md](README.md) for full documentation.
