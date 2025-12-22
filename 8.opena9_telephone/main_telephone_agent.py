#!/usr/bin/env python3
"""
opena9 Telefonie Agent – SIP/Twilio Call Management
Port: 12354 | Kürzel: telphonep
"""

import os
import sys
import logging
import time
import re
import hmac
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict
import requests
import json

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s – %(message)s"
)
logger = logging.getLogger("opena9")

# ============================================================================
# CONFIG
# ============================================================================

PORT = 12355
KUERZEL = "telphonep"

# Port-Policy Enforcement
PORTS_ALLOWED = list(range(12344, 12400))
PORT_FORBIDDEN = [8080]

if PORT not in PORTS_ALLOWED:
    logger.error(f"❌ FATAL: Port {PORT} nicht im erlaubten Bereich {PORTS_ALLOWED[0]}-{PORTS_ALLOWED[-1]}")
    sys.exit(1)

if PORT in PORT_FORBIDDEN:
    logger.error(f"❌ FATAL: Port {PORT} ist verboten (UI-only)")
    sys.exit(1)

logger.info(f"✅ Port-Policy OK: {PORT} in Bereich {PORTS_ALLOWED[0]}-{PORTS_ALLOWED[-1]}")

# ENV-only Secrets
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Twilio API
TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"

# Archivp
ARCHIVP_ROOT = os.getenv("ARCHIVP_ROOT", "../1.opena1&2_portier/archivp_store")
ARCHIVP_ROOT = Path(ARCHIVP_ROOT).resolve()

# Call Timeout
CALL_TIMEOUT = int(os.getenv("CALL_TIMEOUT", "60"))

START_TIME = time.time()

# ============================================================================
# CALL STATE
# ============================================================================

class CallStatus(str, Enum):
    IDLE = "idle"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    FAILED = "failed"
    CANCELED = "canceled"

# In-memory call store (production würde DB verwenden)
active_calls: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# SECURITY
# ============================================================================

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    if credentials.credentials != BEARER_TOKEN:
        logger.warning("❌ Unauthorized: Invalid Bearer token")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return True

def verify_twilio_signature(url: str, params: Dict[str, Any], signature: str) -> bool:
    """Verify Twilio webhook signature"""
    if not TWILIO_AUTH_TOKEN:
        logger.warning("⚠️  TWILIO_AUTH_TOKEN nicht gesetzt – Signature-Check übersprungen")
        return True
    
    # Twilio signature validation
    # https://www.twilio.com/docs/usage/security#validating-requests
    data = url + ''.join([f'{k}{params[k]}' for k in sorted(params.keys())])
    
    expected = hmac.new(
        TWILIO_AUTH_TOKEN.encode(),
        data.encode(),
        hashlib.sha1
    ).digest()
    
    import base64
    expected_b64 = base64.b64encode(expected).decode()
    
    return hmac.compare_digest(expected_b64, signature)

# ============================================================================
# ARCHIVATOR – SAFEPOINTS
# ============================================================================

def mask_secrets(data: Any) -> Any:
    """Mask secrets in data (recursive)"""
    if isinstance(data, dict):
        return {
            k: "***" if any(s in k.lower() for s in ["token", "password", "secret", "credential", "sid", "auth"]) else mask_secrets(v)
            for k, v in data.items()
        }
    elif isinstance(data, str):
        # Mask phone numbers (keep last 4 digits)
        if re.match(r'^\+?\d{10,15}$', data):
            return data[:-4] + "****"
        if len(data) > 500:
            return data[:500] + f"... [truncated {len(data) - 500} chars]"
    elif isinstance(data, list):
        return [mask_secrets(item) for item in data]
    return data

def write_safepoint(src: str, dst: str, typ: str, data: Dict[str, Any], request_id: str) -> None:
    """Write Safepoint (CMD/RESP) to archivp"""
    now = datetime.now(timezone.utc)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    # Unicode-Pfeil → (U+2192)
    filename = f"SP{timestamp}_{src}→{dst}_{typ}.json"
    
    folder = ARCHIVP_ROOT / year / month / day
    folder.mkdir(parents=True, exist_ok=True)
    
    filepath = folder / filename
    
    masked_data = mask_secrets(data)
    
    envelope = {
        "sp_id": timestamp,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "src": src,
        "dst": dst,
        "type": typ,
        "request_id": request_id,
        "data": masked_data
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)
    
    logger.debug(f"📦 Safepoint: {filename}")

# ============================================================================
# TWILIO CLIENT
# ============================================================================

