"""
kordp/router.py — Dispatch Router
Routes tool commands from opena1 CMD envelopes to correct tool endpoints.
LOCATION: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/kordp/router.py
"""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from kordp.schemas import DispatchRequest, DispatchResponse
from kordp.tool_resolver import ToolResolver

router = APIRouter(prefix="/dispatch", tags=["kordp"])
logger = logging.getLogger("kordp.router")

# Tool resolver
resolver = ToolResolver()

# Archivator endpoint
ARCHIVATOR_URL = "http://127.0.0.1:12345/store/resp"


def utc():
    """Generate UTC timestamp with Z suffix."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@router.post("/kordp")
async def dispatch_task(body: dict[str, Any]) -> dict[str, Any]:
    """
    Dispatch tool command from opena1 CMD envelope.

    Expected body structure:
    {
        "request_id": "uuid",
        "timestamp": "ISO-8601 Z",
        "source": "opena1",
        "cmd": {
            "command": "...",
            "tool": "tool_id",
            "reason": "...",
            "payload": {...},
            "routing": {...},
            "project": {...}
        },
        "strict": true
    }
    """
    req_id = body.get("request_id", "unknown")
    cmd = body.get("cmd", {})
    tool_id = cmd.get("tool", "tool_default")

    logger.info(f"[DISPATCH] {req_id} → tool: {tool_id}")

    # Validate dispatch request
    try:
        dispatch = DispatchRequest(
            agent=tool_id, action=cmd.get("command", "execute"), data=cmd.get("payload", {}), request_id=req_id
        )
    except ValidationError as ve:
        logger.error(f"[DISPATCH_ERROR] Invalid request: {ve}")
        raise HTTPException(400, detail={"error": "INVALID_DISPATCH_REQUEST", "details": ve.errors()})

    # Resolve tool endpoint
    route_info = resolver.resolve(tool_id)
    if not route_info:
        logger.error(f"[DISPATCH_ERROR] No route for tool: {tool_id}")
        raise HTTPException(404, detail={"error": "TOOL_NOT_FOUND", "tool": tool_id})

    target_url = route_info["url"]
    timeout = route_info.get("timeout", 30)

    # Execute tool call
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(target_url, json=dispatch.data, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            result = response.json()
    except httpx.TimeoutException:
        logger.error(f"[TIMEOUT] Tool execution timeout: {tool_id}")
        raise HTTPException(504, detail={"error": "TOOL_TIMEOUT", "tool": tool_id, "timeout": timeout})
    except Exception as ex:
        logger.error(f"[TOOL_ERROR] {ex}")
        raise HTTPException(500, detail={"error": "TOOL_EXECUTION_FAILED", "message": str(ex)})

    # Forward RESP to opena2 for safepoint
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp_payload = {
                "request_id": req_id,
                "timestamp": utc(),
                "source": tool_id,
                "result": result,
                "strict": True,
            }
            await client.post(ARCHIVATOR_URL, json=resp_payload)
            logger.info("[RESP] Safepoint forwarded to opena2")
    except Exception as e:
        logger.warning(f"Failed to forward RESP to opena2: {e}")

    # Build dispatch response
    response_obj = DispatchResponse(ok=True, routed_to=route_info, request_id=req_id, strict=True)

    logger.info(f"[DISPATCH_OK] {req_id}")
    return response_obj.model_dump()


@router.get("/routes")
async def list_routes() -> dict[str, Any]:
    """List all available tool routes."""
    routes = resolver.list_all()
    return {"ok": True, "routes": routes, "count": len(routes)}


@router.get("/routes/{tool_id}")
async def get_route(tool_id: str) -> dict[str, Any]:
    """Get route info for specific tool."""
    route = resolver.resolve(tool_id)
    if not route:
        raise HTTPException(404, detail={"error": "TOOL_NOT_FOUND", "tool": tool_id})

    return {"ok": True, "tool": tool_id, "route": route}
