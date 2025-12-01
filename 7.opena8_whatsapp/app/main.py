"""
opena8 FastAPI Main Server
WhatsApp Webhook handler, message sending, health endpoint
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
import httpx

from app.config import config
from app.models import (
    WhatsAppMessage, SendMessageRequest, SendMessageResponse, HealthResponse,
    Safepoint, MailRunRequest, MailRunResponse
)
from app.whatsapp_client import WhatsAppClient, MessageClassifier, MediaHandler


# Logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Metrics
metrics_wa_in = Counter("whatsapp_in_total", "Inbound messages", ["type"])
metrics_wa_out = Counter("whatsapp_out_total", "Outbound messages", ["type"])
metrics_errors = Counter("whatsapp_errors_total", "Errors", ["category"])
metrics_latency = Histogram("whatsapp_latency_seconds", "Request latency", ["endpoint"])

# FastAPI
app = FastAPI(title="opena8-whatsapp", version="1.0.0")
wa_client = WhatsAppClient()


@app.on_event("startup")
async def startup():
    """Register agent with opena1"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{config.OPENA1_URL}/route/update",
                json={
                    "agent_id": "opena8",
                    "endpoint": f"http://127.0.0.1:{config.PORT}",
                    "component": "whatsapp"
                }
            )
            if response.status_code == 200:
                logger.info("✅ Registered with opena1")
            else:
                logger.warning(f"⚠️  opena1 registration: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Startup registration failed: {e}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    # Verify opena2 and opena1 connectivity
    opena2_ok = False
    opena1_ok = False
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r2 = await client.get(f"{config.OPENA2_URL}/health")
            opena2_ok = r2.status_code == 200
    except:
        pass
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r1 = await client.get(f"{config.OPENA1_URL}/health")
            opena1_ok = r1.status_code == 200
    except:
        pass
    
    status = "ok" if (opena2_ok and opena1_ok) else ("degraded" if opena2_ok or opena1_ok else "error")
    
    return HealthResponse(
        status=status,
        service="opena8",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        meta_api_connected=True,  # Would check in real impl
        opena2_connected=opena2_ok,
        opena1_connected=opena1_ok
    )


@app.get("/webhook")
async def webhook_verify(request: Request):
    """Meta Webhook verification (GET)"""
    mode = request.query_params.get("hub.mode")
    challenge = request.query_params.get("hub.challenge")
    verify_token = request.query_params.get("hub.verify_token")
    
    if mode == "subscribe" and verify_token == config.META_WEBHOOK_VERIFY_TOKEN:
        logger.info(f"✅ Webhook verified")
        return int(challenge)
    else:
        logger.warning("❌ Webhook verification failed")
        raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhook")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming WhatsApp messages (POST)"""
    try:
        body = await request.json()
        
        # Parse entry
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [])
        
        if not changes:
            return {"status": "ok"}
        
        change = changes[0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return {"status": "ok"}
        
        # Parse message
        msg_obj = await wa_client.parse_webhook_event(entry)
        if not msg_obj:
            return {"status": "ok"}
        
        metrics_wa_in.labels(type=msg_obj.type.value).inc()
        logger.info(f"📨 Inbound: {msg_obj.message_id} from {msg_obj.phone_number}")
        
        # Archive to opena2
        safepoint = Safepoint(
            ts=datetime.utcnow(),
            src="opena8",
            dst="opena2",
            kind="MSG",
            payload=msg_obj.dict()
        )
        
        # Background: archive safepoint
        background_tasks.add_task(
            _archive_safepoint,
            safepoint
        )
        
        return {"status": "ok"}
    
    except Exception as e:
        metrics_errors.labels(category="webhook_parse").inc()
        logger.error(f"❌ Webhook handler error: {e}")
        return {"status": "error", "detail": str(e)}


@app.post("/send")
async def send_message(req: SendMessageRequest):
    """Send WhatsApp message"""
    try:
        success = False
        msg_id = None
        
        if req.message_type == MessageType.TEXT:
            success, msg_id, error = await wa_client.send_message(req.to_phone, req.body or "")
        elif req.media_url:
            success, msg_id, error = await wa_client.send_media(
                req.to_phone,
                req.media_url,
                req.media_type.value if req.media_type else "image"
            )
        
        metrics_wa_out.labels(type=req.message_type.value).inc()
        
        if success:
            logger.info(f"✅ Sent: {msg_id} to {req.to_phone}")
        else:
            logger.error(f"❌ Send failed: {error}")
            metrics_errors.labels(category="send_failed").inc()
        
        return SendMessageResponse(
            success=success,
            message_id=msg_id,
            error=error,
            sent_at=datetime.utcnow()
        )
    
    except Exception as e:
        metrics_errors.labels(category="send_exception").inc()
        logger.error(f"❌ Send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
async def run_action(req: MailRunRequest):
    """Generic action endpoint for agent orchestration"""
    try:
        action = req.action
        payload = req.payload
        
        if action == "ingest":
            # Process incoming webhook
            msg_obj = await wa_client.parse_webhook_event(payload)
            if msg_obj:
                return MailRunResponse(
                    success=True,
                    action="ingest",
                    data=msg_obj.dict(),
                    timestamp=datetime.utcnow()
                )
        
        elif action == "send":
            # Send message
            success, msg_id, error = await wa_client.send_message(
                payload.get("to_phone"),
                payload.get("body", "")
            )
            return MailRunResponse(
                success=success,
                action="send",
                data={"message_id": msg_id},
                error=error,
                timestamp=datetime.utcnow()
            )
        
        return MailRunResponse(
            success=False,
            action=action,
            error=f"Unknown action: {action}",
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        metrics_errors.labels(category="run_action").inc()
        logger.error(f"❌ Run action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/api/status")
async def api_status():
    """Agent status endpoint"""
    return {
        "agent": "opena8",
        "component": "whatsapp",
        "port": config.PORT,
        "status": "running",
        "meta_phone": config.META_PHONE_NUMBER_ID[:8] + "***",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root info endpoint"""
    return {
        "service": "opena8-whatsapp",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /webhook": "Webhook verification (Meta)",
            "POST /webhook": "Webhook handler (inbound messages)",
            "POST /send": "Send WhatsApp message",
            "POST /run": "Generic agent action",
            "GET /metrics": "Prometheus metrics",
            "GET /api/status": "Agent status",
            "GET /": "This info"
        }
    }


async def _archive_safepoint(safepoint: Safepoint):
    """Background task: archive safepoint to opena2"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{config.OPENA2_URL}/store/archivp",
                json=safepoint.dict()
            )
            if response.status_code == 200:
                logger.info(f"✅ Archived: {safepoint.kind} to opena2")
            else:
                logger.warning(f"⚠️  Archive: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Archive failed: {e}")
        metrics_errors.labels(category="archive_failed").inc()


# Import MessageType for endpoint
from app.models import MessageType


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=config.PORT, log_level="info")
