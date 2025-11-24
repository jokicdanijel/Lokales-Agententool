#!/usr/bin/env python3
"""
opena14 - Calendar Service
Port: 12359
Bearer Token: sk_opena14_cal_12359_strict_v1

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
    title="opena14",
    description="Calendar Service",
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
        service="opena14-calendar",
        port=12359,
        policy="strict",
        version="2.0"
    )

@app.get("/status")
async def status(client_id: str = Depends(verify_bearer_token)):
    """Status endpoint - requires bearer token"""
    return {
        "service": "opena14-calendar",
        "status": "operational",
        "client_id": client_id,
        "policy": "strict",
        "auth_verified": True
    }

@app.get("/info")
async def info(client_id: str = Depends(verify_bearer_token)):
    """Agent information"""
    return {
        "agent_name": "opena14",
        "function": "Calendar",
        "port": 12359,
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
        "service": "opena14-calendar",
        "client_id": client_id,
        "policy": "strict",
        "auth_verified": True
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=12359,
        log_level="info"
    )
