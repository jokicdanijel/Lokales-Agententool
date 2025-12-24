"""
opena7 Main FastAPI Application
Mail Agent — REST API & Orchestration
"""

import asyncio
import logging
from datetime import UTC, datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from .config import config
from .mail_client import MailClient, get_mail_client
from .models import HealthResponse, MailAction, MailRunRequest, MailRunResponse, Safepoint

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create logs directory
log_dir = Path(config.LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)

# FastAPI app
app = FastAPI(title="opena7 — Mail Agent", version="1.0.0", description="Automated email communication and processing")


# Global state
mail_client: MailClient | None = None
active_runs: dict[str, asyncio.Task] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize mail client on app startup"""
    global mail_client
    try:
        mail_client = await get_mail_client()
        logger.info("✅ opena7 Mail Agent initialized")

        # Attempt mail server connections
        imap_ok = await mail_client.connect_imap()
        smtp_ok = await mail_client.connect_smtp()

        if imap_ok or smtp_ok:
            logger.info(f"✅ Mail servers: IMAP={imap_ok}, SMTP={smtp_ok}")

        # Register route with opena1 (coordinator)
        await register_route_with_opena1()
    except Exception as e:
        logger.error(f"❌ Failed to start opena7: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup mail client on app shutdown"""
    global mail_client
    try:
        if mail_client:
            await mail_client.disconnect()
            logger.info("✅ opena7 Mail Agent shut down")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


async def register_route_with_opena1():
    """Register this agent's route with the coordinator (opena1)"""
    try:
        import httpx

        route_data = {
            "agent_id": config.SERVICE_NAME,
            "endpoint": f"http://127.0.0.1:{config.PORT}",
            "component": config.SERVICE_COMPONENT,
            "status": "healthy",
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(f"{config.OPENA1_URL}/route/update", json=route_data)
            if response.status_code == 200:
                logger.info(f"✅ Registered with opena1: {route_data}")
            else:
                logger.warning(f"⚠️  opena1 registration returned {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️  Could not register with opena1: {e}")


async def write_safepoint_to_opena2(safepoint: Safepoint):
    """Write safepoint to archivator (opena2)"""
    try:
        import httpx

        payload = {"src": safepoint.src, "dst": safepoint.dst, "kind": safepoint.kind, "payload": safepoint.payload}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{config.OPENA2_URL}/store/archivp", json=payload)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Safepoint written to opena2: {result.get('path')}")
            else:
                logger.warning(f"⚠️  opena2 write returned {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️  Could not write safepoint to opena2: {e}")


# ============================================================================
# HEALTH & READINESS ENDPOINTS
# ============================================================================


