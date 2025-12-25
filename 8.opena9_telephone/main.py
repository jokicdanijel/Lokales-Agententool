#!/usr/bin/env python3
"""
opena9 Telephone Agent - VoIP/SIP Integration
Port: 12352 | Service: Voice Calls & VoIP
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import lokale Module
from app.config import config
from app.models import CallDirection, CallRecord, CallStatus
from app.sip_client import CallManager, SIPClient

# Logging Konfiguration
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("opena9")

# FastAPI App
app = FastAPI(title="opena9 Telephone Agent", description="VoIP/SIP Integration für Telefonie", version="1.0.0")

# SIP Client & Call Manager
sip_client = SIPClient()
call_manager = CallManager()


# Pydantic Models für API
class MakeCallRequest(BaseModel):
    """Anruf tätigen Request"""

    to_number: str
    caller_id: str | None = None
    duration_limit: int | None = 300  # 5 Minuten default


class CallControlRequest(BaseModel):
    """Anruf Kontrolle Request"""

    call_id: str
    action: str  # hold, unhold, transfer, hangup


class TransferCallRequest(BaseModel):
    """Anruf weiterleiten Request"""

    call_id: str
    target_number: str


# Call Storage (temporär)
active_calls: dict[str, CallRecord] = {}
call_history: list[dict[str, Any]] = []


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "opena9",
        "component": "telephone",
        "port": config.PORT,
        "sip_status": await sip_client.get_status(),
        "active_calls": len(active_calls),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/make-call")
async def make_call(request: MakeCallRequest):
    """Ausgehenden Anruf tätigen"""
    try:
        call_id = await call_manager.initiate_call(
            to_number=request.to_number,
            caller_id=request.caller_id or config.DEFAULT_CALLER_ID,
            duration_limit=request.duration_limit,
        )

        if call_id:
            return {
                "status": "initiated",
                "call_id": call_id,
                "to_number": request.to_number,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=400, detail="Call initiation failed")

    except Exception as e:
        logger.error(f"Make call error: {e}")
        raise HTTPException(status_code=500, detail=f"Call failed: {e!s}")


@app.post("/api/answer-call")
async def answer_call(call_id: str):
    """Eingehenden Anruf annehmen"""
    try:
        success = await call_manager.answer_call(call_id)

        if success:
            return {"status": "answered", "call_id": call_id, "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=400, detail="Failed to answer call")

    except Exception as e:
        logger.error(f"Answer call error: {e}")
        raise HTTPException(status_code=500, detail=f"Answer failed: {e!s}")


@app.post("/api/hangup-call")
async def hangup_call(call_id: str):
    """Anruf beenden"""
    try:
        success = await call_manager.hangup_call(call_id)

        if success:
            # Move to history
            if call_id in active_calls:
                call_record = active_calls.pop(call_id)
                call_history.append(
                    {
                        "call_id": call_id,
                        "from_number": call_record.from_number,
                        "to_number": call_record.to_number,
                        "direction": call_record.direction.value,
                        "status": "completed",
                        "started_at": call_record.started_at.isoformat(),
                        "ended_at": datetime.now().isoformat(),
                        "duration": (datetime.now() - call_record.started_at).total_seconds(),
                    }
                )

            return {"status": "hungup", "call_id": call_id, "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=400, detail="Failed to hangup call")

    except Exception as e:
        logger.error(f"Hangup call error: {e}")
        raise HTTPException(status_code=500, detail=f"Hangup failed: {e!s}")


@app.post("/api/control-call")
async def control_call(request: CallControlRequest):
    """Anruf kontrollieren (hold, unhold, etc.)"""
    try:
        success = await call_manager.control_call(request.call_id, request.action)

        if success:
            return {
                "status": f"{request.action}_success",
                "call_id": request.call_id,
                "action": request.action,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to {request.action} call")

    except Exception as e:
        logger.error(f"Control call error: {e}")
        raise HTTPException(status_code=500, detail=f"Control failed: {e!s}")


@app.post("/api/transfer-call")
async def transfer_call(request: TransferCallRequest):
    """Anruf weiterleiten"""
    try:
        success = await call_manager.transfer_call(request.call_id, request.target_number)

        if success:
            return {
                "status": "transferred",
                "call_id": request.call_id,
                "target_number": request.target_number,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to transfer call")

    except Exception as e:
        logger.error(f"Transfer call error: {e}")
        raise HTTPException(status_code=500, detail=f"Transfer failed: {e!s}")


@app.get("/api/active-calls")
async def get_active_calls():
    """Aktive Anrufe abrufen"""
    calls = []
    for call_id, call_record in active_calls.items():
        calls.append(
            {
                "call_id": call_id,
                "from_number": call_record.from_number,
                "to_number": call_record.to_number,
                "direction": call_record.direction.value,
                "status": call_record.status.value,
                "started_at": call_record.started_at.isoformat(),
                "duration": (datetime.now() - call_record.started_at).total_seconds(),
            }
        )

    return {"total_active": len(calls), "calls": calls}


@app.get("/api/call-history")
async def get_call_history(limit: int = 50):
    """Anrufhistorie abrufen"""
    return {"total": len(call_history), "calls": call_history[-limit:] if call_history else []}


@app.get("/api/stats")
async def get_stats():
    """Telefonie-Statistiken"""
    total_calls = len(call_history)
    active_count = len(active_calls)

    # Analyse der letzten 24 Stunden
    now = datetime.now()
    day_ago = now - timedelta(days=1)

    recent_calls = [
        call for call in call_history if datetime.fromisoformat(call.get("started_at", "2000-01-01")) > day_ago
    ]

    # Richtungsverteilung
    inbound_calls = sum(1 for call in recent_calls if call.get("direction") == "inbound")
    outbound_calls = sum(1 for call in recent_calls if call.get("direction") == "outbound")

    # Durchschnittliche Gesprächsdauer
    durations = [call.get("duration", 0) for call in recent_calls if call.get("duration")]
    avg_duration = sum(durations) / len(durations) if durations else 0

    return {
        "total_calls": total_calls,
        "active_calls": active_count,
        "recent_24h": len(recent_calls),
        "inbound_24h": inbound_calls,
        "outbound_24h": outbound_calls,
        "avg_duration_seconds": round(avg_duration, 2),
        "sip_status": await sip_client.get_status(),
    }


@app.post("/webhook/call-event")
async def call_event_webhook(request: Request):
    """Webhook für Anruf-Events vom SIP-Provider"""
    try:
        event_data = await request.json()
        logger.info(f"📞 Call event received: {event_data}")

        event_type = event_data.get("event_type")
        call_id = event_data.get("call_id")

        if event_type == "incoming_call":
            await handle_incoming_call(event_data)
        elif event_type == "call_answered":
            await handle_call_answered(event_data)
        elif event_type == "call_ended":
            await handle_call_ended(event_data)
        elif event_type == "call_failed":
            await handle_call_failed(event_data)

        return JSONResponse(content={"status": "processed"})

    except Exception as e:
        logger.error(f"Call event webhook error: {e}")
        raise HTTPException(status_code=400, detail="Event processing failed")


async def handle_incoming_call(event_data: dict[str, Any]):
    """Eingehenden Anruf verarbeiten"""
    call_id = event_data.get("call_id")
    from_number = event_data.get("from_number")
    to_number = event_data.get("to_number")

    call_record = CallRecord(
        call_id=call_id,
        from_number=from_number,
        to_number=to_number,
        direction=CallDirection.INBOUND,
        status=CallStatus.RINGING,
        started_at=datetime.now(),
    )

    active_calls[call_id] = call_record

    # Auto-Answer falls konfiguriert
    if config.AUTO_ANSWER_ENABLED:
        await asyncio.sleep(config.AUTO_ANSWER_DELAY)
        await call_manager.answer_call(call_id)

    logger.info(f"📞 Incoming call: {from_number} → {to_number} (ID: {call_id})")


async def handle_call_answered(event_data: dict[str, Any]):
    """Anruf angenommen verarbeiten"""
    call_id = event_data.get("call_id")

    if call_id in active_calls:
        active_calls[call_id].status = CallStatus.ACTIVE
        logger.info(f"✅ Call answered: {call_id}")


async def handle_call_ended(event_data: dict[str, Any]):
    """Anruf beendet verarbeiten"""
    call_id = event_data.get("call_id")

    if call_id in active_calls:
        call_record = active_calls.pop(call_id)

        # Zu Historie hinzufügen
        call_history.append(
            {
                "call_id": call_id,
                "from_number": call_record.from_number,
                "to_number": call_record.to_number,
                "direction": call_record.direction.value,
                "status": "completed",
                "started_at": call_record.started_at.isoformat(),
                "ended_at": datetime.now().isoformat(),
                "duration": (datetime.now() - call_record.started_at).total_seconds(),
            }
        )

        # Archive zu opena2 falls konfiguriert
        if config.OPENA2_URL:
            await archive_call(call_history[-1])

        logger.info(f"📴 Call ended: {call_id}")


async def handle_call_failed(event_data: dict[str, Any]):
    """Fehlgeschlagenen Anruf verarbeiten"""
    call_id = event_data.get("call_id")
    error_reason = event_data.get("reason", "unknown")

    if call_id in active_calls:
        call_record = active_calls.pop(call_id)

        # Als fehlgeschlagen archivieren
        call_history.append(
            {
                "call_id": call_id,
                "from_number": call_record.from_number,
                "to_number": call_record.to_number,
                "direction": call_record.direction.value,
                "status": "failed",
                "error_reason": error_reason,
                "started_at": call_record.started_at.isoformat(),
                "ended_at": datetime.now().isoformat(),
                "duration": 0,
            }
        )

        logger.error(f"❌ Call failed: {call_id} - {error_reason}")


async def archive_call(call_data: dict[str, Any]):
    """Anruf zu opena2 archivieren"""
    try:
        import httpx

        archive_data = {
            "tool_name": "opena9_telephone",
            "input_data": {
                "call_id": call_data["call_id"],
                "from_number": call_data["from_number"],
                "to_number": call_data["to_number"],
                "direction": call_data["direction"],
            },
            "output_data": {
                "status": call_data["status"],
                "duration": call_data["duration"],
                "ended_at": call_data["ended_at"],
            },
            "metadata": {"started_at": call_data["started_at"], "call_type": "voice"},
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(f"{config.OPENA2_URL}/archiv/store", json=archive_data)

            if response.status_code == 200:
                logger.info(f"📁 Call {call_data['call_id']} archived")
            else:
                logger.error(f"❌ Call archive failed: {response.status_code}")

    except Exception as e:
        logger.error(f"Archive error: {e}")


if __name__ == "__main__":
    logger.info(f"🚀 Starting opena9 Telephone Agent on port {config.PORT}")
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, log_level=config.LOG_LEVEL.lower())
