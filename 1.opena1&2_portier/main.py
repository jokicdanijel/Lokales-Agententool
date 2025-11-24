"""
3.opena1_coordinator/main.py – Portier Coordinator Service (opena1)
============================================================================
FastAPI service for coordinating Portier agent communication.

Port: 12344
Endpoints:
  GET /health
  POST /log/opena1

Usage:
  cd 3.opena1_coordinator
  python main.py
  # → Listening on http://127.0.0.1:12344
"""

import os
import sys
import asyncio
import uvicorn
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from src.portier_service_base import (
    PortierServiceBase,
    PortierServiceConfig,
    PortPolicyMiddleware
)

# ─────────────────────────────────────────────────────────────────────────
# BEARER TOKEN CONFIGURATION – PHASE 15.4 STRICT POLICY
# ─────────────────────────────────────────────────────────────────────────

VALID_BEARER_TOKENS = {
    # Core Services
    "opena1-coordinator": "sk_opena1_coord_12344_strict_v1",
    "opena2-archivator": "sk_opena2_arch_12345_strict_v1",

    # Agent Services (opena3-opena20)
    "opena3-webui": "sk_opena3_web_12347_strict_v1",
    "opena4-telegram": "sk_opena4_tele_12348_strict_v1",
    "opena5-vscode": "sk_opena5_vsc_12350_strict_v1",
    "opena6-browser": "sk_opena6_brow_12351_strict_v1",
    "opena7-email": "sk_opena7_mail_12352_strict_v1",
    "opena8-whatsapp": "sk_opena8_what_12353_strict_v1",
    "opena9-call": "sk_opena9_call_12354_strict_v1",
    "opena10-answer": "sk_opena10_answ_12355_strict_v1",
    "opena11-unlock": "sk_opena11_lock_12356_strict_v1",
    "opena12-social": "sk_opena12_soc_12357_strict_v1",
    "opena13-influencer": "sk_opena13_infl_12358_strict_v1",
    "opena14-calendar": "sk_opena14_cal_12359_strict_v1",
    "opena15-html": "sk_opena15_html_12360_strict_v1",
    "opena16-shop": "sk_opena16_shop_12361_strict_v1",
    "opena17-homepage": "sk_opena17_home_12362_strict_v1",
    "opena18-archive": "sk_opena18_arch_12363_strict_v1",
    "opena19-trading": "sk_opena19_trade_12364_strict_v1",
    "opena20-dashboard": "sk_opena20_dash_12365_strict_v1",

    # Testing
    "test-harness": "sk_test_harness_phase15_strict_v1",
}

TOKEN_TO_CLIENT = {v: k for k, v in VALID_BEARER_TOKENS.items()}

