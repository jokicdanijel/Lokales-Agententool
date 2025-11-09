"""
opena8_Telephone: Telephone/VoIP Integration Agent
SIP-based call routing and management
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import json
import urllib.request
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os
import sys
import uuid
import random

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena8_Telephone",
    version="1.0.0",
    description="Telephone/VoIP Integration Agent"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12356
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# SIP Configuration
SIP_SERVER = os.getenv("SIP_SERVER", "sip.provider.com")
SIP_USER = os.getenv("SIP_USER", "user@domain.com")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "sip_password")

# In-memory call tracking
_active_calls: Dict[str, dict] = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class CallMakeRequest(BaseModel):
    to_number: str
    caller_id: str = "Unknown"
    timeout_sec: int = 30


class CallHangupRequest(BaseModel):
    call_id: str


class DTMFSendRequest(BaseModel):
    call_id: str
    digits: str


class RecordingListRequest(BaseModel):
    limit: int = 10


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: Optional[str]):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict):
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena8_telephone",
            "dst": "opena2",
            "kind": "CALL_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"}
        }
        
        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_call_id() -> str:
    """Generate unique call ID"""
    return f"CALL_{uuid.uuid4().hex[:12].upper()}"


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena8_Telephone",
        "port": PORT,
        "sip_server": SIP_SERVER,
        "active_calls": len(_active_calls),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/call/make")
async def make_call(req: CallMakeRequest, authorization: str = Header(None)):
    """Initiate outgoing call"""
    _validate_token(authorization)
    
    try:
        call_id = _generate_call_id()
        
        # Simulate call initiation
        _active_calls[call_id] = {
            "to": req.to_number,
            "caller_id": req.caller_id,
            "status": "ringing",
            "start_time": datetime.utcnow(),
            "duration_sec": 0
        }
        
        logger.info(f"☎️ Call initiated: {call_id} → {req.to_number}")
        
        await _archive({
            "op": "CALL_MAKE",
            "call_id": call_id,
            "to_number": req.to_number,
            "caller_id": req.caller_id
        })
        
        return {
            "strict": True,
            "call_id": call_id,
            "to": req.to_number,
            "status": "ringing",
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/call/hangup")
async def hangup_call(req: CallHangupRequest, authorization: str = Header(None)):
    """Hangup/terminate call"""
    _validate_token(authorization)
    
    try:
        if req.call_id not in _active_calls:
            raise HTTPException(status_code=404, detail=f"Call {req.call_id} not found")
        
        call_info = _active_calls.pop(req.call_id)
        duration = (datetime.utcnow() - call_info["start_time"]).total_seconds()
        
        logger.info(f"☎️ Call hangup: {req.call_id} (Duration: {duration:.0f}s)")
        
        await _archive({
            "op": "CALL_HANGUP",
            "call_id": req.call_id,
            "duration_sec": duration,
            "to": call_info["to"]
        })
        
        return {
            "strict": True,
            "call_id": req.call_id,
            "duration_sec": duration,
            "status": "terminated",
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Hangup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dtmf/send")
async def send_dtmf(req: DTMFSendRequest, authorization: str = Header(None)):
    """Send DTMF tones (keypad digits)"""
    _validate_token(authorization)
    
    try:
        if req.call_id not in _active_calls:
            raise HTTPException(status_code=404, detail=f"Call {req.call_id} not found")
        
        # Validate DTMF format (0-9, *, #)
        if not all(c in "0123456789*#" for c in req.digits):
            raise ValueError("Invalid DTMF digits")
        
        logger.info(f"📞 DTMF sent: {req.call_id} → {req.digits}")
        
        await _archive({
            "op": "DTMF_SEND",
            "call_id": req.call_id,
            "digits": req.digits
        })
        
        return {
            "strict": True,
            "call_id": req.call_id,
            "digits": req.digits,
            "status": "sent",
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ DTMF send failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recordings")
async def list_recordings(authorization: str = Header(None)):
    """List available recordings"""
    _validate_token(authorization)
    
    try:
        # Simulate recordings
        recordings = [
            {
                "id": f"REC_{i}",
                "date": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "duration_sec": random.randint(30, 600),
                "phone": f"+49{300+i}xxxxx"
            }
            for i in range(5)
        ]
        
        logger.info(f"📁 Listing {len(recordings)} recordings")
        
        await _archive({
            "op": "LIST_RECORDINGS",
            "count": len(recordings)
        })
        
        return {
            "strict": True,
            "recordings": recordings,
            "count": len(recordings),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ List failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calls/active")
async def active_calls(authorization: str = Header(None)):
    """Get currently active calls"""
    _validate_token(authorization)
    
    return {
        "strict": True,
        "active_calls": len(_active_calls),
        "calls": [
            {
                "call_id": cid,
                "to": info["to"],
                "status": info["status"],
                "duration_sec": (datetime.utcnow() - info["start_time"]).total_seconds()
            }
            for cid, info in _active_calls.items()
        ],
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena8_Telephone",
        "version": "1.0.0",
        "port": PORT,
        "sip_server": SIP_SERVER,
        "active_calls": len(_active_calls),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena8_Telephone on port {PORT}")
    logger.info(f"SIP Server: {SIP_SERVER}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
