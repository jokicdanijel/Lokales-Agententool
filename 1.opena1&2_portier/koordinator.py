"""
koordinator.py — opena1 Coordinator
Strict 7.1 validation, 7.2 decision schema, CMD-envelope creation,
tool selection, archivator forwarding, and error schema 8.3 responses.
LOCATION: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/koordinator.py
"""

import json
import logging
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from schemas import Decision72, ErrorSchema83, Request71

router = APIRouter(prefix="/log", tags=["opena1"])
logger = logging.getLogger("opena1.koordinator")

ARCHIVATOR_URL = "http://127.0.0.1:12345/finalize/opena2"


def utc():
    """Generate UTC timestamp with Z suffix."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def error(code, msg, details=None, req_id="unknown"):
    """Create standard 8.3 error response."""
    return ErrorSchema83(
        request_id=req_id,
        timestamp=utc(),
        source="opena1",
        error={"code": code, "message": msg, "details": details or {}},
        strict=True,
    )


def build_cmd(req: Request71, tool: str, reason: str):
    """Build CMD envelope for opena2."""
    return {
        "request_id": req.request_id,
        "timestamp": utc(),
        "source": "opena1",
        "cmd": {
            "command": req.command,
            "tool": tool,
            "reason": reason,
            "payload": req.payload,
            "routing": req.routing.model_dump() if hasattr(req.routing, "model_dump") else req.routing,
            "project": req.project.model_dump(),
        },
        "strict": True,
    }


def select_tool(req: Request71):
    """Select tool based on command content."""
    c = req.command.lower()
    if "file" in c:
        return "tool_file_manager", "command contains 'file'"
    if "search" in c:
        return "tool_file_searcher", "command contains 'search'"
    if "analyze" in c:
        return "tool_text_analyzer", "command contains 'analyze'"
    return "tool_default", "fallback"


@router.post("/opena1")
async def log_opena1(body: dict):
    """Main opena1 endpoint - validate, select tool, forward to archivator."""
    req_id = body.get("request_id", "unknown")

    # Validate 7.1 schema
    try:
        req = Request71(**body)
        logger.info(f"[7.1 VALID] {req.request_id}")
    except ValidationError as ve:
        errs = [{"field": ".".join(map(str, e["loc"])), "error": e["msg"]} for e in ve.errors()]
        raise HTTPException(
            400,
            detail=json.loads(
                error("SCHEMA_71_INVALID", "Schema mismatch", {"validation_errors": errs}, req_id).model_dump_json()
            ),
        )

    # Tool selection
    tool, reason = select_tool(req)
    logger.info(f"[TOOL] {tool} — {reason}")

    # Build CMD envelope
    cmd = build_cmd(req, tool, reason)

    # Forward to archivator
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(ARCHIVATOR_URL, json=cmd)
        if r.status_code != 200:
            raise Exception(r.text)
    except Exception as ex:
        logger.error(f"[FORWARD_ERROR] {ex}")
        raise HTTPException(
            500, detail=json.loads(error("FORWARD_ERROR", str(ex), req_id=req.request_id).model_dump_json())
        )

    # Build 7.2 decision response
    decision = Decision72(
        request_id=req.request_id,
        timestamp=utc(),
        source="opena1",
        decision={
            "selected_tool": tool,
            "reason": reason,
            "resolved_path": req.routing.resolved_path if hasattr(req.routing, "resolved_path") else None,
        },
        archivator_forward={"endpoint": ARCHIVATOR_URL, "status": "sent"},
        status="FORWARDED",
        strict=True,
    )

    logger.info(f"[7.2 OUT] {req.request_id}")
    return decision.model_dump()
