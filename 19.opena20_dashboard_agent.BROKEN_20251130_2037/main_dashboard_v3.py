#!/usr/bin/env python3
"""
opena20 - Dashboard Agent v3.0
Port: 12349
Kürzel: dashp

Central Dashboard für ELION/Portier System mit professionellem UI
- Zentrale Übersicht aller Agenten
- Individuelle Agenten-Seiten (/agent/opena1 - /agent/opena20)
- API-Konsole
- Start/Stop/Health für alle Agenten
"""

import os
import time
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import aiohttp

# =============================================================================
# CONFIGURATION
# =============================================================================

PORT = 12349
AGENT_ID = "opena20"
KUERZEL = "dashp"
START_TIME = time.time()

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# =============================================================================
# AGENT REGISTRY (opena1 - opena20)
# =============================================================================

AGENT_REGISTRY: List[Dict[str, Any]] = [
    {"id": "opena1",  "name": "Koordinator",         "kuerzel": "kordp",       "port": 12344, "icon": "🎯"},
    {"id": "opena2",  "name": "Archivator",          "kuerzel": "archivp",     "port": 12345, "icon": "📦"},
    {"id": "opena3",  "name": "OpenWebUI Terminal",  "kuerzel": "owuip",       "port": 12347, "icon": "🖥️"},
    {"id": "opena4",  "name": "Telegram Agent",      "kuerzel": "telep",       "port": 12348, "icon": "📱"},
    {"id": "opena5",  "name": "VS Code Agent",       "kuerzel": "vscop",       "port": 12351, "icon": "💻"},
    {"id": "opena6",  "name": "Browser Agent",       "kuerzel": "browsep",     "port": 12352, "icon": "🌐"},
    {"id": "opena7",  "name": "Email Agent",         "kuerzel": "emailp",      "port": 12353, "icon": "📧"},
    {"id": "opena8",  "name": "WhatsApp Agent",      "kuerzel": "whatsappp",   "port": 12354, "icon": "💬"},
    {"id": "opena9",  "name": "Telefonie Agent",     "kuerzel": "telephonep",  "port": 12355, "icon": "📞"},
    {"id": "opena10", "name": "Call Tracking",       "kuerzel": "calltrackp",  "port": 12356, "icon": "📊"},
    {"id": "opena11", "name": "Unlock Agent",        "kuerzel": "unlockp",     "port": 12357, "icon": "🔓"},
    {"id": "opena12", "name": "Social Media Agent",  "kuerzel": "smp",         "port": 12358, "icon": "📣"},
    {"id": "opena13", "name": "Influencer Agent",    "kuerzel": "influp",      "port": 12359, "icon": "⭐"},
    {"id": "opena14", "name": "Calendar Agent",      "kuerzel": "calp",        "port": 12360, "icon": "📅"},
    {"id": "opena15", "name": "HTML Creator",        "kuerzel": "htmlp",       "port": 12361, "icon": "🎨"},
    {"id": "opena16", "name": "Shop Agent",          "kuerzel": "shopp",       "port": 12362, "icon": "🛒"},
    {"id": "opena17", "name": "Homepage Creator",    "kuerzel": "hpcreatep",   "port": 12363, "icon": "🏠"},
    {"id": "opena18", "name": "CRM Agent",           "kuerzel": "crmp",        "port": 12364, "icon": "👥"},
    {"id": "opena19", "name": "Stocks & Crypto",     "kuerzel": "stockcryptop","port": 12365, "icon": "📈"},
    {"id": "opena20", "name": "Dashboard",           "kuerzel": "dashp",       "port": 12349, "icon": "🚀"},
]


# =============================================================================
# FASTAPI APP
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 ELION Dashboard v3.0 starting on port {PORT}")
    yield
    logger.info("👋 ELION Dashboard shutting down")


app = FastAPI(
    title="ELION Dashboard v3.0",
    description="Zentrale Übersicht aller Agenten",
    version="3.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def check_agent_health(agent: Dict[str, Any]) -> Dict[str, Any]:
    """Check health of single agent"""
    try:
        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"http://127.0.0.1:{agent['port']}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {**agent, "online": True, "data": data, "uptime": data.get("uptime_seconds", 0)}
    except Exception as e:
        logger.debug(f"Agent {agent['id']} offline: {e}")
    return {**agent, "online": False, "data": None, "uptime": 0}


async def get_all_agents_status() -> List[Dict[str, Any]]:
    """Get status of all agents"""
    import asyncio
    tasks = [check_agent_health(agent) for agent in AGENT_REGISTRY]
    return await asyncio.gather(*tasks)


# =============================================================================
# API ROUTES
# =============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": AGENT_ID,
        "kuerzel": KUERZEL,
        "port": PORT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "3.0.0"
    }


@app.get("/api/agents")
async def get_agents():
    """Get all agents with status"""
    agents = await get_all_agents_status()
    online = sum(1 for a in agents if a["online"])
    return {
        "agents": agents,
        "total": len(agents),
        "online": online,
        "offline": len(agents) - online
    }


@app.get("/api/agent/{agent_id}")
async def get_agent(agent_id: str):
    """Get single agent status"""
    agent = next((a for a in AGENT_REGISTRY if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return await check_agent_health(agent)


@app.post("/api/agent/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent (placeholder)"""
    agent = next((a for a in AGENT_REGISTRY if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    logger.info(f"Start requested for {agent_id}")
    return {"status": "start_requested", "agent": agent_id}


@app.post("/api/agent/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop an agent (placeholder)"""
    agent = next((a for a in AGENT_REGISTRY if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    logger.info(f"Stop requested for {agent_id}")
    return {"status": "stop_requested", "agent": agent_id}


@app.post("/api/agents/start-all")
async def start_all_agents():
    """Start all agents (placeholder)"""
    logger.info("Start all agents requested")
    return {"status": "start_all_requested", "agents": len(AGENT_REGISTRY)}


@app.post("/api/agents/stop-all")
async def stop_all_agents():
    """Stop all agents (placeholder)"""
    logger.info("Stop all agents requested")
    return {"status": "stop_all_requested", "agents": len(AGENT_REGISTRY)}


# =============================================================================
# HTML ROUTES
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/agent/{agent_id}", response_class=HTMLResponse)
async def agent_detail(request: Request, agent_id: str):
    """Individual agent detail page"""
    agent = next((a for a in AGENT_REGISTRY if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return templates.TemplateResponse(
        "agent_detail.html",
        {
            "request": request,
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "agent": agent
        }
    )


# Redirect routes for /opena1 - /opena20
for agent in AGENT_REGISTRY:
    exec(f"""
@app.get("/{agent['id']}", response_class=HTMLResponse)
async def redirect_{agent['id']}(request: Request):
    return templates.TemplateResponse("agent_detail.html", {{"request": request, "agent_id": "{agent['id']}", "agent_name": "{agent['name']}", "agent": {agent}}})
""")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main_dashboard_v3:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info"
    )
