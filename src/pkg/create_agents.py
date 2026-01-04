#!/usr/bin/env python3
"""
create_agents.py - Erstelle alle 19 Agent-Verzeichnisse
"""

import os
from datetime import datetime
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).parent.absolute()
os.chdir(PROJECT_ROOT)

# Agent-Definition: (number, name, agent_id, port, description, category)
AGENTS = [
    (3, "opena1_coordinator", "opena1", 12344, "Orchestrator Phase 1", "Core"),
    (4, "opena2_archivator", "opena2", 12345, "File Storage System", "Core"),
    (5, "kordp_scheduler", "kordp", 12346, "Event Coordination", "Core"),
    (6, "opena4_telegram", "opena4", 12347, "Telegram Integration", "Integration"),
    (7, "opena5_browser", "opena5", 12346, "Browser Automation", "Tools"),
    (8, "opena6_email", "opena6", 12349, "Email Management", "Tools"),
    (9, "opena7_whatsapp", "opena7", 12350, "WhatsApp Integration", "Integration"),
    (10, "opena8_telephone", "opena8", 12351, "Telephone System", "Integration"),
    (11, "opena9_call_tracking", "opena9", 12352, "Call Analytics", "Analytics"),
    (12, "opena10_unlock", "opena10", 12353, "Security & Access", "Security"),
    (13, "opena11_social_media", "opena11", 12359, "Social Media Manager", "Integration"),
    (14, "opena12_influencer", "opena12", 12360, "Influencer Collaboration", "Tools"),
    (15, "opena13_calendar", "opena13", 12361, "Calendar & Scheduling", "Tools"),
    (16, "opena14_html", "opena14", 12362, "HTML Generation", "Tools"),
    (17, "opena15_shop", "opena15", 12363, "E-commerce System", "Business"),
    (18, "opena16_crm", "opena16", 12364, "CRM Management", "Business"),
    (19, "opena17_analytics", "opena17", 12365, "Data Analytics", "Analytics"),
    (20, "opena18_dashboard", "opena18", 12366, "Dashboard UI", "UI"),
    (21, "opena19_workflow", "opena19", 12367, "Workflow Automation", "Automation"),
]

# Templates
MAIN_PY = """#!/usr/bin/env python3
\"\"\"Agent main.py - FastAPI Einstiegspunkt\"\"\"

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ELION Agent", version="1.0.0", docs_url="/docs")

AGENT_ID = os.getenv("AGENT_ID", "opena_unknown")
PORT = int(os.getenv("PORT", "12344"))

@app.get("/health")
async def health():
    return {"status": "ok", "service": AGENT_ID, "port": PORT, "version": "1.0.0"}

@app.get("/status")
async def status():
    return {"agent_id": AGENT_ID, "port": PORT, "uptime": "running", "log_file": str(LOG_FILE)}

@app.post("/invoke")
async def invoke(payload: dict):
    logger.info(f"Invoke: {payload}")
    return {"status": "ok", "agent_id": AGENT_ID, "result": "Processing..."}

@app.get("/info")
async def info():
    return {"agent_id": AGENT_ID, "port": PORT, "running": True}

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

if __name__ == "__main__":
    logger.info(f"Starting {AGENT_ID} on port {PORT}")
    try:
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)
"""

README_MD = """# Agent: {name}

**Agent ID:** `{agent_id}`
**Port:** `{port}`
**Category:** `{category}`
**Description:** {description}

## Quick Start

```bash
pip install -r requirements.txt
cp .env.template .env
bash bin/start.sh
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/status` | Agent status |
| POST | `/invoke` | Main invoke endpoint |

## Testing

```bash
curl -s http://127.0.0.1:{port}/health | jq .
```

## Logging

```bash
tail -f logs/app.log
```

---

**Auto-generated:** {date}
"""

REQUIREMENTS_TXT = """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
aiohttp==3.9.1
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
"""

ENV_TEMPLATE = """AGENT_ID={agent_id}
PORT={port}
TOKEN=${{DASHBOARD_ADMIN_TOKEN}}
LOG_LEVEL=INFO
DASHBOARD_URL=http://127.0.0.1:12349
ARCHIVATOR_URL=http://127.0.0.1:12345
"""

AGENT_CONF = """[agent]
id={agent_id}
name={name}
port={port}
description={description}
category={category}

[security]
require_token=true
token_source=env

[logging]
level=INFO
file=logs/app.log

[integrations]
dashboard_url=http://127.0.0.1:12349
archivator_url=http://127.0.0.1:12345
"""

