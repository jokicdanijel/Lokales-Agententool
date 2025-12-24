# Agent Fleet Observatory

Real-time Docker-Compose Service Inventory with Live Container Status for opena20 Dashboard.

## Overview

The Agent Fleet Observatory provides comprehensive visibility into all Docker-Compose services across the repository with **live Docker daemon integration**. It automatically discovers, catalogs, and presents service information with real-time container status in an intuitive web interface.

## Key Features

✅ **Live Docker Status** - Real-time container status (running/stopped/exited) via Docker daemon
✅ **Historical Tracking** - Change detection with automated snapshots (added/removed/modified services)
✅ **Port Conflict Detection** - Identifies duplicate host port assignments across services
✅ **Resource Metrics** - CPU and Memory usage monitoring for running containers
✅ **Auto-Discovery** - Automatically finds all docker-compose files in repository
✅ **Port Mapping** - Visualizes all exposed ports and mappings
✅ **Health Monitoring** - Displays container health check status
✅ **Network Topology** - Shows network configurations and dependencies
✅ **Search & Filter** - Interactive filtering by name, image, port, restart policy
✅ **Dark Theme UI** - Modern, responsive dashboard interface

## Components

### 1. **Scanner** (`scripts/agent_scanner_compose.py`)
Python-based Docker-Compose parser with **live Docker daemon integration** that extracts:
- Service names and container names
- Docker images and tags
- Port mappings (host:container)
- Network configurations
- Restart policies
- Health check configurations
- Environment variables (sanitized)
- Dependencies (depends_on)
- **🆕 Live container status** (running/stopped/exited)
- **🆕 Container IDs** and health status
- **🆕 Container start timestamps**

**Usage:**
```bash
# Standard scan with all features (recommended)
python3 scripts/agent_scanner_compose.py --auto-discover

# Include CPU/Memory stats (slower, only for running containers)
python3 scripts/agent_scanner_compose.py --auto-discover --resource-stats

# Disable specific features
python3 scripts/agent_scanner_compose.py --auto-discover --no-live-status
python3 scripts/agent_scanner_compose.py --auto-discover --no-track-changes

# Scan specific files only
python3 scripts/agent_scanner_compose.py --compose-files docker-compose.yml docker-compose.prod.yml

# Custom output directory
python3 scripts/agent_scanner_compose.py --auto-discover --output-dir /custom/path
```

**CLI Flags:**
- `--auto-discover`: Recursively find all docker-compose files
- `--live-status` / `--no-live-status`: Docker container status (default: enabled)
- `--track-changes` / `--no-track-changes`: Historical change tracking (default: enabled)
- `--detect-conflicts`: Port conflict detection (default: enabled)
- `--resource-stats`: Include CPU/Memory metrics (default: disabled, slower)
- `--compose-files`: Specify exact compose file paths
- `--output-dir`: Custom output directory

**Requirements:**
- Python 3.12+
- `pyyaml` for compose parsing
- `docker` Python SDK for live status (optional, gracefully degrades)

### 2. **Web UI** (`agents_fleet.html`)
Modern, responsive dashboard featuring:
- **Real-time Statistics**: Total services, running/stopped counts, port conflicts, last scan
- **🆕 Change Summary Banner**: Visual indicators for added/removed/modified services
- **🆕 Live Status Badges**: 🟢 Running, 🔴 Stopped, ⚪ Not Found indicators
- **🆕 Container Details**: Container IDs and health status display
- **🆕 Resource Metrics**: Color-coded CPU/Memory usage (🟢 <50%, 🟡 50-80%, 🔴 >80%)
- **🆕 Port Conflict Alert**: Highlights services with duplicate port assignments
- **Interactive Search**: Filter by service name, image, port, or compose file
- **Policy Filtering**: Filter by restart policy (always, unless-stopped, on-failure, no)
- **Service Cards**: Detailed view of each service including ports, networks, dependencies
- **Dark Theme**: Professional dark mode interface

**Access:**
```
http://localhost:8000/agents_fleet.html
```

### 3. **Output Files**

#### `agent_inventory.json`
Complete machine-readable inventory in JSON format:
```json
{
  "scanned_at": "2025-12-24T10:04:31Z",
  "total_services": 185,
  "compose_files_scanned": ["..."],
  "changes": {
    "added": [],
    "removed": [],
    "modified": [],
    "unchanged": ["service1", "service2", "..."]
  },
  "port_conflicts": {
    "9090": ["prometheus", "prometheus", "..."]
  },
  "services": [
    {
      "service_name": "opena20-dashboard",
      "image": "opena20-dashboard:local",
      "ports": [{"host_port": 12349, "container_port": 12349}],
      "networks": ["elion"],
      "restart": "unless-stopped",
      "healthcheck": {...}
    }
  ]
}
```

