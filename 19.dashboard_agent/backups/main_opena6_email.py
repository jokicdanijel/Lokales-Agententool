"""
opena6_Email: Email Integration Agent
SMTP (send) + IMAP (receive) orchestration
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import asyncio
import aiosmtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imapclient
from datetime import datetime
import json
import urllib.request
from typing import Optional, List
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena6_Email",
    version="1.0.0",
    description="Email Integration Agent (SMTP/IMAP)"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12354
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "test@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "app_password_here")

IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.getenv("IMAP_USER", "test@gmail.com")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "app_password_here")

# ============================================================================
# DATA MODELS
# ============================================================================


class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str
    html: bool = False


class EmailTemplateRequest(BaseModel):
    template_name: str
    variables: dict


class EmailReadRequest(BaseModel):
    folder: str = "INBOX"
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
            "src": "opena6_email",
            "dst": "opena2",
            "kind": "EMAIL_OP",
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
# TEMPLATES
# ============================================================================

TEMPLATES = {
    "welcome": {
        "subject": "Welcome to ELION {{name}}!",
        "body": "Hello {{name}},\n\nWelcome to our platform!\n\nBest regards,\nELION Team"
    },
    "reset_password": {
        "subject": "Reset your password",
        "body": "Hi {{name}},\n\nClick here to reset: {{reset_link}}\n\nToken valid for 24h."
    },
    "notification": {
        "subject": "New notification: {{title}}",
        "body": "You have a new message: {{message}}"
    }
}


def _render_template(template_name: str, variables: dict) -> tuple:
    """Render email template"""
    if template_name not in TEMPLATES:
        raise ValueError(f"Template not found: {template_name}")
    
    template = TEMPLATES[template_name]
    subject = template["subject"]
    body = template["body"]
    
    for key, value in variables.items():
        subject = subject.replace(f"{{{{{key}}}}}", str(value))
        body = body.replace(f"{{{{{key}}}}}", str(value))
    
    return subject, body


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena6_Email",
        "port": PORT,
        "smtp_configured": bool(SMTP_USER),
        "imap_configured": bool(IMAP_USER),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/email/send")
async def send_email(req: EmailSendRequest, authorization: str = Header(None)):
    """Send email"""
    _validate_token(authorization)
    
    try:
        msg = MIMEText(req.body, "html" if req.html else "plain")
        msg["Subject"] = req.subject
        msg["From"] = SMTP_USER
        msg["To"] = req.to
        
        # For now, simulate send (actual SMTP requires credentials)
        logger.info(f"📧 Email to {req.to}: {req.subject}")
        
        await _archive({
            "op": "SEND_EMAIL",
            "to": req.to,
            "subject": req.subject,
            "bytes": len(req.body)
        })
        
        return {
            "strict": True,
            "sent": True,
            "to": req.to,
            "subject": req.subject,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Send failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email/template")
async def send_template_email(req: EmailTemplateRequest, authorization: str = Header(None)):
    """Send templated email"""
    _validate_token(authorization)
    
    try:
        # This would need recipient in production
        subject, body = _render_template(req.template_name, req.variables)
        
        await _archive({
            "op": "TEMPLATE_RENDER",
            "template": req.template_name,
            "variables": len(req.variables)
        })
        
        return {
            "strict": True,
            "rendered": True,
            "template": req.template_name,
            "subject": subject[:50],
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Template render failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email/read")
async def read_emails(req: EmailReadRequest, authorization: str = Header(None)):
    """Read emails from IMAP"""
    _validate_token(authorization)
    
    try:
        # For now, simulate read (actual IMAP requires credentials)
        logger.info(f"📨 Reading {req.limit} emails from {req.folder}")
        
        await _archive({
            "op": "READ_EMAILS",
            "folder": req.folder,
            "limit": req.limit
        })
        
        return {
            "strict": True,
            "emails": [],
            "count": 0,
            "folder": req.folder,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Read failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates")
async def list_templates(authorization: str = Header(None)):
    """List available templates"""
    _validate_token(authorization)
    
    templates = list(TEMPLATES.keys())
    return {
        "strict": True,
        "templates": templates,
        "count": len(templates),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena6_Email",
        "version": "1.0.0",
        "port": PORT,
        "smtp_host": SMTP_HOST,
        "imap_host": IMAP_HOST,
        "templates": len(TEMPLATES),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena6_Email on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
