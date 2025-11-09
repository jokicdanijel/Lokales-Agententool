"""
opena3/openwebui_agent.py
OpenWebUI Adapter Agent für ELION Hyper-Dashboard
Port: 12347
Relayed Requests zu OpenWebUI (Port 8080)
"""

import os
import httpx
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="opena3-openwebui-agent", version="1.0.0")

# Configuration
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
OPENWEBUI_TIMEOUT = float(os.getenv("OPENWEBUI_TIMEOUT", "30.0"))

# ============================================================================
# Pydantic Models
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    ts: str
    port: int

class InfoResponse(BaseModel):
    agent_id: str
    version: str
    openwebui_url: str
    endpoints: list

class ChatRequest(BaseModel):
    message: str
    model: str = "default"
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    ts: str

# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/health")
async def health() -> HealthResponse:
    """Health check mit Timestamp"""
    return HealthResponse(
        status="ok",
        ts=datetime.utcnow().isoformat() + "Z",
        port=12347
    )

@app.get("/info")
async def info() -> InfoResponse:
    """Agent Info"""
    return InfoResponse(
        agent_id="opena3",
        version="1.0.0",
        openwebui_url=OPENWEBUI_URL,
        endpoints=["/health", "/info", "/chat", "/command"]
    )

# ============================================================================
# Main Endpoints
# ============================================================================

@app.post("/chat")
async def chat(req: ChatRequest) -> ChatResponse:
    """Relay Chat Request zu OpenWebUI"""
    try:
        async with httpx.AsyncClient(timeout=OPENWEBUI_TIMEOUT) as client:
            # OpenWebUI API v1
            response = await client.post(
                f"{OPENWEBUI_URL}/api/chat",
                json={
                    "message": req.message,
                    "model": req.model,
                    "temperature": req.temperature
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            return ChatResponse(
                response=data.get("response", "No response from OpenWebUI"),
                model=req.model,
                ts=datetime.utcnow().isoformat() + "Z"
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"OpenWebUI error: {str(e)}")

@app.post("/command")
async def command(payload: dict) -> dict:
    """Generic Command Relay zu OpenWebUI"""
    try:
        async with httpx.AsyncClient(timeout=OPENWEBUI_TIMEOUT) as client:
            response = await client.post(
                f"{OPENWEBUI_URL}/api/command",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"OpenWebUI error: {str(e)}")

@app.post("/invoke")
async def invoke(payload: dict) -> dict:
    """Generic Invoke für Dashboard Compat"""
    return await command(payload)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=12347)