class TwilioClient:
    """Twilio Voice API Client"""
    
    def __init__(self):
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.from_number = TWILIO_PHONE_NUMBER
        self.api_base = TWILIO_API_BASE
        
    def start_call(self, to: str, from_number: Optional[str] = None, timeout: int = 60) -> Dict[str, Any]:
        """Initiate outbound call"""
        if not self.account_sid or not self.auth_token:
            raise HTTPException(status_code=500, detail="TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not configured in .env")
        
        from_num = from_number or self.from_number
        if not from_num:
            raise HTTPException(status_code=500, detail="TWILIO_PHONE_NUMBER not configured")
        
        url = f"{self.api_base}/Accounts/{self.account_sid}/Calls.json"
        
        # TwiML for simple test call (plays message)
        twiml_url = "http://demo.twilio.com/docs/voice.xml"
        
        payload = {
            "To": to,
            "From": from_num,
            "Url": twiml_url,
            "Timeout": timeout
        }
        
        try:
            response = requests.post(
                url,
                data=payload,
                auth=(self.account_sid, self.auth_token),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Twilio API timeout")
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Twilio Call Error: {e}")
            if e.response.status_code == 400:
                raise HTTPException(status_code=400, detail="Invalid phone number format")
            elif e.response.status_code == 402:
                raise HTTPException(status_code=402, detail="Insufficient Twilio balance")
            raise HTTPException(status_code=502, detail=f"Twilio API error: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Twilio Request Error: {e}")
            raise HTTPException(status_code=502, detail=f"Twilio API error: {str(e)}")
    
    def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """Get call status from Twilio"""
        if not self.account_sid or not self.auth_token:
            raise HTTPException(status_code=500, detail="Twilio credentials not configured")
        
        url = f"{self.api_base}/Accounts/{self.account_sid}/Calls/{call_sid}.json"
        
        try:
            response = requests.get(
                url,
                auth=(self.account_sid, self.auth_token),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Call {call_sid} not found")
            raise HTTPException(status_code=502, detail="Twilio API error")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Twilio API error: {str(e)}")
    
    def hangup_call(self, call_sid: str) -> Dict[str, Any]:
        """Hangup active call"""
        if not self.account_sid or not self.auth_token:
            raise HTTPException(status_code=500, detail="Twilio credentials not configured")
        
        url = f"{self.api_base}/Accounts/{self.account_sid}/Calls/{call_sid}.json"
        
        try:
            response = requests.post(
                url,
                data={"Status": "completed"},
                auth=(self.account_sid, self.auth_token),
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Call {call_sid} not found")
            raise HTTPException(status_code=502, detail="Twilio API error")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Twilio API error: {str(e)}")

twilio_client = TwilioClient()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CallStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    to: str = Field(..., description="Destination phone number (E.164 format)")
    from_number: Optional[str] = Field(None, description="Caller ID (optional, uses default)")
    timeout: int = Field(default=60, description="Ring timeout in seconds")

class CallHangupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    call_id: str = Field(..., description="Call SID to hangup")

class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default={}, description="Command parameters")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena9 Telefonie Agent",
    description="SIP/Twilio Call Management",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    logger.info("🚀 opena9 (Telefonie Agent) startet...")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Kürzel: {KUERZEL}")
    logger.info(f"   Twilio Account SID: {TWILIO_ACCOUNT_SID[:8]}***" if TWILIO_ACCOUNT_SID else "   Twilio Account SID: NOT CONFIGURED")
    logger.info(f"   Twilio Phone: {TWILIO_PHONE_NUMBER}" if TWILIO_PHONE_NUMBER else "   Twilio Phone: NOT CONFIGURED")
    logger.info(f"   Call Timeout: {CALL_TIMEOUT}s")
    logger.info(f"   Archiv: {ARCHIVP_ROOT}")
    logger.info("✅ opena9 bereit!")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Agent Info"""
    return {
        "agent": "opena9",
        "kuerzel": KUERZEL,
        "port": PORT,
        "status": "running",
        "capabilities": [
            "call/start",
            "call/hangup",
            "call/status",
            "webhook/status"
        ],
        "telephony": {
            "provider": "twilio",
            "account_sid": TWILIO_ACCOUNT_SID[:8] + "***" if TWILIO_ACCOUNT_SID else "NOT CONFIGURED",
            "from_number": TWILIO_PHONE_NUMBER if TWILIO_PHONE_NUMBER else "NOT CONFIGURED",
            "credentials_configured": bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)
        }
    }

@app.get("/health")
async def health():
    """Health Check"""
    uptime = time.time() - START_TIME
    
    # Check Twilio availability
    twilio_status = "unknown"
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        twilio_status = "configured"
    else:
        twilio_status = "not_configured"
    
    return {
        "status": "ok",
        "agent": "opena9",
        "port": PORT,
        "kuerzel": KUERZEL,
        "uptime": round(uptime, 2),
        "active_calls": len(active_calls),
        "twilio_status": twilio_status,
        "call_timeout": CALL_TIMEOUT
    }

@app.post("/command")
async def command(req: CommandRequest, _: bool = Depends(verify_token)):
    """Generic Command Endpoint (Option-2-Flow Compatibility)"""
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    logger.info(f"📥 Command: {req.command}")
    
    # Safepoint CMD
    write_safepoint(KUERZEL, "kordp", "CMD", {
        "command": req.command,
        "params": req.params
    }, request_id)
    
    result = {
        "status": "executed",
        "command": req.command,
        "agent": "opena9",
        "result": "Command received (use specific endpoints for telephony operations)"
    }
    
    # Safepoint RESP
    write_safepoint("kordp", KUERZEL, "RESP", result, request_id)
    
    return result

@app.post("/call/start")
async def call_start(req: CallStartRequest, _: bool = Depends(verify_token)):
    """Start Outbound Call"""
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    logger.info(f"📞 Start call to {req.to}")
    
    # Validate phone number format (basic E.164)
    if not re.match(r'^\+?[1-9]\d{1,14}$', req.to):
        raise HTTPException(status_code=400, detail="Invalid phone number format (use E.164: +1234567890)")
    
    # Safepoint CMD
    write_safepoint(KUERZEL, "twilio_api", "CMD", {
        "action": "call_start",
        "to": req.to,
        "from": req.from_number or TWILIO_PHONE_NUMBER,
        "timeout": req.timeout
    }, request_id)
    
    # Start call
    try:
        response = twilio_client.start_call(req.to, req.from_number, req.timeout)
        
        call_sid = response.get("sid")
        call_status = response.get("status")
        
        # Store in memory
        active_calls[call_sid] = {
            "to": req.to,
            "from": req.from_number or TWILIO_PHONE_NUMBER,
            "status": call_status,
            "start_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        result = {
            "status": "initiated",
            "call_id": call_sid,
            "to": req.to,
            "from": req.from_number or TWILIO_PHONE_NUMBER,
            "call_status": call_status,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        # Safepoint RESP
        write_safepoint("twilio_api", KUERZEL, "RESP", result, request_id)
        
        return result
        
    except HTTPException as e:
        logger.error(f"❌ Call start failed: {e.detail}")
        raise

@app.post("/call/hangup")
async def call_hangup(req: CallHangupRequest, _: bool = Depends(verify_token)):
    """Hangup Active Call"""
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    logger.info(f"📴 Hangup call {req.call_id}")
    
    # Safepoint CMD
    write_safepoint(KUERZEL, "twilio_api", "CMD", {
        "action": "call_hangup",
        "call_id": req.call_id
    }, request_id)
    
    # Hangup call
    try:
        response = twilio_client.hangup_call(req.call_id)
        
        # Update status
        if req.call_id in active_calls:
            active_calls[req.call_id]["status"] = "completed"
            active_calls[req.call_id]["end_time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        result = {
            "status": "hangup",
            "call_id": req.call_id,
            "call_status": response.get("status"),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        # Safepoint RESP
        write_safepoint("twilio_api", KUERZEL, "RESP", result, request_id)
        
        return result
        
    except HTTPException as e:
        logger.error(f"❌ Hangup failed: {e.detail}")
        raise

@app.get("/call/status/{call_id}")
async def call_status(call_id: str, _: bool = Depends(verify_token)):
    """Get Call Status"""
    logger.info(f"📊 Status for call {call_id}")
    
    # Check local cache first
    if call_id in active_calls:
        return {
            "call_id": call_id,
            **active_calls[call_id]
        }
    
    # Query Twilio
    try:
        response = twilio_client.get_call_status(call_id)
        
        return {
            "call_id": call_id,
            "status": response.get("status"),
            "duration": response.get("duration"),
            "to": response.get("to"),
            "from": response.get("from"),
            "direction": response.get("direction")
        }
    except HTTPException as e:
        logger.error(f"❌ Status query failed: {e.detail}")
        raise

@app.post("/webhook/status")
async def webhook_status(
    request: Request,
    x_twilio_signature: Optional[str] = Header(None, alias="X-Twilio-Signature")
):
    """Twilio Status Callback Webhook"""
    form_data = await request.form()
    data = dict(form_data)
    
    # Verify signature (optional, nur wenn konfiguriert)
    # url = str(request.url)
    # if x_twilio_signature and not verify_twilio_signature(url, data, x_twilio_signature):
    #     logger.warning("❌ Invalid Twilio signature")
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    call_sid = data.get("CallSid")
    call_status = data.get("CallStatus")
    
    logger.info(f"📥 Webhook: Call {call_sid} → {call_status}")
    
    # Safepoint RESP (incoming webhook)
    write_safepoint("twilio_webhook", KUERZEL, "RESP", {
        "call_sid": call_sid,
        "status": call_status,
        "duration": data.get("CallDuration"),
        "from": data.get("From"),
        "to": data.get("To")
    }, request_id)
    
    # Update local cache
    if call_sid in active_calls:
        active_calls[call_sid]["status"] = call_status
        if call_status in ["completed", "failed", "busy", "no-answer"]:
            active_calls[call_sid]["end_time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena9 on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