START_SCRIPT = """#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$AGENT_DIR")")"

if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

if [ -f "$AGENT_DIR/.env" ]; then
    set -a
    source "$AGENT_DIR/.env"
    set +a
fi

AGENT_ID="${{AGENT_ID:={agent_id}}}"
PORT="${{PORT:={port}}}"
LOG_LEVEL="${{LOG_LEVEL:-INFO}}"

echo "🚀 Starting ${{AGENT_ID}} on port ${{PORT}}..."
cd "$AGENT_DIR"
exec python main.py
"""

TEST_AGENT = """\"\"\"Basis-Tests für Agent\"\"\"

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app, AGENT_ID, PORT

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["port"] == PORT

def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200

def test_invoke(client):
    response = client.post("/invoke", json={"test": True})
    assert response.status_code == 200
"""


def create_agent(number, name, agent_id, port, description, category):
    """Erstelle einen Agent"""
    agent_dir = PROJECT_ROOT / f"{number}.{name}"

    print(f"✏️  Erstelle Agent {number}: {name} (Port: {port})")

    # Verzeichnisse
    agent_dir.mkdir(exist_ok=True)
    (agent_dir / "bin").mkdir(exist_ok=True)
    (agent_dir / "config").mkdir(exist_ok=True)
    (agent_dir / "tests").mkdir(exist_ok=True)
    (agent_dir / "logs").mkdir(exist_ok=True)
    (agent_dir / "docs").mkdir(exist_ok=True)
    (agent_dir / "data").mkdir(exist_ok=True)
    (agent_dir / "api").mkdir(exist_ok=True)

    # main.py
    (agent_dir / "main.py").write_text(MAIN_PY)
    (agent_dir / "main.py").chmod(0o755)

    # README.md
    readme = README_MD.format(
        name=name,
        agent_id=agent_id,
        port=port,
        category=category,
        description=description,
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    (agent_dir / "README.md").write_text(readme)

    # requirements.txt
    (agent_dir / "requirements.txt").write_text(REQUIREMENTS_TXT)

    # .env.template
    env_tpl = ENV_TEMPLATE.format(agent_id=agent_id, port=port)
    (agent_dir / ".env.template").write_text(env_tpl)

    # config/agent.conf
    conf = AGENT_CONF.format(agent_id=agent_id, name=name, port=port, description=description, category=category)
    (agent_dir / "config" / "agent.conf").write_text(conf)

    # bin/start.sh
    start = START_SCRIPT.format(agent_id=agent_id, port=port)
    start_file = agent_dir / "bin" / "start.sh"
    start_file.write_text(start)
    start_file.chmod(0o755)

    # tests/test_agent.py
    (agent_dir / "tests" / "test_agent.py").write_text(TEST_AGENT)

    # tests/__init__.py
    (agent_dir / "tests" / "__init__.py").touch()

    # logs/.gitkeep
    (agent_dir / "logs" / ".gitkeep").touch()

    # data/.gitkeep
    (agent_dir / "data" / ".gitkeep").touch()

    # api/__init__.py
    (agent_dir / "api" / "__init__.py").touch()

    print(f"✅ Agent {number}: {name} erstellt")
    return True


def main():
    print("\n" + "=" * 60)
    print("Erstelle alle 19 Agent-Verzeichnisse")
    print("=" * 60 + "\n")

    created = 0
    failed = 0

    for number, name, agent_id, port, description, category in AGENTS:
        try:
            if create_agent(number, name, agent_id, port, description, category):
                created += 1
        except Exception as e:
            print(f"❌ Fehler bei {name}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("✅ Erstellung abgeschlossen!")
    print(f"✅ Erstellt: {created} Agenten")
    if failed > 0:
        print(f"❌ Fehler: {failed} Agenten")
    print("=" * 60 + "\n")

    # Verifizierung
    print("📋 Verifiziere Struktur...\n")
    for number, name, agent_id, port, description, category in AGENTS:
        agent_dir = PROJECT_ROOT / f"{number}.{name}"
        if agent_dir.exists():
            files = ["main.py", "README.md", "requirements.txt", ".env.template"]
            if all((agent_dir / f).exists() for f in files):
                print(f"✅ {number}.{name} vollständig")
            else:
                print(f"⚠️  {number}.{name} unvollständig")

    print("\n" + "=" * 60)
    print("🚀 Nächste Schritte:")
    print("   1. cd " + str(PROJECT_ROOT))
    print("   2. git add .")
    print('   3. git commit -m "feat: add 19 standardized agent directories"')
    print("   4. git push origin main")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
