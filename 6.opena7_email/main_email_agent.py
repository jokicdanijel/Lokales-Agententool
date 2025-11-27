#!/usr/bin/env python3
"""
opena7 – E-Mail Client Agent (IMAP/SMTP)
Port: 12352 | Kürzel: emailp
Compliance: PORTIER 3.0 (Option-2-Flow, Strict JSON, ENV-only Secrets)
"""

import os
import sys
import json
import logging
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

# IMAP/SMTP Imports (mit Fallback)
try:
    import imaplib
    import smtplib
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# ============================================================================
# KONFIGURATION (ENV-only, niemals hardcoded)
# ============================================================================

PORT = int(os.getenv("OPENA7_PORT", "12352"))
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
ARCHIVP_ROOT = Path(os.getenv("ARCHIVP_ROOT", "../1.opena1&2_portier/archivp_store"))

# IMAP/SMTP Config
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.example.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USE_SSL = os.getenv("IMAP_USE_SSL", "true").lower() == "true"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "agent@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
DEFAULT_FOLDER = os.getenv("DEFAULT_FOLDER", "INBOX")
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "50"))

# Port-Policy (PORTIER 3.0 Standard)
PORTS_ALLOWED = list(range(12344, 12400))
PORT_FORBIDDEN = [8080]

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[
        logging.FileHandler("logs/opena7.nohup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("opena7")

# ============================================================================
# PORT-POLICY ENFORCEMENT (Startup)
# ============================================================================

if PORT not in PORTS_ALLOWED:
    logger.error(f"❌ FATAL: Port {PORT} nicht im erlaubten Bereich {PORTS_ALLOWED[0]}-{PORTS_ALLOWED[-1]}")
    sys.exit(1)

if PORT in PORT_FORBIDDEN:
    logger.error(f"❌ FATAL: Port {PORT} ist für Backend verboten (nur UI)!")
    sys.exit(1)

logger.info(f"✅ Port-Policy OK: {PORT} in Bereich {PORTS_ALLOWED[0]}-{PORTS_ALLOWED[-1]}")

# ============================================================================
# BEARER TOKEN VALIDATION
# ============================================================================

if not BEARER_TOKEN:
    logger.error("❌ FATAL: BEARER_TOKEN nicht gesetzt in .env")
    sys.exit(1)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Bearer token"
        )
    return True

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena7 – E-Mail Client Agent",
    description="IMAP/SMTP E-Mail integration (PORTIER 3.0)",
    version="1.0.0"
)

# ============================================================================
# STARTUP
# ============================================================================

START_TIME = time.time()
ARCHIVP_ROOT.mkdir(parents=True, exist_ok=True)

logger.info("🚀 opena7 (E-Mail Agent) startet...")
logger.info(f"   Port: {PORT}")
logger.info(f"   IMAP: {IMAP_SERVER}:{IMAP_PORT} (SSL: {IMAP_USE_SSL})")
logger.info(f"   SMTP: {SMTP_SERVER}:{SMTP_PORT} (TLS: {SMTP_USE_TLS})")
logger.info(f"   E-Mail: {EMAIL_ADDRESS}")
logger.info(f"   Archiv: {ARCHIVP_ROOT.absolute()}")
logger.info(f"   Email-Libraries: {'✅ Available' if EMAIL_AVAILABLE else '❌ Not available'}")

# ============================================================================
# PYDANTIC SCHEMAS (Strict JSON)
# ============================================================================

class InboxListRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    folder: str = Field(DEFAULT_FOLDER, description="IMAP folder name")
    limit: int = Field(MAX_MESSAGES, description="Max messages to retrieve")
    offset: int = Field(0, description="Offset for pagination")
    search_criteria: Optional[str] = Field(None, description="IMAP search criteria (e.g., 'UNSEEN')")

class MessageGetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message_id: str = Field(..., description="Message UID or ID")
    folder: str = Field(DEFAULT_FOLDER, description="IMAP folder")
    include_body: bool = Field(True, description="Include message body")

class MessageSendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    to: List[str] = Field(..., description="Recipient email addresses")
    cc: Optional[List[str]] = Field(None, description="CC recipients")
    bcc: Optional[List[str]] = Field(None, description="BCC recipients")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (plain text)")
    html_body: Optional[str] = Field(None, description="Email body (HTML)")

class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(..., description="Search query (IMAP search string)")
    folder: str = Field(DEFAULT_FOLDER, description="Folder to search")
    date_from: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: str = Field(..., description="Command to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")

# ============================================================================
# SAFEPOINT SYSTEM (PORTIER 3.0)
# ============================================================================

def mask_secrets(data: Any) -> Any:
    """Maskiert Secrets in Daten (Bearer-Token, Passwords, SMTP-Credentials)"""
    if isinstance(data, dict):
        return {
            k: "***" if any(s in k.lower() for s in ["token", "password", "secret", "key", "bearer", "auth", "credential"])
            else mask_secrets(v)
            for k, v in data.items()
        }
    elif isinstance(data, str):
        # Kürze lange E-Mail-Bodies
        if len(data) > 500:
            return data[:500] + f"... [truncated {len(data) - 500} chars]"
        # Maskiere E-Mail-Adressen mit Passwörtern (z.B. user:pass@domain)
        if "@" in data and ":" in data:
            return re.sub(r':[^@]+@', ':***@', data)
    return data

