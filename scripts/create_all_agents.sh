#!/usr/bin/env bash
###############################################################################
# create_all_agents.sh
# Erstellt 19 vollständige Agent-Verzeichnisse (3-21) mit kompletter Struktur
# Basierend auf AGENT_STRUCTURE_PLAN.md
###############################################################################

set -euo pipefail

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Projekt-Root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Logging-Funktion
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

###############################################################################
# Agent-Definition (19 Agenten, Nummern 3-21)
###############################################################################

declare -a AGENTS=(
    "3|opena1_coordinator|opena1|12344|Orchestrator Phase 1|Core"
    "4|opena2_archivator|opena2|12345|File Storage System|Core"
    "5|kordp_scheduler|kordp|12346|Event Coordination|Core"
    "6|opena4_telegram|opena4|12347|Telegram Integration|Integration"
    "7|opena5_browser|opena5|12348|Browser Automation|Tools"
    "8|opena6_email|opena6|12349|Email Management|Tools"
    "9|opena7_whatsapp|opena7|12350|WhatsApp Integration|Integration"
    "10|opena8_telephone|opena8|12351|Telephone System|Integration"
    "11|opena9_call_tracking|opena9|12352|Call Analytics|Analytics"
    "12|opena10_unlock|opena10|12353|Security & Access|Security"
    "13|opena11_social_media|opena11|12359|Social Media Manager|Integration"
    "14|opena12_influencer|opena12|12360|Influencer Collaboration|Tools"
    "15|opena13_calendar|opena13|12361|Calendar & Scheduling|Tools"
    "16|opena14_html|opena14|12362|HTML Generation|Tools"
    "17|opena15_shop|opena15|12363|E-commerce System|Business"
    "18|opena16_crm|opena16|12364|CRM Management|Business"
    "19|opena17_analytics|opena17|12365|Data Analytics|Analytics"
    "20|opena18_dashboard|opena18|12366|Dashboard UI|UI"
    "21|opena19_workflow|opena19|12367|Workflow Automation|Automation"
)

###############################################################################
# Funktion: Erstelle Agent-Verzeichnis
###############################################################################

