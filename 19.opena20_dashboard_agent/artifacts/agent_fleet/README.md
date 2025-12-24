# Agent Fleet Observatory

Real-time Docker-Compose Service Inventory for opena20 Dashboard.

## Overview

The Agent Fleet Observatory provides comprehensive visibility into all Docker-Compose services across the repository. It automatically discovers, catalogs, and presents service information in an intuitive web interface.

## Components

### 1. **Scanner** (`scripts/agent_scanner_compose.py`)
Python-based Docker-Compose parser that extracts:
- Service names and container names
- Docker images and tags
- Port mappings (host:container)
- Network configurations
- Restart policies
- Health check configurations
- Environment variables (sanitized)
- Dependencies (depends_on)

**Usage:**
```bash
# Auto-discover all compose files
python3 scripts/agent_scanner_compose.py --auto-discover

# Scan specific files
python3 scripts/agent_scanner_compose.py --compose-files docker-compose.yml docker-compose.prod.yml

# Custom output directory
python3 scripts/agent_scanner_compose.py --auto-discover --output-dir /custom/path
```

### 2. **Web UI** (`agents_fleet.html`)
Modern, responsive dashboard featuring:
- **Real-time Statistics**: Total services, compose files, exposed ports, last scan time
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
  "total_services": 27,
  "compose_files_scanned": ["..."],
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
- [ ] Resource usage metrics (CPU/Memory)
- [ ] Health check testing
- [ ] One-click service start/stop controls
- [ ] Export to CSV/Excel

## Architecture

```
Repository Root
├── scripts/
│   └── agent_scanner_compose.py     # Scanner
├── 19.opena20_dashboard_agent/
│   ├── artifacts/
│   │   └── agent_fleet/              # Output directory
│   │       ├── agent_inventory.json  # JSON output
│   │       └── agent_fleet_report.md # Markdown report
│   └── webpanel/
│       ├── agents_fleet.html         # UI entry point
│       ├── css/agents_fleet.css      # Styling
│       ├── js/agents_fleet.js        # Frontend logic
│       └── app.py                    # FastAPI backend (artifacts mount)
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
**Version**: 1.0.0
**Status**: Production Ready ✅