def write_safepoint(src: str, dst: str, msg_type: str, data: Dict[str, Any], request_id: str):
    """Schreibt Safepoint im PORTIER 3.0 Format"""
    try:
        now = datetime.utcnow()
        date_path = ARCHIVP_ROOT / now.strftime("%Y/%m/%d")
        date_path.mkdir(parents=True, exist_ok=True)
        
        ts = now.strftime("%Y%m%d%H%M%S%f")[:17]
        # Unicode-Pfeil → (U+2192) – PFLICHT
        filename = f"SP{ts}_{src}→{dst}_{msg_type}.json"
        filepath = date_path / filename
        
        masked_data = mask_secrets(data)
        
        envelope = {
            "sp_id": ts,
            "request_id": request_id,
            "timestamp": now.isoformat() + "Z",
            "src": src,
            "dst": dst,
            "type": msg_type,
            "data": masked_data
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"✅ Safepoint: {filename}")
    except Exception as e:
        logger.error(f"❌ Safepoint-Fehler: {e}")

# ============================================================================
# EMAIL HELPERS
# ============================================================================

def get_imap_connection():
    """Erstellt IMAP-Verbindung"""
    if not EMAIL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Email libraries not available")
    
    if not EMAIL_PASSWORD:
        raise HTTPException(status_code=500, detail="EMAIL_PASSWORD not configured in .env")
    
    try:
        if IMAP_USE_SSL:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        else:
            mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        return mail
    except Exception as e:
        logger.error(f"❌ IMAP connection failed: {e}")
        raise HTTPException(status_code=502, detail=f"IMAP connection failed: {str(e)}")

def get_smtp_connection():
    """Erstellt SMTP-Verbindung"""
    if not EMAIL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Email libraries not available")
    
    if not EMAIL_PASSWORD:
        raise HTTPException(status_code=500, detail="EMAIL_PASSWORD not configured in .env")
    
    try:
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        return server
    except Exception as e:
        logger.error(f"❌ SMTP connection failed: {e}")
        raise HTTPException(status_code=502, detail=f"SMTP connection failed: {str(e)}")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    """Health-Check mit E-Mail-Status"""
    uptime = time.time() - START_TIME
    
    # Teste IMAP-Verbindung (optional)
    imap_status = "unknown"
    if EMAIL_AVAILABLE and EMAIL_PASSWORD:
        try:
            mail = get_imap_connection()
            mail.logout()
            imap_status = "connected"
        except:
            imap_status = "connection_failed"
    
    return JSONResponse({
        "status": "ok",
        "agent": "opena7",
        "port": PORT,
        "kuerzel": "emailp",
        "uptime": round(uptime, 2),
        "email_libraries": EMAIL_AVAILABLE,
        "imap_server": IMAP_SERVER,
        "smtp_server": SMTP_SERVER,
        "email_address": EMAIL_ADDRESS,
        "imap_status": imap_status
    })

@app.get("/")
async def root():
    """Agent-Info"""
    return JSONResponse({
        "agent": "opena7",
        "kuerzel": "emailp",
        "port": PORT,
        "status": "running",
        "capabilities": ["inbox/list", "message/get", "message/send", "message/search", "folders/list"],
        "email": {
            "imap_server": IMAP_SERVER,
            "smtp_server": SMTP_SERVER,
            "address": EMAIL_ADDRESS,
            "libraries_available": EMAIL_AVAILABLE
        }
    })

@app.post("/inbox/list")
async def inbox_list(req: InboxListRequest, _: bool = Depends(verify_token)):
    """Liste E-Mails aus Inbox"""
    request_id = str(uuid4())
    
    write_safepoint("emailp", "kordp", "CMD", {
        "endpoint": "/inbox/list",
        "folder": req.folder,
        "limit": req.limit,
        "offset": req.offset,
        "search_criteria": req.search_criteria
    }, request_id)
    
    try:
        mail = get_imap_connection()
        mail.select(req.folder)
        
        # Suche
        search_criteria = req.search_criteria or "ALL"
        typ, data = mail.search(None, search_criteria)
        
        message_ids = data[0].split()
        total = len(message_ids)
        
        # Pagination
        start = req.offset
        end = min(start + req.limit, total)
        selected_ids = message_ids[start:end]
        
        messages = []
        for msg_id in selected_ids:
            typ, msg_data = mail.fetch(msg_id, '(RFC822.HEADER)')
            if msg_data and msg_data[0]:
                header = msg_data[0][1].decode('utf-8', errors='ignore')
                # Parse header (simplified)
                subject_match = re.search(r'^Subject:\s*(.*)$', header, re.MULTILINE | re.IGNORECASE)
                from_match = re.search(r'^From:\s*(.*)$', header, re.MULTILINE | re.IGNORECASE)
                date_match = re.search(r'^Date:\s*(.*)$', header, re.MULTILINE | re.IGNORECASE)
                
                messages.append({
                    "uid": msg_id.decode(),
                    "subject": subject_match.group(1).strip() if subject_match else "(no subject)",
                    "from": from_match.group(1).strip() if from_match else "(unknown)",
                    "date": date_match.group(1).strip() if date_match else "(unknown)"
                })
        
        mail.logout()
        
        result = {
            "folder": req.folder,
            "total": total,
            "offset": req.offset,
            "limit": req.limit,
            "count": len(messages),
            "messages": messages
        }
        
        write_safepoint("kordp", "emailp", "RESP", result, request_id)
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Inbox list error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list inbox: {str(e)}")