#### `agent_fleet_report.md`
Human-readable Markdown report with detailed service information.

## Features

### Security
- **Secret Sanitization**: Automatically redacts passwords, tokens, API keys from environment variables
- **Read-only Operations**: Scanner never modifies compose files or starts/stops services
- **No Runtime Access**: No direct interaction with Docker daemon required

### Performance
- **Fast Scanning**: Processes 47 compose files with 185+ services in <2 seconds
- **Efficient Parsing**: Uses PyYAML for robust YAML parsing
- **Caching-friendly**: JSON output can be cached for quick UI loads

### Flexibility
- **Auto-discovery**: Recursively finds all `docker-compose*.yml` files
- **Selective Scanning**: Specify exact compose files to scan
- **Extensible**: Easy to add new extraction features (volumes, labels, etc.)

## Integration

The Fleet UI integrates seamlessly with the opena20 backend:

1. **Static File Serving**: `/artifacts` endpoint mounted via FastAPI StaticFiles
2. **No Backend Logic Required**: Pure frontend application consuming JSON
3. **Independent Refresh**: Run scanner independently, UI auto-updates on page reload

## Automation

Add to CI/CD or cron jobs:
```bash
# Daily fleet scan
0 2 * * * cd /path/to/repo && python3 scripts/agent_scanner_compose.py --auto-discover
```

## Requirements

- Python 3.8+
- PyYAML (`pip install pyyaml`)
- FastAPI backend running (for UI access)

## Roadmap

Future enhancements:
- [ ] Real-time Docker daemon integration (live status)
- [ ] Historical tracking (service changes over time)
- [ ] Port conflict detection
- [x] **Live Docker Status Integration** - Real-time container status ✅
- [x] **Historical Change Tracking** - Detect service changes over time ✅
- [x] **Port Conflict Detection** - Identify duplicate port assignments ✅
- [x] **Resource Usage Metrics** - CPU/Memory monitoring ✅
- [ ] **One-Click Service Controls** - Start/stop/restart buttons (In Progress 🚧)
- [ ] **Health Check Testing** - Execute container health checks
- [ ] **Export Functionality** - CSV/Excel export
- [ ] **Alert System** - Notifications for critical changes
- [ ] **Multi-Environment Support** - Dev/Staging/Prod separation

## Architecture

```
Repository Root
├── scripts/
│   └── agent_scanner_compose.py     # Scanner (read-only, Docker SDK)
├── 19.opena20_dashboard_agent/
│   ├── artifacts/
│   │   └── agent_fleet/              # Output directory
│   │       ├── agent_inventory.json  # JSON output (with changes/conflicts)
│   │       ├── agent_fleet_report.md # Markdown report (with summaries)
│   │       └── history/              # Historical snapshots (max 10)
│   │           ├── inventory_20251224_102843.json
│   │           └── ...
│   └── webpanel/
│       ├── agents_fleet.html         # UI entry point
│       ├── css/agents_fleet.css      # Styling (with resource colors)
│       ├── js/agents_fleet.js        # Frontend logic (changes display)
│       └── app.py                    # FastAPI backend
```

## Troubleshooting

**Scanner not finding compose files?**
- Ensure you're running from repository root
- Check for YAML syntax errors in compose files
- Use `--compose-files` to specify exact paths

**UI shows "Failed to load agent fleet data"?**
- Run scanner first: `python3 scripts/agent_scanner_compose.py --auto-discover`
- Verify backend is running: `curl http://localhost:8000/health`
- Check artifacts directory exists: `ls 19.opena20_dashboard_agent/artifacts/agent_fleet/`

**Port numbers not displaying correctly?**
- Check compose file port syntax (should be `"8080:80"` or `8080:80`)
- Verify no environment variables in port definitions

## Contributing

When adding features:
1. Maintain read-only scanner operations
2. Sanitize any sensitive data in outputs
3. Update JSON schema in README
4. Test with complex compose files (multi-network, health checks, etc.)
5. Ensure UI remains responsive with 100+ services

---

**Last Updated**: 2025-12-24
**Version**: 2.0.0
**Status**: Production Ready ✅
**Features Completed**: 4/9
**Repository**: jokicdanijel/Gesamtprojekt-start
**Services Tracked**: 185 services across 47 compose files
**Port Conflicts Detected**: 33 conflicts identified
