# 🤖 ELION Agent Lifecycle Guide (opena5 VSCode Agent)

**Vollständiger Workflow:** Scannen → Analysieren → Erweitern → Prüfen → Starten → Testen → Deployment → Integration

Dieses Guide zeigt den kompletten Lifecycle am Beispiel **opena5 (VSCode Agent)** von `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/4.opena5_vscode` bis zum produktiven Deployment auf `www.hyperdashboard-one.de/opena5/`.

---

## 📋 Projekt-Kontext

- **Agent:** opena5 - VSCode Integration Agent
- **Lokaler Pfad:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/4.opena5_vscode`
- **Port:** 12350 (siehe [AGENT_STRUCTURE.md](AGENT_STRUCTURE.md))
- **Kategorie:** Connector-Agent
- **Deployment-Ziel:** `www.hyperdashboard-one.de/opena5/`
- **Dashboard:** opena20 (Port 12348)

### Voraussetzungen

```bash
# Required Tools
python3 --version          # >= 3.11
docker --version           # >= 24.0
git --version             # >= 2.40
jq --version              # >= 1.6 (für JSON-Parsing)

# Optional (für erweiterte Checks)
gh --version              # GitHub CLI
rsync --version           # Für Hetzner-Deployment
```

---

## 📁 SCHRITT 1: SCANNEN

**Ziel:** Vollständige Analyse der Verzeichnisstruktur und Dependencies

### 1.1 Verzeichnisstruktur scannen

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/4.opena5_vscode

# Basis-Scan
tree -L 2 -a

# Erwartete Struktur:
# 4.opena5_vscode/
# ├── main.py              # Haupt-Entrypoint
# ├── requirements.txt     # Python-Dependencies
# ├── config/              # Konfigurationsdateien
# ├── venv/                # Virtual Environment
# ├── logs/                # Log-Dateien
# ├── Dockerfile           # Container-Definition (optional)
# └── tests/               # Test-Suite (optional)
```

### 1.2 Agent-Registry prüfen

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Validiere Agent-Existenz
cat agent_directories.json | jq '.agents[] | select(.name=="opena5")'

# Erwartete Ausgabe:
# {
#   "name": "opena5",
#   "port": 12350,
#   "folder": "4.opena5_vscode",
#   "fullpath": "Gesamtprojekt/4.opena5_vscode"
# }
```

### 1.3 Port-Mapping validieren

```bash
# Prüfe Port-Konflikte
bash scripts/validate_agent_directories.sh

# Prüfe ob Port 12350 bereits belegt
lsof -i :12350 || echo "Port 12350 frei"
```

---

## 🔍 SCHRITT 2: ANALYSIEREN

**Ziel:** Code-Qualität, Dependencies, Konfiguration und Sicherheit prüfen

### 2.1 Python-Syntax-Check

```bash
cd 4.opena5_vscode