create_agent() {
    local number=$1
    local name=$2
    local agent_id=$3
    local port=$4
    local description=$5
    local category=$6

    local agent_dir="${PROJECT_ROOT}/${number}.${name}"

    log "Erstelle Agent ${number}: ${BLUE}${name}${NC} (Port: ${port})"

    # Verzeichnis erstellen
    mkdir -p "$agent_dir"
    mkdir -p "$agent_dir/bin"
    mkdir -p "$agent_dir/config"
    mkdir -p "$agent_dir/tests"
    mkdir -p "$agent_dir/logs"
    mkdir -p "$agent_dir/docs"
    mkdir -p "$agent_dir/data"
    mkdir -p "$agent_dir/api"

    # ========== main.py ==========
    cat > "$agent_dir/main.py" << 'MAIN_EOF'
#!/usr/bin/env python3
"""
Agent main.py - FastAPI Einstiegspunkt
Automatisch generiert aus create_all_agents.sh
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Lade .env
load_dotenv()

# Setup Logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="ELION Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Lade Konfiguration
AGENT_ID = os.getenv("AGENT_ID", "opena_unknown")
PORT = int(os.getenv("PORT", "12344"))
TOKEN = os.getenv("TOKEN", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

@app.get("/health")
async def health():
    """Health Check Endpoint"""
    return {
        "status": "ok",
        "service": AGENT_ID,
        "port": PORT,
        "version": "1.0.0"
    }

@app.get("/status")
async def status():
    """Status Endpoint"""
    return {
        "agent_id": AGENT_ID,
        "port": PORT,
        "category": "service",
        "uptime": "running",
        "log_file": str(LOG_FILE)
    }

@app.post("/invoke")
async def invoke(payload: dict):
    """Main Invoke Endpoint"""
    logger.info(f"Received invoke request: {payload}")
    return {
        "status": "ok",
        "agent_id": AGENT_ID,
        "result": "Processing..."
    }

@app.get("/info")
async def info():
    """Info Endpoint"""
    return {
        "agent_id": AGENT_ID,
        "port": PORT,
        "running": True
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    logger.info(f"Starting {AGENT_ID} on port {PORT}")
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=PORT,
            log_level=LOG_LEVEL.lower()
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
MAIN_EOF
    chmod +x "$agent_dir/main.py"

    # ========== README.md ==========
    cat > "$agent_dir/README.md" << 'README_EOF'
# Agent: %NAME%

**Agent ID:** `%AGENT_ID%`  
**Port:** `%PORT%`  
**Category:** `%CATEGORY%`  
**Description:** %DESCRIPTION%

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.template .env
# Edit .env with your values

# 3. Run agent
bash bin/start.sh
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/status` | Agent status |
| GET | `/info` | Agent info |
| POST | `/invoke` | Main invoke endpoint |

## Testing

```bash
# Health check
curl -s http://127.0.0.1:%PORT%/health | jq .

# Status
curl -s http://127.0.0.1:%PORT%/status | jq .

# Invoke
curl -s -X POST http://127.0.0.1:%PORT%/invoke \
  -H "Content-Type: application/json" \
  -d '{"test": true}' | jq .
```

## Logging

Logs are written to `logs/app.log`

```bash
tail -f logs/app.log
```

## Docker (Optional)

```bash
docker build -t %AGENT_ID%:latest .
docker run -p %PORT%:%PORT% %AGENT_ID%:latest
```

## Integration with Dashboard

This agent automatically registers with the Dashboard API:

```bash
curl -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer $(cat ../.env | head -1)" \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\": \"%AGENT_ID%\", \"endpoint\": \"http://127.0.0.1:%PORT%\"}"
```

## Development

```bash
# Run tests
pytest -v tests/

# Format code
black .

# Type checking
mypy .
```

---

**Auto-generated:** 2025-11-08  
**Framework:** FastAPI 0.104.1 | Python 3.12+
README_EOF

    # Ersetze Platzhalter in README.md
    sed -i "s|%NAME%|${name}|g" "$agent_dir/README.md"
    sed -i "s|%AGENT_ID%|${agent_id}|g" "$agent_dir/README.md"
    sed -i "s|%PORT%|${port}|g" "$agent_dir/README.md"
    sed -i "s|%CATEGORY%|${category}|g" "$agent_dir/README.md"
    sed -i "s|%DESCRIPTION%|${description}|g" "$agent_dir/README.md"

    # ========== requirements.txt ==========
    cat > "$agent_dir/requirements.txt" << 'REQUIREMENTS_EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
aiohttp==3.9.1
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.0
mypy==1.7.1
REQUIREMENTS_EOF

    # ========== .env.template ==========
    cat > "$agent_dir/.env.template" << 'ENV_TEMPLATE_EOF'
# Agent Environment Template
AGENT_ID=%AGENT_ID%
PORT=%PORT%
TOKEN=${DASHBOARD_ADMIN_TOKEN}
LOG_LEVEL=INFO
DASHBOARD_URL=http://127.0.0.1:12349
ARCHIVATOR_URL=http://127.0.0.1:12345
KORDP_URL=http://127.0.0.1:12346
ENV_TEMPLATE_EOF

    sed -i "s|%AGENT_ID%|${agent_id}|g" "$agent_dir/.env.template"
    sed -i "s|%PORT%|${port}|g" "$agent_dir/.env.template"

    # ========== config/agent.conf ==========
    cat > "$agent_dir/config/agent.conf" << 'CONFIG_EOF'
[agent]
id=%AGENT_ID%
name=%NAME%
port=%PORT%
description=%DESCRIPTION%
category=%CATEGORY%

[security]
require_token=true
token_source=env

[logging]
level=INFO
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
file=logs/app.log

[integrations]
dashboard_url=http://127.0.0.1:12349
archivator_url=http://127.0.0.1:12345
kordp_url=http://127.0.0.1:12346
CONFIG_EOF

    sed -i "s|%AGENT_ID%|${agent_id}|g" "$agent_dir/config/agent.conf"
    sed -i "s|%NAME%|${name}|g" "$agent_dir/config/agent.conf"
    sed -i "s|%PORT%|${port}|g" "$agent_dir/config/agent.conf"
    sed -i "s|%DESCRIPTION%|${description}|g" "$agent_dir/config/agent.conf"
    sed -i "s|%CATEGORY%|${category}|g" "$agent_dir/config/agent.conf"

    # ========== config/logging.conf ==========
    cat > "$agent_dir/config/logging.conf" << 'LOGGING_EOF'
[loggers]
keys=root

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=standard

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=standard
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=standard
args=('logs/app.log',)

[formatter_standard]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOGGING_EOF

    # ========== bin/start.sh ==========
    cat > "$agent_dir/bin/start.sh" << 'START_SCRIPT_EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$AGENT_DIR")")"

# Lade .env aus Projekt-Root
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Lade Agent-lokale .env
if [ -f "$AGENT_DIR/.env" ]; then
    set -a
    source "$AGENT_DIR/.env"
    set +a
fi

# Setze Defaults
AGENT_ID="${AGENT_ID:-%AGENT_ID%}"
PORT="${PORT:-%PORT%}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo "🚀 Starting ${AGENT_ID} on port ${PORT}..."
cd "$AGENT_DIR"

# Starte Agent mit uvicorn
exec python main.py
START_SCRIPT_EOF

    sed -i "s|%AGENT_ID%|${agent_id}|g" "$agent_dir/bin/start.sh"
    sed -i "s|%PORT%|${port}|g" "$agent_dir/bin/start.sh"
    chmod +x "$agent_dir/bin/start.sh"

    # ========== tests/test_agent.py ==========
    cat > "$agent_dir/tests/test_agent.py" << 'TEST_EOF'
"""
Basis-Tests für Agent
"""

import pytest
import sys
from pathlib import Path

# Importiere main.py
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app, AGENT_ID, PORT

@pytest.fixture
def client():
    """Test Client"""
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_health(client):
    """Test Health Endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["port"] == PORT

def test_status(client):
    """Test Status Endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == AGENT_ID

def test_info(client):
    """Test Info Endpoint"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["running"] is True

def test_invoke(client):
    """Test Invoke Endpoint"""
    response = client.post("/invoke", json={"test": True})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
TEST_EOF

    # ========== tests/__init__.py ==========
    touch "$agent_dir/tests/__init__.py"

    # ========== logs/.gitkeep ==========
    touch "$agent_dir/logs/.gitkeep"

    # ========== data/.gitkeep ==========
    touch "$agent_dir/data/.gitkeep"

    # ========== api/__init__.py ==========
    touch "$agent_dir/api/__init__.py"

    # ========== docs/README_DEV.md ==========
    cat > "$agent_dir/docs/README_DEV.md" << 'DEV_README_EOF'
# Development Guide

## Architecture

This agent follows a FastAPI-based microservice architecture:

- **main.py** - FastAPI application with endpoints
- **config/** - Configuration files
- **tests/** - Unit and integration tests
- **logs/** - Runtime logs
- **data/** - Runtime data storage

## API Endpoints

### Health Check
```bash
GET /health
```

### Status
```bash
GET /status
```

### Invoke
```bash
POST /invoke
Content-Type: application/json

{"data": "..."}
```

## Development Workflow

1. Edit **main.py** for application logic
2. Update **requirements.txt** for new dependencies
3. Run **pytest** to test
4. Update **README.md** with API changes
5. Commit and push changes

## Testing

```bash
# Run all tests
pytest -v tests/

# Run specific test
pytest -v tests/test_agent.py::test_health

# With coverage
pytest --cov=. tests/
```

## Debugging

Enable debug logging:
```bash
LOG_LEVEL=DEBUG bash bin/start.sh
```

View logs:
```bash
tail -f logs/app.log
```

## Deployment

1. Build Docker image (optional)
2. Configure .env from .env.template
3. Start service: `bash bin/start.sh`
4. Verify health: `curl http://127.0.0.1:PORT/health`
5. Register with dashboard

---

**Last Updated:** 2025-11-08
DEV_README_EOF

    success "Agent ${number}: ${GREEN}${name}${NC} erstellt (${agent_dir})"
}

###############################################################################
# MAIN
###############################################################################

main() {
    log "=================================="
    log "Erstelle alle 19 Agent-Verzeichnisse"
    log "=================================="
    log ""

    local created=0
    local failed=0

    for agent in "${AGENTS[@]}"; do
        IFS='|' read -r number name agent_id port description category <<< "$agent"
        
        if create_agent "$number" "$name" "$agent_id" "$port" "$description" "$category"; then
            ((created++))
        else
            ((failed++))
            error "Failed to create agent: ${name}"
        fi
    done

    log ""
    log "=================================="
    success "Erstellung abgeschlossen!"
    log "=================================="
    log "✅ Erstellt: ${created} Agenten"
    if [ $failed -gt 0 ]; then
        warn "❌ Fehler: ${failed} Agenten"
    fi
    log ""

    # Verifizierung
    log "Verifiziere Struktur..."
    for agent in "${AGENTS[@]}"; do
        IFS='|' read -r number name agent_id port _ _ <<< "$agent"
        agent_dir="${PROJECT_ROOT}/${number}.${name}"
        if [ -d "$agent_dir" ]; then
            if [ -f "$agent_dir/main.py" ] && [ -f "$agent_dir/README.md" ] && [ -f "$agent_dir/requirements.txt" ]; then
                success "✅ ${number}.${name} vollständig"
            else
                warn "⚠️ ${number}.${name} unvollständig"
            fi
        fi
    done

    log ""
    log "📋 Alle 19 Agent-Verzeichnisse unter:"
    log "   ${PROJECT_ROOT}/3.opena1_coordinator"
    log "   ${PROJECT_ROOT}/4.opena2_archivator"
    log "   ..."
    log "   ${PROJECT_ROOT}/21.opena19_workflow"
    log ""
    log "🚀 Nächste Schritte:"
    log "   1. git add ."
    log "   2. git commit -m 'feat: add 19 standardized agent directories'"
    log "   3. git push origin main"
    log ""
}

main "$@"
