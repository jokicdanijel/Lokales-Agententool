#!/usr/bin/env bash

# Agent-Definitionen: name|port|description
AGENTS=(
  "opena1_coordinator|12344|Orchestrator for Phase 1 services"
  "opena2_archivator|12345|File-based storage and archiving system"
  "kordp_scheduler|12346|Event coordination and scheduling"
  "opena4_telegram|12347|Telegram integration and messaging"
  "opena5_browser|12348|Web browser automation"
  "opena6_email|12349|Email client and management"
  "opena7_whatsapp|12350|WhatsApp integration"
  "opena8_telephone|12351|Telephone system integration"
  "opena9_call_tracking|12352|Call analytics and tracking"
  "opena10_unlock|12353|Security and access control"
  "opena11_social_media|12359|Social media management"
  "opena12_influencer|12360|Influencer collaboration tools"
  "opena13_calendar|12361|Calendar and scheduling"
  "opena14_html|12362|HTML content generation"
  "opena15_shop|12363|E-commerce and shop"
  "opena16_crm|12364|Customer relationship management"
  "opena17_analytics|12365|Data analytics and reporting"
  "opena18_dashboard|12366|Dashboard and visualization"
  "opena19_workflow|12367|Workflow automation"
)

for agent in "${AGENTS[@]}"; do
  IFS='|' read -r name port desc <<< "$agent"

  # Create directory structure
  mkdir -p "$name"/{bin,config,tests,logs,docs,data,api,cache}

  # Create README
  cat > "$name/README.md" << AGENT_README
# $name

**Port:** $port
**Description:** $desc

## Quick Start

\`\`\`bash
cd $name
python main.py
\`\`\`

## Structure

- \`bin/\` – Scripts and utilities
- \`config/\` – Configuration files
- \`tests/\` – Unit and integration tests
- \`logs/\` – Runtime logs
- \`docs/\` – Documentation
- \`data/\` – Static data and resources
- \`api/\` – API endpoints
- \`cache/\` – Cached data

## Configuration

Create \`.env\` in this directory:

\`\`\`env
PORT=$port
TOKEN=\${DASHBOARD_ADMIN_TOKEN}
LOG_LEVEL=INFO
\`\`\`

## Health Check

\`\`\`bash
curl http://127.0.0.1:$port/health
\`\`\`

## Integration

Register with dashboard:

\`\`\`bash
curl -X POST http://127.0.0.1:12349/api/agent/register \\
  -H "Authorization: Bearer \$TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"agent_id":"$name","endpoint":"http://127.0.0.1:$port"}'
\`\`\`
AGENT_README

  # Create main.py template
  cat > "$name/main.py" << 'AGENT_MAIN'
#!/usr/bin/env python3
"""
Agent main entry point
"""
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

PORT = int(os.getenv("PORT", "12344"))
TOKEN = os.getenv("TOKEN", "")

@app.get("/health")
async def health():
    return {"status": "ok", "port": PORT}

@app.post("/invoke")
async def invoke(payload: dict):
    """Main agent endpoint"""
    logger.info(f"Invoke: {payload}")
    return {"result": "ok", "payload": payload}

if __name__ == "__main__":
    logger.info(f"Starting agent on port {PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
AGENT_MAIN

  # Create config.py
  cat > "$name/config/agent.conf" << 'AGENT_CONF'
[agent]
name = $name
port = $port
debug = false
log_level = INFO

[security]
require_token = true
token_header = Authorization

[integrations]
dashboard_url = http://127.0.0.1:12349
archivator_url = http://127.0.0.1:12345
AGENT_CONF

  # Create .env template
  cat > "$name/.env.template" << 'AGENT_ENV'
PORT=$port
TOKEN=${DASHBOARD_ADMIN_TOKEN}
LOG_LEVEL=INFO
AGENT_ENV

  # Create empty files
  touch "$name/logs/.gitkeep"
  touch "$name/data/.gitkeep"
  touch "$name/cache/.gitkeep"
  touch "$name/tests/__init__.py"
  touch "$name/api/__init__.py"

  echo "✅ Created $name (port $port)"
done

echo "✅ All agent directories created!"
