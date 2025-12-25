"""
Agent Server - Mini-Orchestrator Entry Point
FastAPI-Service der sich beim Dashboard registriert und interne Agents verwaltet.

Port: 12350 (oder konfigurierbar)
Agent-ID: opena_mini_orchestrator
"""

import asyncio
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from monitoring import ServiceMetrics, get_metrics_endpoint
from pydantic import BaseModel, Field

from agents.agent_api import AgentAPIClient
from agents.agent_base import AgentCapability

# Interne Module
from agents.agent_manager import AgentManager
from agents.memory_system import MemorySystem

# Logging Setup
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "agent_server.log"), logging.StreamHandler()],
)
logger = logging.getLogger("agent_server")

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
AGENT_SERVER_PORT = int(os.getenv("AGENT_SERVER_PORT", "12350"))
AGENT_ID = os.getenv("AGENT_ID", "opena_mini_orchestrator")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------
app = FastAPI(
    title="Agent Server - Mini Orchestrator",
    description="Internal agent management system integrated with ELION Dashboard",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Core Components
# -------------------------------------------------------------------
memory_system = MemorySystem(persist_to_disk=True)
agent_manager = AgentManager(memory_system=memory_system)
dashboard_api = AgentAPIClient(dashboard_url=DASHBOARD_URL, agent_id=AGENT_ID, bearer_token=BEARER_TOKEN)
metrics = ServiceMetrics("mini_orchestrator")

# Background Tasks
heartbeat_task: asyncio.Task | None = None

# -------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------


class CommandRequest(BaseModel):
    """Command-Request an einen internen Agent"""

    command: str = Field(..., description="Command name (e.g., 'send_email')")
    params: dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    agent_id: str | None = Field(None, description="Target agent ID (optional, auto-route if None)")
    capability: str | None = Field(None, description="Required capability for auto-routing")


class CommandResponse(BaseModel):
    """Command-Response"""

    status: str = Field(..., description="'success' or 'error'")
    data: Any | None = Field(None, description="Result data")
    error: str | None = Field(None, description="Error message if failed")
    agent_id: str | None = Field(None, description="Agent that executed the command")


class HealthResponse(BaseModel):
    """Health-Check Response"""

    status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    timestamp: str
    details: dict[str, Any] = Field(default_factory=dict)


# -------------------------------------------------------------------
# Startup / Shutdown
# -------------------------------------------------------------------


@app.on_event("startup")
async def startup_event():
    """Startup: Registriere beim Dashboard, starte Agents, Heartbeat"""
    global heartbeat_task

    logger.info(f"Agent Server starting on port {AGENT_SERVER_PORT}...")

    # Metrics: Set healthy
    metrics.set_health(True)

    # 1. Memory System laden
    loaded_entries = await memory_system.load_from_disk()
    logger.info(f"Loaded {loaded_entries} memory entries")

    # 2. Interne Agents registrieren (hier später deine implementations/)
    # Beispiel: await agent_manager.register_agent(MailAgent(...))
    logger.info("Internal agents: (none registered yet, add in implementations/)")

    # 3. Beim Dashboard registrieren
    capabilities = _get_all_capabilities()
    registration_result = await dashboard_api.register_agent(
        port=AGENT_SERVER_PORT,
        capabilities=capabilities,
        metadata={"version": "1.0.0", "python_version": "3.13", "agent_count": len(agent_manager.agents)},
    )

    if registration_result.get("status") == "error":
        logger.error(f"Dashboard registration failed: {registration_result.get('error')}")
    else:
        logger.info(f"Registered at Dashboard: {DASHBOARD_URL}")

    # 4. Heartbeat-Loop starten
    heartbeat_task = asyncio.create_task(dashboard_api.heartbeat_loop(interval_seconds=30))
    logger.info("Heartbeat task started")

    logger.info("Agent Server ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown: Agents herunterfahren, Dashboard benachrichtigen"""
    global heartbeat_task

    logger.info("Agent Server shutting down...")

    # 1. Heartbeat stoppen
    if heartbeat_task:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

    # 2. Status update: offline
    await dashboard_api.update_status("offline")

    # 3. Alle Agents herunterfahren
    await agent_manager.shutdown_all()

    # 4. API-Client schließen
    await dashboard_api.close()

    logger.info("Agent Server stopped")


# -------------------------------------------------------------------
# API Routes
# -------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health-Check des gesamten Mini-Orchestrators.
    """
    health_data = await agent_manager.health_check_all()

    return HealthResponse(status=health_data["overall"], timestamp=datetime.now(UTC).isoformat(), details=health_data)


@app.post("/command", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """
    Führt einen Command auf einem internen Agent aus.

    Routing:
    - Wenn agent_id gegeben → an diesen Agent
    - Wenn capability gegeben → an ersten passenden Agent
    - Sonst → Fehler
    """
    capability = None
    if request.capability:
        try:
            capability = AgentCapability(request.capability)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid capability: {request.capability}")

    result = await agent_manager.execute_command(
        command=request.command, params=request.params, agent_id=request.agent_id, capability=capability
    )

    # SSE-Event ans Dashboard publishen
    await dashboard_api.publish_sse_event(
        event_type="command_executed",
        data={"command": request.command, "result_status": result["status"], "agent_id": result.get("agent_id")},
    )

    return CommandResponse(**result)


@app.get("/agents", response_model=list[dict[str, Any]])
async def list_agents():
    """
    Listet alle internen Agents auf.
    """
    return await agent_manager.get_all_status()


@app.get("/stats")
async def get_stats():
    """
    Statistiken über AgentManager + Memory.
    """
    agent_stats = agent_manager.get_stats()
    memory_stats = await memory_system.get_stats()

    # Metrics aktualisieren
    by_status = agent_stats.get("by_status", {})
    metrics.update_agent_stats(
        ready=by_status.get("ready", 0),
        busy=by_status.get("busy", 0),
        error=by_status.get("error", 0),
        offline=by_status.get("offline", 0),
    )

    return {
        "agent_manager": agent_stats,
        "memory_system": memory_stats,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus Metrics Endpoint
    """
    return get_metrics_endpoint()


@app.get("/")
async def root():
    """Root-Endpoint mit Info"""
    return {
        "service": "Agent Server - Mini Orchestrator",
        "agent_id": AGENT_ID,
        "port": AGENT_SERVER_PORT,
        "dashboard": DASHBOARD_URL,
        "status": "online",
        "endpoints": {"health": "/health", "command": "POST /command", "agents": "/agents", "stats": "/stats"},
    }


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def _get_all_capabilities() -> list[str]:
    """
    Sammelt alle Capabilities der registrierten Agents.
    """
    capabilities = set()
    for agent in agent_manager.agents.values():
        for cap in agent.capabilities:
            capabilities.add(cap.value)

    return list(capabilities)


# -------------------------------------------------------------------
# Main Entry Point
# -------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agent_server:app",
        host="0.0.0.0",
        port=AGENT_SERVER_PORT,
        log_level="info",
        reload=False,  # Kein reload im Production-Mode
    )
