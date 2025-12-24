#!/usr/bin/env python3.12
"""
OPENA Agent Generator
Erstellt neue OPENA-Agents basierend auf dem funktionierenden Template

Usage:
    python3.12 create_agent.py --agent-id 1 --name "Portier" --port 12344
"""

import argparse
import shutil
import sys
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "agent_templates" / "opena_fastapi_base"
PROJECT_ROOT = Path(__file__).parent


def create_agent(agent_id: int, agent_name: str, port: int, api_key: str = None):
    """Erstelle neuen Agent aus Template"""

    # Agent-Ordner-Name
    agent_folder = f"{agent_id:02d}.opena{agent_id}_{agent_name.lower().replace(' ', '_')}"
    agent_path = PROJECT_ROOT / agent_folder

    print(f"🚀 Erstelle Agent: {agent_folder}")
    print(f"   Port: {port}")
    print(f"   Template: {TEMPLATE_DIR}")

    # 1. Prüfe ob Template existiert
    if not TEMPLATE_DIR.exists():
        print(f"❌ Template nicht gefunden: {TEMPLATE_DIR}")
        return False

    # 2. Erstelle Agent-Ordner
    if agent_path.exists():
        print(f"⚠️  Agent-Ordner existiert bereits: {agent_path}")
        response = input("   Überschreiben? [y/N]: ")
        if response.lower() != "y":
            print("   Abgebrochen.")
            return False
        shutil.rmtree(agent_path)

    agent_path.mkdir(parents=True)
    print(f"✅ Ordner erstellt: {agent_path}")

    # 3. Kopiere Template-Dateien
    for file in ["agent_start.py", "media_handler.py", "metrics.py", "README.md"]:
        src = TEMPLATE_DIR / file
        if src.exists():
            if file in ["media_handler.py", "metrics.py"]:
                # Module in modules/ Unterordner
                modules_dir = agent_path / "modules"
                modules_dir.mkdir(exist_ok=True)
                dst = modules_dir / file
            else:
                dst = agent_path / file

            shutil.copy2(src, dst)
            print(f"   ✓ {file}")

    # 4. Erstelle .env
    env_content = f"""# OPENA{agent_id} {agent_name} Agent Configuration
OPENA{agent_id}_PORT={port}
"""

    if api_key:
        env_content += f'OPENAI_API_KEY_OPENA{agent_id}="{api_key}"\n'
    else:
        env_content += f'OPENAI_API_KEY_OPENA{agent_id}="<YOUR_API_KEY_HERE>"\n'

    (agent_path / ".env").write_text(env_content)
    print("   ✓ .env")

    # 5. Erstelle logs/ und media/ Verzeichnisse
    (agent_path / "logs").mkdir(exist_ok=True)
    (agent_path / "media").mkdir(exist_ok=True)
    print("   ✓ logs/ und media/")

    # 6. Passe agent_start.py an
    agent_start_path = agent_path / "agent_start.py"
    if agent_start_path.exists():
        content = agent_start_path.read_text()
        # Ersetze OPENA12 → OPENAX
        content = content.replace("OPENA12", f"OPENA{agent_id}")
        content = content.replace("opena12", f"opena{agent_id}")
        content = content.replace("12357", str(port))
        content = content.replace("Social Media", agent_name)
        agent_start_path.write_text(content)
        print("   ✓ agent_start.py angepasst")

    # 7. Erstelle minimales main.py Template
    main_py_content = f'''#!/usr/bin/env python3.12
"""
OPENA{agent_id} - {agent_name} Agent
PORTIER PAS-6.0 Standard

Port: {port}
API Key: OPENAI_API_KEY_OPENA{agent_id}
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv("OPENA{agent_id}_PORT", "{port}"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_OPENA{agent_id}", os.getenv("OPENAI_API_KEY", ""))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="OPENA{agent_id} {agent_name} Agent",
    version="1.0.0",
    description="{agent_name} Agent - PORTIER PAS-6.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Startup
START_TIME = time.time()

@app.on_event("startup")
async def startup():
    logger.info(f"🚀 OPENA{agent_id} {agent_name} Agent starting...")
    logger.info(f"   Port: {{PORT}}")
    logger.info(f"   API Key: {{'configured' if OPENAI_API_KEY else 'NOT SET'}}")

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - serve HTML dashboard"""
    html_path = os.path.join(os.path.dirname(__file__), "html")
    if os.path.exists(os.path.join(html_path, "index.html")):
        return FileResponse(os.path.join(html_path, "index.html"))
    else:
        return {{
            "service": "opena{agent_id}",
            "name": "{agent_name} Agent",
            "version": "1.0.0",
            "standard": "PAS-6.0",
            "port": PORT,
            "status": "operational"
        }}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "agent": "opena{agent_id}_{agent_name.lower().replace(' ', '_')}",
        "version": "1.0.0",
        "port": PORT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "openai_configured": bool(OPENAI_API_KEY),
        "timestamp": datetime.now().isoformat() + "Z"
    }}

@app.get("/status")
async def status():
    """Detailed status endpoint"""
    return {{
        "agent": "opena{agent_id}_{agent_name.lower().replace(' ', '_')}",
        "version": "1.0.0",
        "status": "operational",
        "uptime": {{
            "seconds": round(time.time() - START_TIME, 2),
            "started_at": datetime.fromtimestamp(START_TIME).isoformat()
        }}
    }}

# ============================================================================
# HTML MOUNTING
# ============================================================================

html_path = os.path.join(os.path.dirname(__file__), "html")
if os.path.exists(html_path):
    app.mount("/html", StaticFiles(directory=html_path), name="html")
    logger.info(f"✅ HTML directory mounted: {{html_path}}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
'''

    (agent_path / "main.py").write_text(main_py_content)
    print("   ✓ main.py erstellt")

    # 8. Zusammenfassung
    print("\n✅ Agent erfolgreich erstellt!")
    print(f"\n📁 Ordner: {agent_path}")
    print("🔧 Nächste Schritte:")
    print(f"   1. cd {agent_folder}")
    print("   2. Bearbeite .env und füge API Key hinzu")
    print("   3. Erstelle html/ Verzeichnis mit Dashboard")
    print("   4. python3.12 agent_start.py")
    print(f"   5. Browser: http://localhost:{port}/")

    return True


def main():
    parser = argparse.ArgumentParser(description="OPENA Agent Generator")
    parser.add_argument("--agent-id", type=int, required=True, help="Agent ID (1-21)")
    parser.add_argument("--name", type=str, required=True, help="Agent Name (z.B. 'Portier')")
    parser.add_argument("--port", type=int, required=True, help="Port (12344-12399)")
    parser.add_argument("--api-key", type=str, help="OpenAI API Key (optional)")

    args = parser.parse_args()

    # Validierung
    if not (1 <= args.agent_id <= 21):
        print("❌ Agent ID muss zwischen 1 und 21 liegen")
        sys.exit(1)

    if not (12344 <= args.port <= 12399):
        print("❌ Port muss zwischen 12344 und 12399 liegen")
        sys.exit(1)

    # Agent erstellen
    success = create_agent(agent_id=args.agent_id, agent_name=args.name, port=args.port, api_key=args.api_key)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
