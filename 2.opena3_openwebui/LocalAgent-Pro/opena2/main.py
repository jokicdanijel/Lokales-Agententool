#!/usr/bin/env python3
"""
opena2 - Archivator Service
Port: 12345
Bearer Token: sk_opena2_arch_12345_strict_v1

PHASE 15.4 Policy: STRICT - Bearer token required for all protected endpoints
"""

import json
import sys
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.auth import verify_bearer_token

app = FastAPI(
    title="opena2",
    description="Archivator Service",
    version="2.0"
)

class HealthResponse(BaseModel):
    status: str
    service: str
    port: int
    policy: str
    version: str

@app.get("/health")
async def health():
    """Diagnostic endpoint - no auth required"""
    return HealthResponse(
        status="healthy",
        service="opena2-archivator",
        port=12345,
        policy="strict",
        version="2.0"
    )

@app.get("/status")
async def status(client_id: str = Depends(verify_bearer_token)):
    """Status endpoint - requires bearer token"""
    return {
        "service": "opena2-archivator",
        "status": "operational",
        "client_id": client_id,
        "policy": "strict",
        "auth_verified": True
    }

@app.get("/info")
async def info(client_id: str = Depends(verify_bearer_token)):
    """Agent information"""
    return {
        "agent_name": "opena2",
        "function": "Archivator",
        "port": 12345,
        "client_id": client_id,
        "bearer_token_configured": True
    }

@app.post("/request")
async def handle_request(request: Request, client_id: str = Depends(verify_bearer_token)):
    """Process incoming request - requires bearer token"""
    body = await request.json()
    return {
        "request_id": "uuid-placeholder",
        "status": "success",
        "service": "opena2-archivator",
        "client_id": client_id,
        "policy": "strict",
        "auth_verified": True
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=12345,
        log_level="info"
    )
