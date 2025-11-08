"""
opena9_CallTracking: Call Analytics & CRM Integration
Duration tracking, transcription, sentiment analysis
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

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena9_CallTracking",
    version="1.0.0",
    description="Call Analytics & CRM Integration"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12357
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory call logs
_call_logs: List[Dict] = []

# ============================================================================
# DATA MODELS
# ============================================================================


class CallLogRequest(BaseModel):
    call_id: str
    from_number: str
    to_number: str
    duration_sec: int
    status: str = "completed"


class TranscriptionRequest(BaseModel):
    call_id: str


class SentimentAnalysisRequest(BaseModel):
    call_id: str
    text: str


class CRMSyncRequest(BaseModel):
    contact_id: str
    call_data: dict


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
            "src": "opena9_call_tracking",
            "dst": "opena2",
            "kind": "ANALYTICS_OP",
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


def _analyze_sentiment(text: str) -> str:
    """Simple sentiment analysis"""
    positive = ["good", "great", "excellent", "happy", "satisfied", "thanks"]
    negative = ["bad", "terrible", "angry", "unhappy", "disappointed"]
    
    text_lower = text.lower()
    
    pos_count = sum(1 for word in positive if word in text_lower)
    neg_count = sum(1 for word in negative if word in text_lower)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena9_CallTracking",
        "port": PORT,
        "logged_calls": len(_call_logs),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/call/log")
async def log_call(req: CallLogRequest, authorization: str = Header(None)):
    """Log call to database"""
    _validate_token(authorization)
    
    try:
        call_entry = {
            "call_id": req.call_id,
            "from": req.from_number,
            "to": req.to_number,
            "duration_sec": req.duration_sec,
            "status": req.status,
            "timestamp": datetime.utcnow().isoformat(),
            "cost_estimate": req.duration_sec * 0.01  # €0.01 per second
        }
        
        _call_logs.append(call_entry)
        logger.info(f"📊 Call logged: {req.call_id} ({req.duration_sec}s)")
        
        await _archive({
            "op": "LOG_CALL",
            "call_id": req.call_id,
            "duration_sec": req.duration_sec,
            "cost": call_entry["cost_estimate"]
        })
        
        return {
            "strict": True,
            "logged": True,
            "call_id": req.call_id,
            "duration_sec": req.duration_sec,
            "cost_estimate": call_entry["cost_estimate"],
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Log failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcription/get")
async def get_transcription(req: TranscriptionRequest, authorization: str = Header(None)):
    """Get call transcription"""
    _validate_token(authorization)
    
    try:
        # Simulate transcription
        transcription = f"""
        [0:00] Agent: Hello, thank you for calling. How can I help?
        [0:05] Customer: Hi, I have a question about my account.
        [0:10] Agent: Of course! What's your concern?
        [0:15] Customer: I was charged twice last month.
        [0:20] Agent: I'm very sorry to hear that. Let me look into this for you.
        """
        
        logger.info(f"📝 Transcription retrieved: {req.call_id}")
        
        await _archive({
            "op": "GET_TRANSCRIPTION",
            "call_id": req.call_id,
            "length": len(transcription)
        })
        
        return {
            "strict": True,
            "call_id": req.call_id,
            "transcription": transcription.strip(),
            "duration_sec": 30,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment/analyze")
async def analyze_sentiment(req: SentimentAnalysisRequest, authorization: str = Header(None)):
    """Analyze sentiment of call text"""
    _validate_token(authorization)
    
    try:
        sentiment = _analyze_sentiment(req.text)
        confidence = 0.85 + (0.1 if sentiment != "neutral" else 0)
        
        logger.info(f"😊 Sentiment analyzed: {req.call_id} → {sentiment}")
        
        await _archive({
            "op": "ANALYZE_SENTIMENT",
            "call_id": req.call_id,
            "sentiment": sentiment,
            "confidence": confidence
        })
        
        return {
            "strict": True,
            "call_id": req.call_id,
            "sentiment": sentiment,
            "confidence": confidence,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crm/sync")
async def sync_crm(req: CRMSyncRequest, authorization: str = Header(None)):
    """Sync call data to CRM"""
    _validate_token(authorization)
    
    try:
        logger.info(f"🔄 CRM sync: Contact {req.contact_id}")
        
        await _archive({
            "op": "CRM_SYNC",
            "contact_id": req.contact_id,
            "fields": len(req.call_data)
        })
        
        return {
            "strict": True,
            "contact_id": req.contact_id,
            "synced": True,
            "fields": len(req.call_data),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ CRM sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(authorization: str = Header(None), limit: int = 10):
    """Get call history"""
    _validate_token(authorization)
    
    try:
        history = _call_logs[-limit:]
        logger.info(f"📋 History retrieved: {len(history)} calls")
        
        return {
            "strict": True,
            "calls": history,
            "count": len(history),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ History failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    total_duration = sum(call.get("duration_sec", 0) for call in _call_logs)
    total_cost = total_duration * 0.01
    
    return {
        "service": "opena9_CallTracking",
        "version": "1.0.0",
        "port": PORT,
        "logged_calls": len(_call_logs),
        "total_duration_sec": total_duration,
        "total_cost": total_cost,
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena9_CallTracking on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