@app.post("/message/send")
async def message_send(req: MessageSendRequest, _: bool = Depends(verify_token)):
    """Sende E-Mail"""
    request_id = str(uuid4())
    
    write_safepoint("emailp", "kordp", "CMD", {
        "endpoint": "/message/send",
        "to": [str(addr) for addr in req.to],
        "cc": [str(addr) for addr in req.cc] if req.cc else None,
        "subject": req.subject,
        "body_length": len(req.body)
    }, request_id)
    
    try:
        # Erstelle Message
        if req.html_body:
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(req.body, 'plain', 'utf-8'))
            msg.attach(MIMEText(req.html_body, 'html', 'utf-8'))
        else:
            msg = MIMEText(req.body, 'plain', 'utf-8')
        
        msg['From'] = formataddr(("ELION Agent", EMAIL_ADDRESS))
        msg['To'] = ', '.join([str(addr) for addr in req.to])
        if req.cc:
            msg['Cc'] = ', '.join([str(addr) for addr in req.cc])
        msg['Subject'] = req.subject
        
        # Sende via SMTP
        server = get_smtp_connection()
        
        recipients = [str(addr) for addr in req.to]
        if req.cc:
            recipients.extend([str(addr) for addr in req.cc])
        if req.bcc:
            recipients.extend([str(addr) for addr in req.bcc])
        
        server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())
        server.quit()
        
        result = {
            "status": "sent",
            "to": [str(addr) for addr in req.to],
            "cc": [str(addr) for addr in req.cc] if req.cc else [],
            "subject": req.subject,
            "from": EMAIL_ADDRESS
        }
        
        write_safepoint("kordp", "emailp", "RESP", result, request_id)
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Send email error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.post("/message/search")
async def message_search(req: SearchRequest, _: bool = Depends(verify_token)):
    """Suche E-Mails"""
    request_id = str(uuid4())
    
    write_safepoint("emailp", "kordp", "CMD", {
        "endpoint": "/message/search",
        "query": req.query,
        "folder": req.folder,
        "date_from": req.date_from,
        "date_to": req.date_to
    }, request_id)
    
    try:
        mail = get_imap_connection()
        mail.select(req.folder)
        
        # Erweitere Query mit Datum-Filter
        search_query = req.query
        if req.date_from:
            search_query = f'SINCE "{req.date_from}" {search_query}'
        if req.date_to:
            search_query = f'BEFORE "{req.date_to}" {search_query}'
        
        typ, data = mail.search(None, search_query)
        
        message_ids = data[0].split()
        
        mail.logout()
        
        result = {
            "folder": req.folder,
            "query": search_query,
            "count": len(message_ids),
            "message_ids": [mid.decode() for mid in message_ids]
        }
        
        write_safepoint("kordp", "emailp", "RESP", result, request_id)
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/folders/list")
async def folders_list(_: bool = Depends(verify_token)):
    """Liste alle IMAP-Ordner"""
    request_id = str(uuid4())
    
    write_safepoint("emailp", "kordp", "CMD", {"endpoint": "/folders/list"}, request_id)
    
    try:
        mail = get_imap_connection()
        typ, folders = mail.list()
        
        folder_list = []
        for folder in folders:
            if folder:
                # Parse folder name (simplified)
                folder_str = folder.decode('utf-8', errors='ignore')
                match = re.search(r'"([^"]+)"$', folder_str)
                if match:
                    folder_list.append(match.group(1))
        
        mail.logout()
        
        result = {
            "count": len(folder_list),
            "folders": folder_list
        }
        
        write_safepoint("kordp", "emailp", "RESP", result, request_id)
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ List folders error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list folders: {str(e)}")

@app.post("/command")
async def command(req: CommandRequest, _: bool = Depends(verify_token)):
    """Generischer Command-Endpoint (Option-2-Flow Compatibility)"""
    request_id = str(uuid4())
    
    write_safepoint("emailp", "kordp", "CMD", {
        "command": req.command,
        "params": mask_secrets(req.params)
    }, request_id)
    
    response = {
        "status": "executed",
        "command": req.command,
        "agent": "opena7",
        "result": "Command received (use specific endpoints for email operations)"
    }
    
    write_safepoint("kordp", "emailp", "RESP", response, request_id)
    
    return JSONResponse(response)

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("✅ opena7 bereit!")
    logger.info(f"   Health: http://127.0.0.1:{PORT}/health")
    
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
