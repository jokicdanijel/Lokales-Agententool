#!/usr/bin/env python3
"""
opena8 WhatsApp Agent – WhatsApp Business Cloud API Integration
Port: 12353 | Kürzel: whatsappp
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
from typing import Any, Dict, Optional, List
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
logger = logging.getLogger("opena8")

# ============================================================================
# CONFIG
# ============================================================================

PORT = 12354  # PORTIER 3.0: opena8 = WhatsApp Agent
KUERZEL = "whatsappp"

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
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")

# WhatsApp API
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v18.0")
WHATSAPP_API_BASE = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}"

# Archivp
ARCHIVP_ROOT = os.getenv("ARCHIVP_ROOT", "../1.opena1&2_portier/archivp_store")
ARCHIVP_ROOT = Path(ARCHIVP_ROOT).resolve()

START_TIME = time.time()

# ============================================================================
# SECURITY
# ============================================================================

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    if credentials.credentials != BEARER_TOKEN:
        logger.warning("❌ Unauthorized: Invalid Bearer token")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return True

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify WhatsApp webhook signature"""
    if not META_APP_SECRET:
        logger.warning("⚠️  META_APP_SECRET nicht gesetzt – Signature-Check übersprungen")
        return True
    
    expected = hmac.new(
        META_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)

# ============================================================================
# ARCHIVATOR – SAFEPOINTS
# ============================================================================

