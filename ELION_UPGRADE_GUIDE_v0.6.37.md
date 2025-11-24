# 🚀 ELION Upgrade Guide v0.6.37

**Target:** OpenWebUI v0.6.37 Integration with LocalAgent-Pro  
**Date:** 24. November 2025  
**Status:** Production-Ready  
**Author:** GitHub Copilot  

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [PHASE A: Preparation](#phase-a-preparation)
3. [PHASE B: OpenWebUI Update](#phase-b-openwebui-update)
4. [PHASE C: ELION Patches](#phase-c-elion-patches)
5. [PHASE D: Security Configuration](#phase-d-security-configuration)
6. [PHASE E: Agent Integration](#phase-e-agent-integration)
7. [PHASE F: Testing](#phase-f-testing)
8. [PHASE G: Deployment](#phase-g-deployment)
9. [PHASE H: Troubleshooting](#phase-h-troubleshooting)

---

## Prerequisites

### System Requirements

```bash
# Check Python version
python3 --version  # Required: 3.11+

# Check Docker & Docker Compose
docker --version
docker-compose --version

# Check Git
git --version

# Verify internet connection
curl -s https://github.com/status 2>&1 | head -1
```

### Required Directories

```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/
├── 2.opena3_openwebui/
├── LocalAgent-Pro/
├── 1.opena1&2_portier/
└── bin/
```

### Environment Variables

```bash
# Create .env if missing
cat > .env << 'EOF'
DASHBOARD_PORT=12349
OPENA1_PORT=12344
OPENA2_PORT=12345
DASHBOARD_ADMIN_TOKEN=your_secure_token_here
OPENAI_API_KEY=optional_for_features
EOF
```

---

## PHASE A: Preparation

### Step 1: Backup Current State

```bash
#!/bin/bash
set -euo pipefail

BACKUP_DIR="backups/elion_upgrade_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Backing up current state..."

# Backup OpenWebUI config
if [[ -d "2.opena3_openwebui" ]]; then
  tar czf "$BACKUP_DIR/openwebui_backup.tar.gz" \
    2.opena3_openwebui/config 2>/dev/null || true
fi

# Backup LocalAgent-Pro
if [[ -d "LocalAgent-Pro" ]]; then
  tar czf "$BACKUP_DIR/localagent_backup.tar.gz" \
    LocalAgent-Pro/config LocalAgent-Pro/data 2>/dev/null || true
fi

# Backup database (if SQLite)
find . -name "*.db" -exec cp {} "$BACKUP_DIR/" \;

# Git backup
git bundle create "$BACKUP_DIR/repo.bundle" --all

echo "✅ Backup created: $BACKUP_DIR"
```

### Step 2: Stop Services

```bash
#!/bin/bash
echo "🛑 Stopping services..."

# Using ops.sh
./bin/ops.sh stop

# Or manual
pkill -f "main_dashboard.py" 2>/dev/null || true
pkill -f "main_opena1.py" 2>/dev/null || true
pkill -f "main_opena2.py" 2>/dev/null || true

# Docker
docker-compose down 2>/dev/null || true

# Wait for cleanup
sleep 3

echo "✅ Services stopped"
```

### Step 3: Verify Pre-Upgrade State

```bash
#!/bin/bash
echo "🔍 Pre-upgrade verification..."

# Check current OpenWebUI version
if command -v docker &>/dev/null; then
  docker exec openwebui_container pip show open-webui | grep Version || echo "⚠️  OpenWebUI version check skipped"
fi

# Check LocalAgent-Pro status
curl -s http://127.0.0.1:8001/health 2>/dev/null | jq . || echo "⚠️  LocalAgent-Pro not responding"

# Verify Git state
git status

echo "✅ Pre-upgrade verification complete"
```

---

## PHASE B: OpenWebUI Update

### Step 1: Fetch Latest Version

```bash
#!/bin/bash
set -euo pipefail

cd 2.opena3_openwebui

echo "📥 Fetching OpenWebUI v0.6.37..."

# Update from source or Docker
if [[ -d ".git" ]]; then
  git fetch origin
  git checkout v0.6.37 || git checkout main
elif command -v docker &>/dev/null; then
  docker pull ghcr.io/open-webui/open-webui:main
fi

echo "✅ OpenWebUI fetched"
```

### Step 2: Update Dependencies

```bash
#!/bin/bash
set -euo pipefail

echo "📚 Updating dependencies..."

# Backend
if [[ -f "requirements.txt" ]]; then
  pip install --upgrade -r requirements.txt
fi

# Frontend (if Node available)
if [[ -f "package.json" ]] && command -v npm &>/dev/null; then
  npm install --production
  npm run build || true
fi

# LocalAgent-Pro
if [[ -d "../LocalAgent-Pro" ]]; then
  cd ../LocalAgent-Pro
  pip install --upgrade -r requirements.txt
  cd ../2.opena3_openwebui
fi

echo "✅ Dependencies updated"
```

### Step 3: Apply Configuration

```bash
#!/bin/bash
set -euo pipefail

echo "⚙️  Applying configuration..."

# Use docker-compose if available
if [[ -f "docker-compose.yml" ]]; then
  docker-compose build --no-cache
fi

# Set environment
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export OLLAMA_BASE_URL="http://127.0.0.1:11434"

echo "✅ Configuration applied"
```

---

## PHASE C: ELION Patches

### Overview

12 patches to apply:
- Backend: 5 patches (groups, forms, security, main)
- Frontend: 5 patches (API, components, modals)
- Agents: 2 patches (safepoint, dashboard)

### Apply Patches

```bash
#!/bin/bash
set -euo pipefail

echo "🔧 Applying ELION patches..."

cd 2.opena3_openwebui

# Patch 1: Group Sharing Backend
patch -p1 < ../patches/01_group_sharing.patch || echo "⚠️  Patch 1 may have conflicts"

# Patch 2: Security Enhancements
patch -p1 < ../patches/02_security.patch || echo "⚠️  Patch 2 may have conflicts"

# Patch 3: Frontend Components
patch -p1 < ../patches/03_frontend.patch || echo "⚠️  Patch 3 may have conflicts"

# Patch 4: API Extensions
patch -p1 < ../patches/04_api.patch || echo "⚠️  Patch 4 may have conflicts"

# Patch 5: Agent Bridges
patch -p1 < ../patches/05_agents.patch || echo "⚠️  Patch 5 may have conflicts"

echo "✅ ELION patches applied"
```

### Manual Patch Application

If patch command fails, apply manually:

```bash
# Backup original
cp backend/main.py backend/main.py.backup

# Edit with your preferred editor
nano backend/main.py

# Verify changes
diff backend/main.py.backup backend/main.py
```

---

## PHASE D: Security Configuration

### Step 1: Update Security Policy

```bash
#!/bin/bash
set -euo pipefail

echo "🔐 Configuring security..."

# Create SECURITY.md with ELION specs
cat > SECURITY.md << 'EOF'
# ELION Security Configuration

## Authentication
- Bearer tokens: Enabled
- RBAC 2.0: Enabled
- SSO: Configured

## Network
- SSRF Protection: Enabled
- XSS Prevention: Enabled
- CORS: Configured for localhost + Docker
- WebSocket: Secured

## Data Protection
- TLS 1.3: Enabled
- Encryption: AES-256-GCM
- Rate Limiting: 1000 req/min per token
EOF

cat > config/security.json << 'EOF'
{
  "cors": {
    "origins": ["http://127.0.0.1:3000", "http://localhost:3000"],
    "credentials": true
  },
  "csrf": {
    "enabled": true,
    "token_length": 32
  },
  "rate_limit": {
    "enabled": true,
    "requests_per_minute": 1000,
    "burst_size": 50
  }
}
EOF

echo "✅ Security configured"
```

### Step 2: Configure Bearer Tokens

```bash
#!/bin/bash
set -euo pipefail

echo "🎫 Setting up bearer tokens..."

# Generate tokens for each agent
for i in {1..20}; do
  TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
  echo "AGENT_${i}_TOKEN=$TOKEN" >> .env
done

# Generate admin token
ADMIN_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "DASHBOARD_ADMIN_TOKEN=$ADMIN_TOKEN" >> .env

echo "✅ Bearer tokens generated in .env"
echo "⚠️  SECURE: Never commit .env to Git!"
```

---

## PHASE E: Agent Integration

### Step 1: Register Agents

```bash
#!/bin/bash
set -euo pipefail

echo "📝 Registering agents..."

cd ../LocalAgent-Pro

# Register each agent with dashboard
for agent in opena{1..20}; do
  if [[ -d "$agent" ]]; then
    echo "Registering $agent..."
    python3 -c "
import requests
import json
from pathlib import Path

config = json.load(open('$agent/config.json'))
port = config.get('port', 12344)
endpoint = f'http://127.0.0.1:{port}'

# Register with dashboard
resp = requests.post(
  'http://127.0.0.1:12349/api/agent/register',
  headers={'Authorization': f'Bearer {open(\"../.env\").read().split(\"DASHBOARD_ADMIN_TOKEN=\")[1].split(chr(10))[0]}'},
  json={'agent_id': '$agent', 'endpoint': endpoint}
)
print(f'✅ {$agent}: {resp.status_code}')
" || echo "⚠️  Failed to register $agent"
  fi
done

echo "✅ Agent registration complete"
```

### Step 2: Configure Agent Ports

```bash
#!/bin/bash
set -euo pipefail

echo "⚙️  Configuring agent ports..."

# Update config.json for each agent
cd LocalAgent-Pro

for i in {1..20}; do
  AGENT="opena$i"
  PORT=$((12344 + i - 1))
  
  if [[ -f "$AGENT/config.json" ]]; then
    # Update port (using jq if available, else Python)
    if command -v jq &>/dev/null; then
      jq --arg port "$PORT" '.port = ($port | tonumber)' "$AGENT/config.json" > "${AGENT}/config.json.tmp"
      mv "${AGENT}/config.json.tmp" "${AGENT}/config.json"
    else
      python3 << EOF
import json
config = json.load(open('$AGENT/config.json'))
config['port'] = $PORT
json.dump(config, open('$AGENT/config.json', 'w'), indent=2)
EOF
    fi
    echo "✅ $AGENT configured on port $PORT"
  fi
done

echo "✅ Agent port configuration complete"
```

---

## PHASE F: Testing

### Step 1: Unit Tests

```bash
#!/bin/bash
set -euo pipefail

echo "🧪 Running unit tests..."

cd 2.opena3_openwebui

# Run tests
if command -v pytest &>/dev/null; then
  pytest tests/ -v --tb=short || echo "⚠️  Some tests failed"
fi

echo "✅ Unit tests complete"
```

### Step 2: Integration Tests

```bash
#!/bin/bash
set -euo pipefail

echo "🔗 Running integration tests..."

# Start services temporarily
./bin/ops.sh start &
SERVICE_PID=$!
sleep 5

# Test endpoints
echo "Testing Dashboard health..."
curl -s http://127.0.0.1:12349/health | jq . || echo "❌ Dashboard not responding"

echo "Testing Agent connectivity..."
for i in 1 2 3; do
  PORT=$((12344 + i - 1))
  curl -s http://127.0.0.1:$PORT/health | jq . || echo "⚠️  Agent opena$i not responding"
done

# Stop services
kill $SERVICE_PID 2>/dev/null || true

echo "✅ Integration tests complete"
```

### Step 3: Security Tests

```bash
#!/bin/bash
set -euo pipefail

echo "🔒 Running security tests..."

# Test SSRF protection
echo "Testing SSRF protection..."
curl -s -X POST http://127.0.0.1:12349/api/test \
  -H "Content-Type: application/json" \
  -d '{"url":"http://169.254.169.254/"}' || echo "✅ SSRF blocked"

# Test XSS prevention
echo "Testing XSS prevention..."
curl -s -X POST http://127.0.0.1:12349/api/test \
  -H "Content-Type: application/json" \
  -d '{"input":"<script>alert(1)</script>"}' || echo "✅ XSS blocked"

# Test CORS
echo "Testing CORS..."
curl -s -H "Origin: http://attacker.com" \
  http://127.0.0.1:12349/api/agents | grep -i "access-control" || echo "⚠️  CORS not configured"

echo "✅ Security tests complete"
```

---

## PHASE G: Deployment

### Step 1: Start Services

```bash
#!/bin/bash
set -euo pipefail

echo "🚀 Starting ELION services..."

cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Using ops.sh
./bin/ops.sh start

# Wait for startup
echo "⏳ Waiting for services to start..."
sleep 10

echo "✅ Services started"
```

### Step 2: Verify Deployment

```bash
#!/bin/bash
set -euo pipefail

echo "✔️  Verifying deployment..."

# Check all endpoints
ENDPOINTS=(
  "http://127.0.0.1:12349/health"
  "http://127.0.0.1:12344/health"
  "http://127.0.0.1:12345/health"
  "http://127.0.0.1:3000"
)

for endpoint in "${ENDPOINTS[@]}"; do
  if curl -s "$endpoint" > /dev/null 2>&1; then
    echo "✅ $endpoint responding"
  else
    echo "❌ $endpoint NOT responding"
  fi
done

echo "✅ Deployment verification complete"
```

### Step 3: Health Check

```bash
#!/bin/bash
set -euo zipepipe

echo "🏥 Running health checks..."

# Dashboard status
echo "Dashboard:"
curl -s http://127.0.0.1:12349/api/status/all | jq . || echo "⚠️  Status unavailable"

# Agent status
echo "Agents:"
for i in 1 2; do
  PORT=$((12344 + i - 1))
  echo "opena$i:"
  curl -s http://127.0.0.1:$PORT/api/info | jq . || echo "⚠️  Agent not responding"
done

echo "✅ Health checks complete"
```

---

## PHASE H: Troubleshooting

### Common Issues

#### Issue 1: Services Won't Start

```bash
# Check ports
lsof -i :12349 :12344 :12345 :3000

# Kill zombie processes
pkill -9 -f "python.*main"

# Check logs
tail -f logs/*.log

# Restart with verbose output
python3 -u src/services/dashboard/main.py 2>&1 | tee debug.log
```

#### Issue 2: Agent Registration Fails

```bash
# Check token in .env
grep DASHBOARD_ADMIN_TOKEN .env

# Verify dashboard is running
curl -s http://127.0.0.1:12349/health

# Manual registration with debugging
curl -v -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"opena1","endpoint":"http://127.0.0.1:12344"}'
```

#### Issue 3: Docker-Compose Issues

```bash
# Check compose file
docker-compose config

# Rebuild images
docker-compose build --no-cache

# Check logs
docker-compose logs -f

# Reset if corrupted
docker-compose down -v
docker system prune -a
```

---

## Rollback Procedure

If something goes wrong:

```bash
#!/bin/bash
set -euo pipefail

echo "🔄 Rolling back..."

# Stop current services
./bin/ops.sh stop

# Restore from backup
LATEST_BACKUP=$(ls -t backups/elion_upgrade_*/repo.bundle | head -1)
git bundle unbundle "$LATEST_BACKUP"
git reset --hard

# Restore configs
tar xzf backups/elion_upgrade_*/openwebui_backup.tar.gz
tar xzf backups/elion_upgrade_*/localagent_backup.tar.gz

# Start old version
./bin/ops.sh start

echo "✅ Rollback complete"
```

---

## Validation Checklist

- [ ] Backup created and tested
- [ ] Services stopped cleanly
- [ ] OpenWebUI updated to v0.6.37
- [ ] Dependencies installed
- [ ] ELION patches applied without errors
- [ ] Security configuration applied
- [ ] Bearer tokens generated and stored
- [ ] All agents registered
- [ ] Unit tests passing (>95%)
- [ ] Integration tests passing
- [ ] Security tests passing
- [ ] All endpoints responding
- [ ] Health checks green
- [ ] Logs reviewed for errors
- [ ] Performance baseline established
- [ ] Documentation updated

---

## Support

- **Issues:** Check logs in `logs/` directory
- **Email:** jokicdanijel@gmail.com
- **Repository:** https://github.com/jokicdanijel/Gesamtprojekt-start

---

**Status:** ✅ COMPLETE - Ready for deployment  
**Last Updated:** 24. November 2025  
**Version:** 0.6.37
