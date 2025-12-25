#!/usr/bin/env python3
"""
OpenWebUI Integration Server - Port 12347
HYPER-DASHBOARD 3.0 PORTIER Enterprise (Optimized)

Korrekte Port-Zuordnung:
- Port 12347: OpenWebUI Integration (this service)
- Port 12346: kordp Gateway (already running)
- Port 12349: HYPER-DASHBOARD 3.0
- Port 8080: OpenWebUI UI (external, UI-only)
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuration - PORTIER 3.0 Optimized
OPENWEBUI_INTEGRATION_PORT = 12347  # This service
KORDP_GATEWAY_PORT = 12346  # kordp gateway (running)
DASHBOARD_PORT = 12349  # HYPER-DASHBOARD 3.0
OPENWEBUI_UI_PORT = 8080  # OpenWebUI UI (external)

# URLs
KORDP_URL = f"http://127.0.0.1:{KORDP_GATEWAY_PORT}"
DASHBOARD_URL = f"http://127.0.0.1:{DASHBOARD_PORT}"
OPENWEBUI_UI_URL = f"http://127.0.0.1:{OPENWEBUI_UI_PORT}"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openwebui_integration")

# Global HTTP Session
http_session: aiohttp.ClientSession | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global http_session

    # Startup
    http_session = aiohttp.ClientSession()
    logger.info("🚀 OpenWebUI Integration Server started on port 12347")

    yield

    # Shutdown
    if http_session:
        await http_session.close()
    logger.info("🛑 OpenWebUI Integration Server stopped")


# FastAPI App with lifespan
app = FastAPI(
    title="OpenWebUI Integration Server",
    description="HYPER-DASHBOARD 3.0 OpenWebUI Integration - Port 12347",
    version="3.0.0",
    lifespan=lifespan,
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


class WorkflowRequest(BaseModel):
    workflow_name: str
    parameters: dict[str, Any] = {}


# Routes
@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check for OpenWebUI Integration"""
    return {
        "status": "ok",
        "service": "openwebui_integration",
        "port": OPENWEBUI_INTEGRATION_PORT,
        "version": "3.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "connections": {"kordp_gateway": KORDP_URL, "hyper_dashboard": DASHBOARD_URL, "openwebui_ui": OPENWEBUI_UI_URL},
    }


@app.get("/api/status/system")
async def get_system_status() -> dict[str, Any]:
    """Get complete system status via HYPER-DASHBOARD"""
    if not http_session:
        raise HTTPException(500, "HTTP session not initialized")

    try:
        async with http_session.get(f"{DASHBOARD_URL}/api/status/all") as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "ok",
                    "system": data,
                    "source": "hyper_dashboard_3.0",
                    "integration_port": OPENWEBUI_INTEGRATION_PORT,
                }
            else:
                raise HTTPException(500, f"HYPER-DASHBOARD nicht erreichbar: HTTP {response.status}")
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(500, f"System-Status Fehler: {e!s}")


@app.get("/api/status/kordp")
async def get_kordp_status() -> dict[str, Any]:
    """Get kordp gateway status"""
    if not http_session:
        raise HTTPException(500, "HTTP session not initialized")

    try:
        async with http_session.get(f"{KORDP_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "online",
                    "service": "kordp_gateway",
                    "port": KORDP_GATEWAY_PORT,
                    "health": data,
                    "last_check": datetime.now(UTC).isoformat(),
                }
            else:
                return {
                    "status": "offline",
                    "service": "kordp_gateway",
                    "port": KORDP_GATEWAY_PORT,
                    "error": f"HTTP {response.status}",
                }
    except Exception as e:
        logger.error(f"Error checking kordp status: {e}")
        return {"status": "error", "service": "kordp_gateway", "port": KORDP_GATEWAY_PORT, "error": str(e)}