def mask_secrets(data: Any) -> Any:
    """Mask secrets in data (recursive)"""
    if isinstance(data, dict):
        return {
            k: "***" if any(s in k.lower() for s in ["token", "password", "secret", "credential"]) else mask_secrets(v)
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
# WHATSAPP CLIENT
# ============================================================================

class WhatsAppClient:
    """WhatsApp Business Cloud API Client"""
    
    def __init__(self):
        self.access_token = META_ACCESS_TOKEN
        self.phone_number_id = META_PHONE_NUMBER_ID
        self.api_base = WHATSAPP_API_BASE
        
    def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message"""
        if not self.access_token:
            raise HTTPException(status_code=500, detail="META_ACCESS_TOKEN not configured in .env")
        
        url = f"{self.api_base}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="WhatsApp API timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ WhatsApp API Error: {e}")
            raise HTTPException(status_code=502, detail=f"WhatsApp API error: {str(e)}")
    
    def send_template_message(self, to: str, template_name: str, language: str, parameters: List[str]) -> Dict[str, Any]:
        """Send template message"""
        if not self.access_token:
            raise HTTPException(status_code=500, detail="META_ACCESS_TOKEN not configured in .env")
        
        url = f"{self.api_base}/{self.phone_number_id}/messages"
        
        # Build components array
        components = []
        if parameters:
            components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in parameters]
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="WhatsApp API timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Template Send Error: {e}")
            if "template" in str(e).lower():
                raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found or not approved")
            raise HTTPException(status_code=502, detail=f"WhatsApp API error: {str(e)}")

whatsapp_client = WhatsAppClient()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SendMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    to: str = Field(..., description="Recipient phone number (E.164 format)")
    text: str = Field(..., description="Message text")

class SendTemplateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    to: str = Field(..., description="Recipient phone number")
    template_name: str = Field(..., description="Template name (approved)")
    language: str = Field(default="de", description="Language code (de, en, etc.)")
    parameters: List[str] = Field(default=[], description="Template parameters")

class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default={}, description="Command parameters")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena8 WhatsApp Agent",
    description="WhatsApp Business Cloud API Integration",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    logger.info("🚀 opena8 (WhatsApp Agent) startet...")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Kürzel: {KUERZEL}")
    logger.info(f"   WhatsApp API: {WHATSAPP_API_BASE}")
    logger.info(f"   Phone Number ID: {META_PHONE_NUMBER_ID[:8]}***" if META_PHONE_NUMBER_ID else "   Phone Number ID: NOT CONFIGURED")
    logger.info(f"   Archiv: {ARCHIVP_ROOT}")
    logger.info("✅ opena8 bereit!")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Agent Info"""
    return {
        "agent": "opena8",
        "kuerzel": KUERZEL,
        "port": PORT,
        "status": "running",
        "capabilities": [
            "send/text",
            "send/template",
            "webhook",
            "conversations"
        ],
        "whatsapp": {
            "api_version": WHATSAPP_API_VERSION,
            "phone_number_id": META_PHONE_NUMBER_ID[:8] + "***" if META_PHONE_NUMBER_ID else "NOT CONFIGURED",
            "access_token_configured": bool(META_ACCESS_TOKEN)
        }
    }

@app.get("/health")
async def health():
    """Health Check"""
    uptime = time.time() - START_TIME
    
    # Check WhatsApp API availability
    whatsapp_status = "unknown"
    if META_ACCESS_TOKEN:
        try:
            # Quick health check (no actual API call, just validate token format)
            if len(META_ACCESS_TOKEN) > 20:
                whatsapp_status = "configured"
            else:
                whatsapp_status = "invalid_token"
        except:
            whatsapp_status = "error"
    else:
        whatsapp_status = "not_configured"
    
    return {
        "status": "ok",
        "agent": "opena8",
        "port": PORT,
        "kuerzel": KUERZEL,
        "uptime": round(uptime, 2),
        "whatsapp_api_version": WHATSAPP_API_VERSION,
        "phone_number_id": META_PHONE_NUMBER_ID[:8] + "***" if META_PHONE_NUMBER_ID else "NOT CONFIGURED",
        "whatsapp_status": whatsapp_status
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
        "agent": "opena8",
        "result": "Command received (use specific endpoints for WhatsApp operations)"
    }
    
    # Safepoint RESP
    write_safepoint("kordp", KUERZEL, "RESP", result, request_id)
    
    return result

@app.post("/send/text")
async def send_text(req: SendMessageRequest, _: bool = Depends(verify_token)):
    """Send WhatsApp Text Message"""
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    logger.info(f"📤 Send text to {req.to}")
    
    # Safepoint CMD
    write_safepoint(KUERZEL, "whatsapp_api", "CMD", {
        "action": "send_text",
        "to": req.to,
        "text": req.text[:100] + "..." if len(req.text) > 100 else req.text
    }, request_id)
    
    # Send message
    try:
        response = whatsapp_client.send_text_message(req.to, req.text)
        
        result = {
            "status": "sent",
            "message_id": response.get("messages", [{}])[0].get("id"),
            "to": req.to,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        # Safepoint RESP
        write_safepoint("whatsapp_api", KUERZEL, "RESP", result, request_id)
        
        return result
        
    except HTTPException as e:
        logger.error(f"❌ Send failed: {e.detail}")
        raise

@app.post("/send/template")
async def send_template(req: SendTemplateRequest, _: bool = Depends(verify_token)):
    """Send WhatsApp Template Message"""
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    logger.info(f"📤 Send template '{req.template_name}' to {req.to}")
    
    # Safepoint CMD
    write_safepoint(KUERZEL, "whatsapp_api", "CMD", {
        "action": "send_template",
        "to": req.to,
        "template_name": req.template_name,
        "language": req.language,
        "parameters": req.parameters
    }, request_id)
    
    # Send template
    try:
        response = whatsapp_client.send_template_message(
            req.to,
            req.template_name,
            req.language,
            req.parameters
        )
        
        result = {
            "status": "sent",
            "message_id": response.get("messages", [{}])[0].get("id"),
            "template_name": req.template_name,
            "to": req.to,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        # Safepoint RESP
        write_safepoint("whatsapp_api", KUERZEL, "RESP", result, request_id)
        
        return result
        
    except HTTPException as e:
        logger.error(f"❌ Template send failed: {e.detail}")
        raise

@app.get("/webhook")
async def webhook_verify(
    hub_mode: str = "",
    hub_challenge: str = "",
    hub_verify_token: str = ""
):
    """WhatsApp Webhook Verification (GET)"""
    logger.info(f"📞 Webhook Verification: mode={hub_mode}, token={hub_verify_token[:5]}***")
    
    if hub_mode == "subscribe" and hub_verify_token == META_VERIFY_TOKEN:
        logger.info("✅ Webhook verified")
        return int(hub_challenge)
    else:
        logger.warning("❌ Webhook verification failed")
        raise HTTPException(status_code=403, detail="Invalid verify token")

@app.post("/webhook")
async def webhook_receive(
    request: Request,
    x_hub_signature: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """WhatsApp Webhook (POST) – Receive Messages"""
    body = await request.body()
    
    # Verify signature
    if x_hub_signature and not verify_webhook_signature(body, x_hub_signature):
        logger.warning("❌ Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:21]
    
    logger.info(f"📥 Webhook received: {len(body)} bytes")
    
    # Safepoint RESP (incoming message)
    write_safepoint("whatsapp_webhook", KUERZEL, "RESP", data, request_id)
    
    # Process messages (extract text, sender, etc.)
    messages = []
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    messages.append({
                        "from": msg.get("from"),
                        "type": msg.get("type"),
                        "text": msg.get("text", {}).get("body", ""),
                        "timestamp": msg.get("timestamp")
                    })
    except Exception as e:
        logger.error(f"❌ Webhook parsing error: {e}")
    
    logger.info(f"📨 Processed {len(messages)} messages")
    
    return {"status": "received", "message_count": len(messages)}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena8 on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