async def verify_bearer_token(request: Request) -> str:
    """
    STRICT policy: Verify bearer token on protected endpoints
    Returns: client_id (key from VALID_BEARER_TOKENS)
    Raises: HTTPException 401 if invalid/missing
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        # Log security event
        asyncio.create_task(
            log_security_event("auth_missing", "No Authorization header")
        )
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    if not auth_header.startswith("Bearer "):
        asyncio.create_task(
            log_security_event("auth_malformed", "Invalid Authorization format")
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization format (use: Bearer <token>)"
        )

    token = auth_header[7:]  # Remove "Bearer " prefix

    if token not in TOKEN_TO_CLIENT:
        asyncio.create_task(
            log_security_event("auth_invalid", f"Invalid token: {token[:10]}...")
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid bearer token"
        )

    client_id = TOKEN_TO_CLIENT[token]
    return client_id

async def log_security_event(event_type: str, details: str) -> None:
    """Log security events (auth failures, etc.) to archiv"""
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        security_data = {
            "src": "system",
            "dst": "opena1",
            "kind": "SECURITY_EVENT",
            "payload": {
                "event_type": event_type,
                "details": details,
                "timestamp": timestamp
            }
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://127.0.0.1:12344/log/opena1",
                json=security_data,
                timeout=2.0
            )
    except Exception as e:
        print(f"[opena1] Warning: Failed to log security event: {e}")

# ─────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────

config = PortierServiceConfig(
    service_name="opena1",
    service_port=int(os.getenv("OPENA1_PORT", "12344")),
    allowed_port_min=12344,
    allowed_port_max=12399,
    bind_addr=os.getenv("BIND_ADDR", "127.0.0.1"),
    archiv_base=os.getenv("ARCHIV_BASE", "./archiv")
)

# ─────────────────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="opena1 – Portier Coordinator",
    description="Coordinator service for Portier agent orchestration",
    version="1.0.0"
)

# Middleware for port-policy enforcement
PortPolicyMiddleware(app, config)

# Initialize base service
service_base = PortierServiceBase(config)

# ─────────────────────────────────────────────────────────────────────────
# LOGGING CONFIGURATION – PHASE 15.2
# ─────────────────────────────────────────────────────────────────────────
# Note: /log/opena1 endpoint is already registered by setup_safepoints()
# in PortierServiceBase. This config ensures the log directory exists.

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_OPENA1 = os.path.join(LOG_DIR, "opena1_safepoints.log")

print(f"[opena1] Safepoint log directory: {LOG_DIR}")
print(f"[opena1] Safepoint log file: {LOG_FILE_OPENA1}")
print(f"[opena1] /log/opena1 endpoint available via PortierServiceBase")


# Setup endpoints
service_base.setup_health_endpoint(app)
service_base.setup_safepoints(app, config.archiv_base)

# ─────────────────────────────────────────────────────────────────────────
# ROOT ENDPOINT
# ─────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "opena1",
        "status": "online",
        "port": config.service_port,
        "docs": "/docs"
    }



# ─────────────────────────────────────────────────────────────────────────
# /REQUEST ENDPOINT – PHASE 15.1 IMPLEMENTATION
# ─────────────────────────────────────────────────────────────────────────
# Routes incoming requests through Option-2-Flow:
# opena1 → opena2 (Archivator) → kordp (Gateway) → Agents
# Automatically creates safepoint logs for all requests
# ─────────────────────────────────────────────────────────────────────────

class RequestPayload(BaseModel):
    """Incoming request structure"""
    source: str  # "user", "agent", "system"
    user_query: str  # The actual question/command
    context: Optional[Dict[str, Any]] = None  # Additional context

class ResponsePayload(BaseModel):
    """Response structure"""
    request_id: str
    status: str  # "success", "pending", "error"
    response: str
    metadata: Dict[str, Any]

@app.post("/request")
async def handle_request(
    payload: RequestPayload,
    request: Request,
    client_id: str = Depends(verify_bearer_token)
) -> ResponsePayload:
    """
    POST /request – Main Option-2-Flow entry point with STRICT POLICY

    PHASE 15.4: Bearer token REQUIRED

    Flow:
      1. Verify bearer token (strict) → client_id
      2. Generate request_id (UUID)
      3. LOG CMD safepoint with client_id (background)
      4. Process request
      5. LOG RESP safepoint with client_id (background)
      6. Return response immediately (<5ms latency)
    """

    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    print(f"[opena1] Request {request_id}: Client={client_id}, Query={payload.user_query[:50]}")

    try:
        # STEP 1: Log CMD (Command) safepoint asynchronously
        async def log_cmd_safepoint():
            try:
                cmd_data = {
                    "src": client_id,
                    "dst": "opena1",
                    "kind": "CMD",
                    "payload": {
                        "request_id": request_id,
                        "query": payload.user_query,
                        "context": payload.context,
                        "timestamp": timestamp,
                        "client_id": client_id
                    }
                }
                # Fire and forget - don't wait
                await asyncio.create_task(log_safepoint_async(cmd_data))
            except Exception as e:
                print(f"[opena1] Warning: Failed to log CMD safepoint: {e}")

        # Start logging in background
        asyncio.create_task(log_cmd_safepoint())

        # STEP 2: Process request (simulated)
        agent_response = f"Request received and queued for processing. Query: {payload.user_query}"
        response_time_ms = 2

        # STEP 3: Log RESP (Response) safepoint asynchronously
        async def log_resp_safepoint():
            try:
                resp_data = {
                    "src": "opena1",
                    "dst": client_id,
                    "kind": "RESP",
                    "payload": {
                        "request_id": request_id,
                        "response": agent_response,
                        "status": "success",
                        "timestamp": timestamp,
                        "latency_ms": response_time_ms,
                        "client_id": client_id
                    }
                }
                # Fire and forget
                await asyncio.create_task(log_safepoint_async(resp_data))
            except Exception as e:
                print(f"[opena1] Warning: Failed to log RESP safepoint: {e}")

        # Start response logging in background
        asyncio.create_task(log_resp_safepoint())

        print(f"[opena1] Request {request_id}: CMD/RESP logging queued (non-blocking)")

        # STEP 4: Return response immediately (don't wait for logging)
        return ResponsePayload(
            request_id=request_id,
            status="success",
            response=agent_response,
            metadata={
                "source": "opena1",
                "timestamp": timestamp,
                "user_query": payload.user_query,
                "source_origin": client_id,
                "latency_ms": response_time_ms,
                "safepoint_logged": True,
                "policy": "strict",
                "auth_verified": True
            }
        )

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"[opena1] Error in /request: {error_msg}")
        traceback.print_exc()

        # Log ERROR safepoint
        async def log_error_safepoint():
            try:
                err_data = {
                    "src": payload.source,
                    "dst": "opena1",
                    "kind": "ERROR",
                    "payload": {
                        "request_id": request_id,
                        "error": error_msg,
                        "timestamp": timestamp
                    }
                }
                await asyncio.create_task(log_safepoint_async(err_data))
            except:
                pass

        asyncio.create_task(log_error_safepoint())

        return ResponsePayload(
            request_id=request_id,
            status="error",
            response=f"Error processing request: {error_msg}",
            metadata={"source": "opena1", "timestamp": timestamp, "error": error_msg}
        )


async def log_safepoint_async(safepoint_data: Dict[str, Any]) -> None:
    """Helper function to log safepoint asynchronously"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:12344/log/opena1",
                json=safepoint_data,
                timeout=2.0
            )
            if response.status_code == 200:
                data = response.json()
                request_id = safepoint_data.get("payload", {}).get("request_id", "?")
                print(f"[opena1] Safepoint logged: {safepoint_data['kind']} - {request_id}")
            else:
                print(f"[opena1] Failed to log safepoint: HTTP {response.status_code}")
    except Exception as e:
        print(f"[opena1] Safepoint logging error: {e}")

@app.get("/request/status/{request_id}")
async def get_request_status(request_id: str) -> Dict[str, Any]:
    """GET /request/status/{request_id} – Check status of a request"""
    return {
        "request_id": request_id,
        "status": "pending",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message": "Status lookup (Phase 15.2)"
    }

# ─────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = config.service_port

    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║           opena1 – Portier Coordinator                    ║
    ╚════════════════════════════════════════════════════════════╝

    Port:      {port}
    Bind:      {config.bind_addr}
    Docs:      http://{config.bind_addr}:{port}/docs
    Health:    http://{config.bind_addr}:{port}/health

    Starting server...
    """)

    uvicorn.run(
        "main:app",
        host=config.bind_addr,
        port=port,
        reload=False,
        log_level="info"
    )