# Syntax-Validation
python3 -m py_compile main.py
python3 -m py_compile config/*.py 2>/dev/null || echo "No config modules"

# Erweiterte Code-Analyse (optional)
if command -v pylint &> /dev/null; then
    pylint main.py --disable=C,R --reports=n
fi
```

### 2.2 Dependencies analysieren

```bash
# Prüfe requirements.txt
if [ -f requirements.txt ]; then
    echo "✅ requirements.txt gefunden"
    cat requirements.txt

    # Validiere Syntax
    pip3 install --dry-run -r requirements.txt 2>&1 | tee /tmp/pip_check.log
else
    echo "❌ requirements.txt fehlt - muss erstellt werden!"
fi
```

### 2.3 Umgebungsvariablen prüfen

```bash
# Check für .env oder Secrets
if [ -f .env ]; then
    echo "⚠️  .env gefunden - prüfe ob in .gitignore"
    grep -q "^.env$" .gitignore && echo "✅ .env wird ignoriert" || echo "❌ .env NICHT in .gitignore!"
fi

# Prüfe auf hartcodierte Secrets (via grep)
grep -rE "(api_key|secret|password|token).*=.*['\"][^'\"]{8,}" . --exclude-dir=venv --exclude="*.log" || echo "✅ Keine offensichtlichen Secrets gefunden"
```

### 2.4 Docker-Setup prüfen (falls vorhanden)

```bash
# Dockerfile validieren
if [ -f Dockerfile ]; then
    echo "✅ Dockerfile gefunden"
    docker build --no-cache --progress=plain -t opena5-test . --target test 2>&1 | tee /tmp/docker_build.log

    # Check für bekannte Probleme
    grep -E "(WORKDIR|COPY|RUN)" Dockerfile | head -10
fi
```

### 2.5 Gate-Reports erstellen

```bash
# Security Gate (angepasst für Agent-Verzeichnis)
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Führe Preflight-Check aus (angepasst für opena5)
if [ -f css/scripts/preflight_check.py ]; then
    # Adaptiere für Agent-Verzeichnis (vereinfachte Version)
    python3 << 'PYTHON'
import os
import json
import re
from pathlib import Path

agent_dir = Path("4.opena5_vscode")
report = {
    "agent": "opena5",
    "path": str(agent_dir.absolute()),
    "checks": {}
}

# Check 1: main.py existiert
report["checks"]["main_py"] = agent_dir.joinpath("main.py").exists()

# Check 2: requirements.txt existiert
report["checks"]["requirements"] = agent_dir.joinpath("requirements.txt").exists()

# Check 3: Port 12350 in Code referenziert
try:
    main_content = agent_dir.joinpath("main.py").read_text()
    report["checks"]["port_configured"] = "12350" in main_content
except:
    report["checks"]["port_configured"] = False

# Check 4: No hardcoded secrets
secret_patterns = [
    r'api_key\s*=\s*["\'][^"\']{20,}["\']',
    r'sk-[A-Za-z0-9]{20,}',
    r'ghp_[A-Za-z0-9]{20,}'
]
has_secrets = False
for py_file in agent_dir.rglob("*.py"):
    if "venv" in str(py_file):
        continue
    try:
        content = py_file.read_text()
        for pattern in secret_patterns:
            if re.search(pattern, content):
                has_secrets = True
                break
    except:
        pass
report["checks"]["no_secrets"] = not has_secrets

print(json.dumps(report, indent=2))
PYTHON
fi
```

---

## 🛠️ SCHRITT 3: ERWEITERN

**Ziel:** Features hinzufügen, Code verbessern, Tests erweitern

### 3.1 Neue Feature-Branch erstellen

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Branch erstellen
FEATURE_NAME="opena5/add-tracing"
git checkout -b "${FEATURE_NAME}"

# Bestätige Branch
git branch --show-current
```

### 3.2 Tracing-Integration (Beispiel)

```bash
cd 4.opena5_vscode

# Füge Tracing-Dependencies hinzu
cat >> requirements.txt << 'EOF'
# Tracing
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp>=1.20.0
EOF

# Erstelle Tracing-Setup-Modul
mkdir -p src/tracing
cat > src/tracing/setup.py << 'PYTHON'
"""OpenTelemetry Tracing Setup für opena5"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_tracing(service_name: str = "opena5-vscode", endpoint: str = "http://localhost:4317"):
    """Initialisiere OpenTelemetry Tracing"""
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
PYTHON
```

### 3.3 Tests erweitern

```bash
# Erstelle Test-Struktur
mkdir -p tests
cat > tests/test_opena5_basic.py << 'PYTHON'
"""Basis-Tests für opena5"""
import pytest
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import_main():
    """Test: main.py kann importiert werden"""
    import main
    assert hasattr(main, '__name__')

def test_port_configured():
    """Test: Port 12350 ist konfiguriert"""
    import main
    # Annahme: main.py hat PORT Variable
    assert hasattr(main, 'PORT') or '12350' in Path('main.py').read_text()

# Run: pytest tests/test_opena5_basic.py -v
PYTHON

# Test ausführen
pip3 install pytest
pytest tests/test_opena5_basic.py -v
```

---

## ✅ SCHRITT 4: PRÜFEN

**Ziel:** Vollständige Validierung vor Deployment

### 4.1 Preflight-Checks

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Führe ALLE Checks aus
echo "🔍 Running Preflight Checks für opena5..."

# 1. Python-Syntax
echo "[1/5] Python Syntax Check..."
python3 -m py_compile 4.opena5_vscode/main.py && echo "✅ Syntax OK" || { echo "❌ Syntax ERROR"; exit 1; }

# 2. Dependencies
echo "[2/5] Dependencies Check..."
cd 4.opena5_vscode
pip3 install --dry-run -r requirements.txt &> /dev/null && echo "✅ Dependencies OK" || { echo "❌ Dependencies ERROR"; exit 1; }
cd ..

# 3. Port-Konflikt
echo "[3/5] Port Conflict Check..."
! lsof -i :12350 && echo "✅ Port 12350 frei" || echo "⚠️  Port 12350 belegt"

# 4. Git-Status
echo "[4/5] Git Status Check..."
git status --porcelain | grep -q "^" && echo "⚠️  Uncommitted changes" || echo "✅ Git clean"

# 5. Tests
echo "[5/5] Unit Tests..."
if [ -d "4.opena5_vscode/tests" ]; then
    cd 4.opena5_vscode
    pytest tests/ -q && echo "✅ Tests PASSED" || echo "❌ Tests FAILED"
    cd ..
else
    echo "⚠️  No tests found"
fi
```

### 4.2 Security-Scan

```bash
# Secret-Detection (via grep)
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

echo "🔒 Security Scan für opena5..."
grep -rE "(sk-|ghp_|AKIA|bearer |authorization:|BEGIN PRIVATE KEY)" 4.opena5_vscode/ \
    --exclude-dir=venv --exclude="*.log" --exclude="*.pyc" && \
    echo "❌ SECRETS GEFUNDEN!" || \
    echo "✅ Keine Secrets gefunden"
```

### 4.3 Docker-Build-Test (optional)

```bash
cd 4.opena5_vscode

if [ -f Dockerfile ]; then
    echo "🐳 Docker Build Test..."
    docker build -t opena5:test . && \
        echo "✅ Docker Build OK" || \
        echo "❌ Docker Build FAILED"
fi
```

---

## 🚀 SCHRITT 5: STARTEN

**Ziel:** Lokaler Start des Agenten für manuelle Tests

### 5.1 Virtual Environment Setup

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/4.opena5_vscode

# Erstelle venv (falls nicht vorhanden)
if [ ! -d venv ]; then
    python3 -m venv venv
    echo "✅ venv erstellt"
fi

# Aktiviere venv
source venv/bin/activate

# Installiere Dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "✅ Environment bereit"
```

### 5.2 Lokaler Start

```bash
# Starte Agent im Vordergrund (für Debugging)
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/4.opena5_vscode
source venv/bin/activate

# Start mit Logging
python3 main.py 2>&1 | tee logs/opena5_$(date +%Y%m%d_%H%M%S).log

# ODER im Hintergrund:
nohup python3 main.py > logs/opena5.log 2>&1 &
echo $! > /tmp/opena5.pid
echo "✅ opena5 gestartet (PID: $(cat /tmp/opena5.pid))"
```

### 5.3 Health-Check

```bash
# Warte auf Startup
sleep 5

# HTTP Health-Check (annahme: Agent hat /health Endpoint)
curl -f http://localhost:12350/health && \
    echo "✅ opena5 läuft" || \
    echo "❌ opena5 antwortet nicht"

# Port-Check
lsof -i :12350 && echo "✅ Port 12350 aktiv" || echo "❌ Port 12350 inaktiv"

# Logs prüfen
tail -n 20 logs/opena5.log
```

---

## 🧪 SCHRITT 6: TESTEN

**Ziel:** Funktionale Tests und Integration mit Dashboard

### 6.1 Unit-Tests

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/4.opena5_vscode

# Alle Tests ausführen
pytest tests/ -v --tb=short

# Mit Coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### 6.2 Integration-Tests (mit Dashboard)

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Starte Dashboard (opena20) falls nicht läuft
if ! lsof -i :12348 &> /dev/null; then
    echo "🚀 Starte Dashboard opena20..."
    cd 19.opena20_dashboard_agent
    nohup python3 main_dashboard_v3.py > logs/dashboard.log 2>&1 &
    cd ..
    sleep 3
fi

# Prüfe Dashboard-Agent-Discovery
curl -s http://localhost:12348/api/agents | jq '.agents[] | select(.name=="opena5")'

# Erwartete Ausgabe:
# {
#   "name": "opena5",
#   "port": 12350,
#   "status": "running",
#   "health": "healthy"
# }
```

### 6.3 Manueller Funktionstest

```bash
# Beispiel: VSCode-Integration testen
# (angepasst an tatsächliche opena5-API)

# Test 1: Agent-Info abrufen
curl http://localhost:12350/info

# Test 2: Feature-Aufruf (Beispiel: Code-Formatting)
curl -X POST http://localhost:12350/format \
  -H "Content-Type: application/json" \
  -d '{"file": "test.py", "content": "def foo():pass"}'

# Test 3: WebSocket-Verbindung (falls implementiert)
websocat ws://localhost:12350/ws
```

---

## 📦 SCHRITT 7: DEPLOYMENT

**Ziel:** Upload auf `www.hyperdashboard-one.de/opena5/`

### 7.1 Pre-Deployment-Checks

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Vollständiger Preflight (nochmal)
bash css/bin/deploy.sh preflight-only

# Git-Status
git status --porcelain
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Uncommitted changes - commit first!"
    exit 1
fi

# Agent läuft lokal?
lsof -i :12350 || { echo "❌ opena5 läuft nicht lokal"; exit 1; }
```

### 7.2 Production-Build erstellen

```bash
cd 4.opena5_vscode

# Freeze Dependencies
pip freeze > requirements.lock

# Erstelle Deployment-Artefakte
mkdir -p dist/opena5
rsync -av --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' \
    --exclude='logs/*.log' --exclude='.git' \
    . dist/opena5/

# Erstelle Deployment-Manifest
cat > dist/opena5/MANIFEST.json << JSON
{
  "agent": "opena5",
  "version": "$(date +%Y.%m.%d)",
  "port": 12350,
  "deployment_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "git_commit": "$(git rev-parse HEAD)"
}
JSON

echo "✅ Production-Build erstellt: dist/opena5/"
```

### 7.3 Deployment auf Hetzner (<www.hyperdashboard-one.de>)

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Prüfe deploy-Skript
if [ -f bin/deploy_to_hetzner.sh ]; then
    # Deployment durchführen
    bash bin/deploy_to_hetzner.sh opena5
else
    # Manuelles rsync-Deployment
    HETZNER_HOST="root@hyperdashboard-one.de"
    REMOTE_PATH="/var/www/hyperdashboard/agents/opena5"

    echo "📤 Deploying opena5 nach $HETZNER_HOST..."

    # Upload Artefakte
    rsync -avz --delete \
        4.opena5_vscode/dist/opena5/ \
        "${HETZNER_HOST}:${REMOTE_PATH}/"

    # Remote-Setup
    ssh "${HETZNER_HOST}" << 'REMOTE'
cd /var/www/hyperdashboard/agents/opena5

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Service neu starten (systemd)
sudo systemctl restart opena5.service
sudo systemctl status opena5.service

# Health-Check
sleep 3
curl -f http://localhost:12350/health && echo "✅ opena5 deployed" || echo "❌ Deployment failed"
REMOTE
fi
```

### 7.4 DNS & Reverse-Proxy konfigurieren

```bash
# Auf Hetzner-Server (SSH)
ssh root@hyperdashboard-one.de

# Nginx-Config für opena5
cat > /etc/nginx/sites-available/opena5 << 'NGINX'
server {
    listen 80;
    server_name hyperdashboard-one.de;

    location /opena5/ {
        proxy_pass http://localhost:12350/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # WebSocket-Support
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
NGINX

# Aktiviere Config
ln -sf /etc/nginx/sites-available/opena5 /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Prüfe öffentliche URL
curl -f https://www.hyperdashboard-one.de/opena5/health
```

---

## 🔗 SCHRITT 8: VERBINDEN (Integration)

**Ziel:** Agent mit Dashboard und anderen Agents verbinden

### 8.1 Dashboard-Integration

```bash
# Auf Hetzner: Dashboard-Config aktualisieren
ssh root@hyperdashboard-one.de

cd /var/www/hyperdashboard/19.opena20_dashboard_agent

# Agent in Registry eintragen
cat >> config/agent_registry.json << JSON
{
  "opena5": {
    "name": "opena5",
    "display_name": "VSCode Integration",
    "port": 12350,
    "url": "/opena5",
    "category": "connector",
    "health_endpoint": "/health",
    "icon": "🆚"
  }
}
JSON

# Dashboard neu starten
sudo systemctl restart opena20-dashboard.service
```

### 8.2 Entitlements konfigurieren

```bash
# Plan-Zugriff konfigurieren (siehe entitlements-client.js)
cd /var/www/hyperdashboard/build

# entitlements.json aktualisieren
jq '.plans.basic.agents.opena5 = {
  "visible": true,
  "clickable": false,
  "gates": ["requires_upgrade"],
  "reason": "VSCode Integration requires Pro Plan",
  "limits": {}
}' entitlements.json > entitlements.tmp && mv entitlements.tmp entitlements.json

jq '.plans.pro.agents.opena5 = {
  "visible": true,
  "clickable": true,
  "gates": [],
  "reason": "full_access",
  "limits": {
    "workflow_limit": 100
  }
}' entitlements.json > entitlements.tmp && mv entitlements.tmp entitlements.json

echo "✅ Entitlements aktualisiert"
```

### 8.3 Agent-Fleet-Integration

```bash
# Docker-Compose Update (falls Agent containerisiert)
cd /var/www/hyperdashboard

cat >> docker-compose.yml << 'YAML'
  opena5:
    image: hyperdashboard/opena5:latest
    container_name: opena5-vscode
    restart: unless-stopped
    ports:
      - "12350:12350"
    networks:
      - agents-network
    environment:
      - AGENT_NAME=opena5
      - DASHBOARD_URL=http://opena20:12348
    volumes:
      - ./4.opena5_vscode:/app
      - opena5-logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:12350/health"]
      interval: 30s
      timeout: 10s
      retries: 3
YAML

# Starte Agent im Fleet
docker-compose up -d opena5

# Prüfe Status
docker-compose ps opena5
docker logs opena5-vscode --tail 50
```

### 8.4 Finaler Verbindungstest

```bash
# Von lokalem Rechner
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Test 1: Öffentliche URL
curl -f https://www.hyperdashboard-one.de/opena5/health

# Test 2: Dashboard sieht Agent
curl -s https://www.hyperdashboard-one.de/api/agents | \
    jq '.agents[] | select(.name=="opena5")'

# Test 3: Agent-Fleet-Inventory
curl -s https://www.hyperdashboard-one.de/api/fleet/inventory | \
    jq '.services[] | select(.service_name | contains("opena5"))'

# Test 4: WebUI-Zugriff
# Browser: https://www.hyperdashboard-one.de/
# → Dashboard öffnen
# → opena5 Karte sollte sichtbar sein
# → Click sollte zu /opena5/ weiterleiten
```

---

## 📊 VERIFIZIERUNG & MONITORING

### Post-Deployment-Checks

```bash
# Health-Status
curl https://www.hyperdashboard-one.de/opena5/health | jq

# Logs prüfen (Hetzner)
ssh root@hyperdashboard-one.de "tail -f /var/www/hyperdashboard/agents/opena5/logs/opena5.log"

# Systemd-Status
ssh root@hyperdashboard-one.de "sudo systemctl status opena5.service"

# Docker-Status (falls containerisiert)
ssh root@hyperdashboard-one.de "docker logs opena5-vscode --tail 100"
```

### Monitoring-Setup

```bash
# Prometheus-Exporter für opena5 (optional)
# Füge Metrics-Endpoint hinzu in main.py

# Grafana-Dashboard konfigurieren
# Panel: opena5_requests_total, opena5_response_time_seconds
```

---

## 🔄 ROLLBACK (Falls nötig)

```bash
# Git-basierter Rollback
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Vorherigen Release-Tag finden
PREV_TAG=$(git describe --tags --abbrev=0 HEAD~1)
echo "Rollback zu: $PREV_TAG"

# Hetzner: Code auf vorherige Version zurücksetzen
ssh root@hyperdashboard-one.de << REMOTE
cd /var/www/hyperdashboard/agents/opena5
git fetch --tags
git checkout $PREV_TAG
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart opena5.service
REMOTE

echo "✅ Rollback abgeschlossen"
```

---

## 📚 WICHTIGE REFERENZEN

- **Agent-Struktur:** [AGENT_STRUCTURE.md](AGENT_STRUCTURE.md)
- **Deployment-Checklist:** [19.opena20_dashboard_agent/webpanel/DEPLOYMENT_CHECKLIST.md](../19.opena20_dashboard_agent/webpanel/DEPLOYMENT_CHECKLIST.md)
- **Rollback-Guide:** [19.opena20_dashboard_agent/webpanel/ROLLBACK_QUICKREF.md](../19.opena20_dashboard_agent/webpanel/ROLLBACK_QUICKREF.md)
- **Backup-Strategie:** [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md)

---

## 🆘 TROUBLESHOOTING

### Problem: Agent startet nicht lokal

```bash
# Check 1: Virtual Environment
cd 4.opena5_vscode
source venv/bin/activate
python3 -c "import sys; print(sys.executable)"

# Check 2: Dependencies
pip list | grep -E "(flask|fastapi|opentelemetry)"

# Check 3: Port-Konflikt
lsof -i :12350
# Falls belegt: kill $(lsof -t -i :12350)

# Check 4: Logs
tail -n 50 logs/opena5.log
```

### Problem: Deployment schlägt fehl

```bash
# Check 1: SSH-Zugriff
ssh root@hyperdashboard-one.de "uptime"

# Check 2: Remote-Verzeichnis
ssh root@hyperdashboard-one.de "ls -la /var/www/hyperdashboard/agents/opena5"

# Check 3: Systemd-Logs
ssh root@hyperdashboard-one.de "journalctl -u opena5.service -n 50"
```

### Problem: Dashboard zeigt Agent nicht

```bash
# Check 1: Agent-Registry
ssh root@hyperdashboard-one.de "cat /var/www/hyperdashboard/19.opena20_dashboard_agent/config/agent_registry.json | jq '.opena5'"

# Check 2: Dashboard-Logs
ssh root@hyperdashboard-one.de "tail -f /var/www/hyperdashboard/19.opena20_dashboard_agent/logs/dashboard.log | grep opena5"

# Check 3: Nginx-Config
ssh root@hyperdashboard-one.de "nginx -t"
```

---

## ✅ CHECKLISTE: Kompletter Lifecycle

- [ ] **SCANNEN:** Verzeichnisstruktur und agent_directories.json validiert
- [ ] **ANALYSIEREN:** Python-Syntax, Dependencies, Secrets geprüft
- [ ] **ERWEITERN:** Features implementiert, Tests hinzugefügt
- [ ] **PRÜFEN:** Preflight-Checks, Security-Scan, Tests PASSED
- [ ] **STARTEN:** Agent läuft lokal auf Port 12350
- [ ] **TESTEN:** Unit-Tests, Integration-Tests, Health-Check OK
- [ ] **DEPLOYMENT:** Artefakte auf Hetzner deployed, Nginx konfiguriert
- [ ] **VERBINDEN:** Dashboard sieht Agent, Entitlements konfiguriert, Fleet-Integration OK

---

**🎉 FERTIG!** opena5 ist jetzt vollständig integriert und läuft auf `www.hyperdashboard-one.de/opena5/`