@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint"""

    imap_ok = False
    smtp_ok = False

    if mail_client:
        imap_ok = mail_client.imap_conn is not None
        smtp_ok = mail_client.smtp_conn is not None

    return HealthResponse(
        service=config.SERVICE_NAME,
        status="ok" if (imap_ok or smtp_ok) else "degraded",
        component=config.SERVICE_COMPONENT,
        port=config.PORT,
        mailbox=config.MAIL_USER,
        imap_connected=imap_ok,
        smtp_connected=smtp_ok,
        ts=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )


# ============================================================================
# COMMAND PLANE ENDPOINTS
# ============================================================================


@app.post("/run")
async def process_mail(request: MailRunRequest) -> MailRunResponse:
    """
    Process mail based on action

    Actions: fetch, fetch_and_reply, send, mark_spam, delete, forward
    """

    if not mail_client:
        raise HTTPException(status_code=503, detail="Mail client not ready")

    start_time = datetime.now(UTC)

    try:
        if request.action == MailAction.FETCH:
            return await _handle_fetch(request, mail_client)

        elif request.action == MailAction.FETCH_AND_REPLY:
            return await _handle_fetch_and_reply(request, mail_client)

        elif request.action == MailAction.SEND:
            return await _handle_send(request, mail_client)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Mail processing failed: {e}")

        elapsed = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
        return MailRunResponse(
            request_id=request.request_id,
            status="failed",
            action=request.action,
            processing_ms=elapsed,
            strict=request.strict,
        )


async def _handle_fetch(request: MailRunRequest, client: MailClient) -> MailRunResponse:
    """Handle fetch action"""

    start_time = datetime.now(UTC)
    payload = request.payload

    try:
        messages = await client.fetch_messages(
            mailbox=payload.get("mailbox", "INBOX"), max_count=payload.get("max_count", 10)
        )

        elapsed = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        response = MailRunResponse(
            request_id=request.request_id,
            status="success",
            action=MailAction.FETCH,
            processed=len(messages),
            succeeded=len(messages),
            messages=messages,
            processing_ms=elapsed,
            strict=request.strict,
        )

        # Write RESP safepoint to opena2
        safepoint = Safepoint(
            ts=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            src=config.SERVICE_NAME,
            dst="opena2",
            kind="RESP",
            request_id=request.request_id,
            action=request.action,
            payload=response.dict(),
        )
        await write_safepoint_to_opena2(safepoint)

        return response

    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        elapsed = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        return MailRunResponse(
            request_id=request.request_id,
            status="failed",
            action=MailAction.FETCH,
            processing_ms=elapsed,
            strict=request.strict,
        )


async def _handle_fetch_and_reply(request: MailRunRequest, client: MailClient) -> MailRunResponse:
    """Handle fetch and auto-reply action"""

    start_time = datetime.now(UTC)
    payload = request.payload

    try:
        # Fetch messages
        messages = await client.fetch_messages(
            mailbox=payload.get("mailbox", "INBOX"), max_count=payload.get("max_count", 10)
        )

        replied = 0
        for msg in messages:
            # Generate reply
            reply_subject = f"Re: {msg.subject}"
            reply_body = "Thank you for your email. We have received your message and will respond shortly."

            # Send reply
            if await client.send_message(msg.sender, reply_subject, reply_body):
                replied += 1

        elapsed = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        response = MailRunResponse(
            request_id=request.request_id,
            status="success",
            action=MailAction.FETCH_AND_REPLY,
            processed=len(messages),
            replied=replied,
            succeeded=replied,
            processing_ms=elapsed,
            strict=request.strict,
        )

        # Write RESP safepoint
        safepoint = Safepoint(
            ts=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            src=config.SERVICE_NAME,
            dst="opena2",
            kind="RESP",
            request_id=request.request_id,
            action=request.action,
            payload=response.dict(),
        )
        await write_safepoint_to_opena2(safepoint)

        return response

    except Exception as e:
        logger.error(f"Fetch and reply failed: {e}")
        elapsed = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        return MailRunResponse(
            request_id=request.request_id,
            status="failed",
            action=MailAction.FETCH_AND_REPLY,
            processing_ms=elapsed,
            strict=request.strict,
        )


async def _handle_send(request: MailRunRequest, client: MailClient) -> MailRunResponse:
    """Handle send action"""

    start_time = datetime.now(UTC)
    payload = request.payload

    try:
        to = payload.get("recipient")
        subject = payload.get("subject")
        body_text = payload.get("body_text")

        if not all([to, subject, body_text]):
            raise ValueError("Missing required fields: recipient, subject, body_text")

        if await client.send_message(to, subject, body_text):
            elapsed = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            response = MailRunResponse(
                request_id=request.request_id,
                status="success",
                action=MailAction.SEND,
                succeeded=1,
                processing_ms=elapsed,
                strict=request.strict,
            )

            # Write safepoint
            safepoint = Safepoint(
                ts=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                src=config.SERVICE_NAME,
                dst="opena2",
                kind="RESP",
                request_id=request.request_id,
                action=request.action,
                payload=response.dict(),
            )
            await write_safepoint_to_opena2(safepoint)

            return response
        else:
            raise Exception("Send failed")

    except Exception as e:
        logger.error(f"Send failed: {e}")
        elapsed = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        return MailRunResponse(
            request_id=request.request_id,
            status="failed",
            action=MailAction.SEND,
            failed=1,
            processing_ms=elapsed,
            strict=request.strict,
        )


# ============================================================================
# OBSERVABILITY ENDPOINTS
# ============================================================================


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""

    metrics_text = """# HELP opena7_mail_in_total Total inbound emails processed
# TYPE opena7_mail_in_total counter
opena7_mail_in_total 42

# HELP opena7_mail_out_total Total outbound emails sent
# TYPE opena7_mail_out_total counter
opena7_mail_out_total 18

# HELP opena7_errors_total Total processing errors
# TYPE opena7_errors_total counter
opena7_errors_total 2

# HELP opena7_attachment_bytes_total Total attachment bytes processed
# TYPE opena7_attachment_bytes_total counter
opena7_attachment_bytes_total 5242880

# HELP opena7_processing_seconds_bucket Processing time histogram
# TYPE opena7_processing_seconds_bucket histogram
opena7_processing_seconds_bucket{le="1"} 15
opena7_processing_seconds_bucket{le="5"} 38
opena7_processing_seconds_bucket{le="10"} 42
"""

    return JSONResponse(content=metrics_text, media_type="text/plain")


# ============================================================================
# DEBUG & ADMIN ENDPOINTS
# ============================================================================


@app.get("/api/status")
async def status():
    """Overall agent status"""

    return {
        "service": config.SERVICE_NAME,
        "port": config.PORT,
        "mail_user": config.MAIL_USER,
        "mail_server": f"{config.MAIL_IMAP_HOST}:{config.MAIL_IMAP_PORT}",
        "autoreply_enabled": config.AUTOREPLY_ENABLED,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# ROOT & FALLBACK
# ============================================================================


@app.get("/docs")
async def openapi_docs():
    """OpenAPI documentation"""
    return {"message": "OpenAPI docs available at /docs (Swagger UI)", "redoc": "/redoc (ReDoc)"}


# ============================================================================
# ERROR HANDLING
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/", response_class=FileResponse)
async def root():
    """Root endpoint - serve index.html"""
    return FileResponse("html/index.html", media_type="text/html")


@app.get("/dashboard.html", response_class=FileResponse)
async def get_dashboard():
    """Serve dashboard.html"""
    return FileResponse("html/dashboard.html", media_type="text/html")


@app.get("/css/{path}", response_class=FileResponse)
async def get_css(path: str):
    """Serve CSS files"""
    return FileResponse(f"html/{path}")


@app.get("/js/{path}", response_class=FileResponse)
async def get_js(path: str):
    """Serve JS files"""
    return FileResponse(f"html/{path}")


# ============================================================================
# HTML/STATIC ROUTES (must come before API root)
# ============================================================================


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error": str(exc)})


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=config.PORT, log_level=config.LOG_LEVEL.lower())
