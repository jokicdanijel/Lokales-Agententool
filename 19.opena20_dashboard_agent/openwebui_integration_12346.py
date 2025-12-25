#!/usr/bin/env python3
"""
OpenWebUI Integration Server - Port 12346
HYPER-DASHBOARD 3.0 PORTIER Enterprise

Integriert OpenWebUI direkt in das PORTIER 3.0 System:
- opena3 (12347) Terminal Agent Bridge
- HYPER-DASHBOARD (12349) Status Integration
- Option-2-Flow Compliance
"""

import logging
import time
from datetime import UTC, datetime
from typing import Any

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuration - PORTIER 3.0 Ports (Updated for kordp conflict)
OPENWEBUI_INTEGRATION_PORT = 12350  # This service (moved from 12346 - kordp conflict)
OPENA3_TERMINAL_PORT = 12347  # opena3 terminal agent
DASHBOARD_PORT = 12349  # HYPER-DASHBOARD 3.0
KORDP_PORT = 12346  # kordp gateway (already running)
OPENWEBUI_UI_PORT = 8080  # OpenWebUI UI (external, UI-only)

# URLs
OPENA3_URL = f"http://127.0.0.1:{OPENA3_TERMINAL_PORT}"
DASHBOARD_URL = f"http://127.0.0.1:{DASHBOARD_PORT}"
OPENWEBUI_UI_URL = f"http://127.0.0.1:{OPENWEBUI_UI_PORT}"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openwebui_integration")

