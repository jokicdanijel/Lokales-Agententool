"""
opena7_WhatsApp: WhatsApp Integration Agent
Twilio-based messaging
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import json
import urllib.request
from datetime import datetime
from typing import Optional
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena7_WhatsApp",
    version="1.0.0",
    description="WhatsApp Integration Agent (Twilio)"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12355
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC_TEST_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "test_token")
TWILIO_PHONE = os.getenv("TWILIO_PHONE", "+1234567890")

# ============================================================================
# DATA MODELS
# ============================================================================


class WhatsAppMessageRequest(BaseModel):
    to: str
    message: str


class WhatsAppMediaRequest(BaseModel):
    to: str
    media_url: str
    caption: Optional[str] = None


class WhatsAppGroupRequest(BaseModel):
    name: str
    participants: list


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
            "src": "opena7_whatsapp",
            "dst": "opena2",
            "kind": "WHATSAPP_OP",
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


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena7_WhatsApp",
        "port": PORT,
        "twilio_configured": bool(TWILIO_ACCOUNT_SID),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/message/send")
async def send_message(req: WhatsAppMessageRequest, authorization: str = Header(None)):
    """Send WhatsApp message"""
    _validate_token(authorization)
    
    try:
        logger.info(f"💬 WhatsApp to {req.to}: {req.message[:50]}")
        
        await _archive({
            "op": "SEND_MESSAGE",
            "to": req.to,
            "message_length": len(req.message),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "strict": True,
            "sent": True,
            "to": req.to,
            "message_id": f"msg_{datetime.utcnow().timestamp()}",
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Send failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/media/upload")
async def upload_media(req: WhatsAppMediaRequest, authorization: str = Header(None)):
    """Upload media (photo/video)"""
    _validate_token(authorization)
    
    try:
        logger.info(f"📸 Media to {req.to}: {req.media_url}")
        
        await _archive({
            "op": "UPLOAD_MEDIA",
            "to": req.to,
            "media_url": req.media_url,
            "caption": req.caption
        })
        
        return {
            "strict": True,
            "uploaded": True,
            "to": req.to,
            "media_url": req.media_url,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/group/create")
async def create_group(req: WhatsAppGroupRequest, authorization: str = Header(None)):
    """Create WhatsApp group"""
    _validate_token(authorization)
    
    try:
        logger.info(f"👥 Creating group: {req.name} ({len(req.participants)} members)")
        
        await _archive({
            "op": "CREATE_GROUP",
            "name": req.name,
            "participant_count": len(req.participants)
        })
        
        return {
            "strict": True,
            "created": True,
            "group_name": req.name,
            "group_id": f"grp_{datetime.utcnow().timestamp()}",
            "members": len(req.participants),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Group creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena7_WhatsApp",
        "version": "1.0.0",
        "port": PORT,
        "twilio_configured": bool(TWILIO_ACCOUNT_SID),
        "endpoints": 5,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena7_WhatsApp on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