@app.get("/api/status/dashboard")
async def get_dashboard_status() -> dict[str, Any]:
    """Get HYPER-DASHBOARD 3.0 status"""
    if not http_session:
        raise HTTPException(500, "HTTP session not initialized")

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
async def chat_with_openwebui(request: ChatRequest) -> ChatResponse:
    """Send chat message via kordp to OpenWebUI terminal"""
    if not http_session:
        raise HTTPException(500, "HTTP session not initialized")

    try:
        start_time = time.time()

        # Prepare kordp dispatch request (Option-2-Flow compliant)
        kordp_request = {
            "service_target": "openwebui3",
            "action": "chat",
            "params": {
                "prompt": request.message,
                "model": request.model,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
        }

        # Send via kordp (Option-2-Flow)
        async with http_session.post(
            f"{KORDP_URL}/dispatch/kordp", json=kordp_request, headers={"Content-Type": "application/json"}
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
                raise HTTPException(500, f"kordp Dispatch Fehler: {error_text}")

    except Exception as e:
        logger.error(f"Error in chat with OpenWebUI: {e}")
        raise HTTPException(500, f"Chat-Fehler: {e!s}")


@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest) -> dict[str, Any]:
    """Execute workflow via HYPER-DASHBOARD"""
    if not http_session:
        raise HTTPException(500, "HTTP session not initialized")

    try:
        # Forward to HYPER-DASHBOARD workflow engine
        workflow_request = {
            "workflow_name": request.workflow_name,
            "parameters": request.parameters,
            "source": "openwebui_integration",
        }

        async with http_session.post(
            f"{DASHBOARD_URL}/api/workflows/execute",
            json=workflow_request,
            headers={"Content-Type": "application/json"},
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


@app.get("/api/system/integration-test")
async def integration_test() -> dict[str, Any]:
    """Test all system integrations"""
    if not http_session:
        raise HTTPException(500, "HTTP session not initialized")

    results = {}

    # Test kordp Gateway
    try:
        async with http_session.get(f"{KORDP_URL}/health") as response:
            results["kordp_gateway"] = {
                "status": "ok" if response.status == 200 else "error",
                "port": KORDP_GATEWAY_PORT,
                "response_code": response.status,
            }
    except Exception as e:
        results["kordp_gateway"] = {"status": "error", "port": KORDP_GATEWAY_PORT, "error": str(e)}

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
                "note": "UI-only, Backend via kordp → opena3",
            }
    except Exception as e:
        results["openwebui_ui"] = {
            "status": "warning",
            "port": OPENWEBUI_UI_PORT,
            "error": str(e),
            "note": "Optional UI component",
        }

    # Summary
    core_services_ok = all(
        r.get("status") == "ok" for key, r in results.items() if key in ["kordp_gateway", "hyper_dashboard"]
    )

    return {
        "integration_test": "complete",
        "overall_status": "ok" if core_services_ok else "partial",
        "timestamp": datetime.now(UTC).isoformat(),
        "results": results,
        "portier_compliance": "✅ Option-2-Flow via kordp",
        "port_mapping": {
            "openwebui_integration": OPENWEBUI_INTEGRATION_PORT,
            "kordp_gateway": KORDP_GATEWAY_PORT,
            "hyper_dashboard": DASHBOARD_PORT,
            "openwebui_ui": OPENWEBUI_UI_PORT,
        },
    }


@app.get("/api/openwebui/models")
async def get_available_models() -> dict[str, Any]:
    """Get available models via kordp"""
    if not http_session:
        raise HTTPException(500, "HTTP session not initialized")

    try:
        # Query models via kordp dispatch
        kordp_request = {"service_target": "openwebui3", "action": "list_models", "params": {}}

        async with http_session.post(
            f"{KORDP_URL}/dispatch/kordp", json=kordp_request, headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {"status": "success", "models": data.get("result", []), "source": "kordp → opena3 → openwebui"}
            else:
                return {"status": "error", "error": f"kordp dispatch failed (HTTP {response.status})"}

    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return {"status": "error", "error": str(e), "fallback": "Use direct OpenWebUI UI at port 8080"}


if __name__ == "__main__":
    logger.info("🚀 Starting OpenWebUI Integration Server...")
    logger.info(f"📡 Port: {OPENWEBUI_INTEGRATION_PORT}")
    logger.info(f"🚪 kordp Gateway: {KORDP_URL}")
    logger.info(f"🎯 HYPER-DASHBOARD: {DASHBOARD_URL}")
    logger.info(f"🌐 OpenWebUI UI: {OPENWEBUI_UI_URL}")
    logger.info("🔄 Option-2-Flow: OpenWebUI → kordp → opena3")

    uvicorn.run(app, host="127.0.0.1", port=OPENWEBUI_INTEGRATION_PORT, log_level="info")