# FastAPI App
app = FastAPI(
    title="OpenWebUI Integration Server",
    description="HYPER-DASHBOARD 3.0 OpenWebUI Integration - Port 12346",
    version="3.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000


class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    response_time_ms: float


class AgentStatus(BaseModel):
    agent_id: str
    status: str
    port: int
    last_check: str


# Global HTTP Session
http_session: aiohttp.ClientSession | None = None


@app.on_event("startup")
async def startup_event():
    """Initialize HTTP session"""
    global http_session
    http_session = aiohttp.ClientSession()
    logger.info("🚀 OpenWebUI Integration Server started on port 12346")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup HTTP session"""
    global http_session
    if http_session:
        await http_session.close()
    logger.info("🛑 OpenWebUI Integration Server stopped")


@app.get("/health")
async def health():
    """Health check for OpenWebUI Integration"""
    return {
        "status": "ok",
        "service": "openwebui_integration",
        "port": OPENWEBUI_INTEGRATION_PORT,
        "version": "3.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "connections": {
            "opena3_terminal": OPENA3_URL,
            "hyper_dashboard": DASHBOARD_URL,
            "openwebui_ui": OPENWEBUI_UI_URL,
        },
    }


@app.get("/api/status/agents")
async def get_agents_status():
    """Get status of all PORTIER agents via HYPER-DASHBOARD"""
    try:
        async with http_session.get(f"{DASHBOARD_URL}/api/status/all") as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "ok",
                    "agents": data.get("agents", {}),
                    "total_agents": len(data.get("agents", {})),
                    "source": "hyper_dashboard_3.0",
                }
            else:
                raise HTTPException(500, "HYPER-DASHBOARD nicht erreichbar")
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(500, f"Fehler beim Abrufen des Agent-Status: {e!s}")


@app.get("/api/status/opena3")
async def get_opena3_status():
    """Get opena3 terminal agent status"""
    try:
        async with http_session.get(f"{OPENA3_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "online",
                    "agent": "opena3",
                    "port": OPENA3_TERMINAL_PORT,
                    "health": data,
                    "last_check": datetime.now(UTC).isoformat(),
                }
            else:
                return {
                    "status": "offline",
                    "agent": "opena3",
                    "port": OPENA3_TERMINAL_PORT,
                    "error": f"HTTP {response.status}",
                }
    except Exception as e:
        logger.error(f"Error checking opena3 status: {e}")
        return {"status": "error", "agent": "opena3", "port": OPENA3_TERMINAL_PORT, "error": str(e)}


@app.get("/api/status/dashboard")
async def get_dashboard_status():
    """Get HYPER-DASHBOARD 3.0 status"""
    try:
        async with http_session.get(f"{DASHBOARD_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "online",
                    "service": "hyper_dashboard_3.0",
                    "port": DASHBOARD_PORT,
                    "health": data,
                    "last_check": datetime.now(UTC).isoformat(),
                }
            else:
                return {
                    "status": "offline",
                    "service": "hyper_dashboard_3.0",
                    "port": DASHBOARD_PORT,
                    "error": f"HTTP {response.status}",
                }
    except Exception as e:
        logger.error(f"Error checking dashboard status: {e}")
        return {"status": "error", "service": "hyper_dashboard_3.0", "port": DASHBOARD_PORT, "error": str(e)}


@app.post("/api/chat")
async def chat_with_opena3(request: ChatRequest):
    """Send chat message to opena3 terminal agent"""
    try:
        start_time = time.time()

        # Prepare request for opena3
        opena3_request = {
            "command": "chat",
            "params": {
                "message": request.message,
                "model": request.model,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
        }

        # Send to opena3 terminal
        async with http_session.post(
            f"{OPENA3_URL}/command", json=opena3_request, headers={"Content-Type": "application/json"}
        ) as response:
            response_time_ms = (time.time() - start_time) * 1000

            if response.status == 200:
                data = await response.json()

                return ChatResponse(
                    response=data.get("result", "Keine Antwort erhalten"),
                    model=request.model,
                    tokens_used=data.get("tokens_used", 0),
                    response_time_ms=response_time_ms,
                )
            else:
                error_text = await response.text()
                raise HTTPException(500, f"opena3 Fehler: {error_text}")

    except Exception as e:
        logger.error(f"Error in chat with opena3: {e}")
        raise HTTPException(500, f"Chat-Fehler: {e!s}")


@app.post("/api/workflow/execute")
async def execute_workflow(request: dict[str, Any]):
    """Execute workflow via HYPER-DASHBOARD"""
    try:
        # Forward to HYPER-DASHBOARD workflow engine
        async with http_session.post(
            f"{DASHBOARD_URL}/api/workflows/execute", json=request, headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "success",
                    "workflow_id": data.get("workflow_id"),
                    "result": data,
                    "executed_via": "hyper_dashboard_3.0",
                }
            else:
                error_text = await response.text()
                raise HTTPException(500, f"Workflow-Fehler: {error_text}")

    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(500, f"Workflow-Ausführung fehlgeschlagen: {e!s}")


@app.get("/api/openwebui/models")
async def get_openwebui_models():
    """Get available models from OpenWebUI"""
    try:
        async with http_session.get(f"{OPENWEBUI_UI_URL}/api/models") as response:
            if response.status == 200:
                data = await response.json()
                return {"status": "success", "models": data, "source": "openwebui_ui"}
            else:
                return {
                    "status": "error",
                    "error": f"OpenWebUI UI nicht erreichbar (HTTP {response.status})",
                    "note": "Port 8080 ist nur für UI erlaubt, Backend-Calls über opena3",
                }
    except Exception as e:
        logger.error(f"Error getting OpenWebUI models: {e}")
        return {"status": "error", "error": str(e), "note": "Verwende opena3 (Port 12347) für Backend-Operationen"}


@app.get("/api/system/integration-test")
async def integration_test():
    """Test all system integrations"""
    results = {}

    # Test opena3
    try:
        async with http_session.get(f"{OPENA3_URL}/health") as response:
            results["opena3"] = {
                "status": "ok" if response.status == 200 else "error",
                "port": OPENA3_TERMINAL_PORT,
                "response_code": response.status,
            }
    except Exception as e:
        results["opena3"] = {"status": "error", "port": OPENA3_TERMINAL_PORT, "error": str(e)}

    # Test HYPER-DASHBOARD
    try:
        async with http_session.get(f"{DASHBOARD_URL}/health") as response:
            results["hyper_dashboard"] = {
                "status": "ok" if response.status == 200 else "error",
                "port": DASHBOARD_PORT,
                "response_code": response.status,
            }
    except Exception as e:
        results["hyper_dashboard"] = {"status": "error", "port": DASHBOARD_PORT, "error": str(e)}

    # Test OpenWebUI UI (optional)
    try:
        async with http_session.get(f"{OPENWEBUI_UI_URL}/health") as response:
            results["openwebui_ui"] = {
                "status": "ok" if response.status == 200 else "warning",
                "port": OPENWEBUI_UI_PORT,
                "response_code": response.status,
                "note": "UI-only, Backend via opena3",
            }
    except Exception as e:
        results["openwebui_ui"] = {
            "status": "warning",
            "port": OPENWEBUI_UI_PORT,
            "error": str(e),
            "note": "Optional UI component",
        }

    # Summary
    all_ok = all(r.get("status") == "ok" for r in results.values() if r.get("status") != "warning")

    return {
        "integration_test": "complete",
        "overall_status": "ok" if all_ok else "partial",
        "timestamp": datetime.now(UTC).isoformat(),
        "results": results,
        "portier_compliance": "✅ Option-2-Flow ready",
    }


if __name__ == "__main__":
    logger.info("🚀 Starting OpenWebUI Integration Server...")
    logger.info(f"📡 Port: {OPENWEBUI_INTEGRATION_PORT}")
    logger.info(f"🔗 opena3 Terminal: {OPENA3_URL}")
    logger.info(f"🎯 HYPER-DASHBOARD: {DASHBOARD_URL}")
    logger.info(f"🌐 OpenWebUI UI: {OPENWEBUI_UI_URL}")

    uvicorn.run(app, host="127.0.0.1", port=OPENWEBUI_INTEGRATION_PORT, log_level="info")
