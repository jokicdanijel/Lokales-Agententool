"""
opena7 Data Models & Schemas
Mail Agent — Messages, Attachments, Responses, Safepoints
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class MailAction(str, Enum):
    """Mail processing actions"""
    FETCH = "fetch"
    FETCH_AND_REPLY = "fetch_and_reply"
    SEND = "send"
    MARK_SPAM = "mark_spam"
    DELETE = "delete"
    FORWARD = "forward"


class SentimentType(str, Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    URGENT = "urgent"


class AttachmentInfo(BaseModel):
    """Information about an email attachment"""
    filename: str
    mime_type: str
    size_bytes: int
    sha256: Optional[str] = None
    path: Optional[str] = None  # archivp path
    scanned: bool = False
    safe: bool = True
    scan_result: Optional[str] = None


class MailMessage(BaseModel):
    """Email message structure"""
    msg_id: str  # UID or Message-ID
    subject: str
    sender: EmailStr
    recipients: List[EmailStr]
    cc: List[EmailStr] = Field(default_factory=list)
    bcc: List[EmailStr] = Field(default_factory=list)
    date: str  # ISO 8601
    body_text: str
    body_html: Optional[str] = None
    body_preview: str = Field(default="", description="First N chars of body")
    attachments: List[AttachmentInfo] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)  # Seen, Flagged, etc.
    language: Optional[str] = None  # ISO 639-1 (en, de, etc.)
    sentiment: Optional[SentimentType] = None
    urgency: int = Field(default=0, ge=0, le=10)  # 0-10 scale


class MailReplyTemplate(BaseModel):
    """Auto-reply template"""
    name: str
    subject_prefix: str
    body: str
    signature: Optional[str] = None


class MailRunRequest(BaseModel):
    """Request to process mail"""
    request_id: Optional[str] = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    action: MailAction
    payload: Dict[str, Any]
    strict: bool = True


class MailReplyPayload(BaseModel):
    """Payload for fetch_and_reply action"""
    mailbox: str
    mode: str = "unread_only"  # unread_only, all, since_timestamp
    ruleset: str = "default"
    reply_template: Optional[str] = None
    max_count: int = 10
    auto_forward: List[str] = Field(default_factory=list)  # Forward to other agents


class MailSendPayload(BaseModel):
    """Payload for send action"""
    recipient: EmailStr
    subject: str
    body_text: str
    body_html: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    reply_to_msg_id: Optional[str] = None
    idempotency_key: Optional[str] = None


class MailRunResponse(BaseModel):
    """Response from mail processing"""
    request_id: str
    status: str  # success, failed, partial
    action: MailAction
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    replied: int = 0
    archived: Optional[str] = None  # archivp path
    messages: List[MailMessage] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    processing_ms: int = 0
    strict: bool = True


class MailErrorResponse(BaseModel):
    """Error response from mail operation"""
    request_id: str
    status: str = "failed"
    error_code: str  # AUTH_FAILED, MAILBOX_LOCKED, SMTP_REJECTED, etc.
    error_message: str
    retryable: bool = False
    strict: bool = True


class HealthResponse(BaseModel):
    """Health check response"""
    service: str
    status: str  # ok, degraded, error
    component: str
    port: int
    mailbox: Optional[str] = None
    imap_connected: bool = False
    smtp_connected: bool = False
    ts: str


class MetricsData(BaseModel):
    """Metrics snapshot"""
    mail_in_total: int = 0
    mail_out_total: int = 0
    errors_total: int = 0
    attachment_bytes_total: int = 0
    processing_seconds_bucket: Dict[str, int] = Field(default_factory=dict)


class Safepoint(BaseModel):
    """Safepoint for archiving via opena2"""
    ts: str  # ISO 8601
    src: str  # opena7
    dst: str  # opena2
    kind: str  # CMD, RESP, LOG
    request_id: str
    action: MailAction
    payload: Any


class EventLog(BaseModel):
    """Structured event log (JSONL)"""
    ts: str  # ISO 8601
    request_id: str
    action: str
    msg_id: Optional[str] = None
    sender: Optional[str] = None
    status: str  # ok, error, warning
    note: str
    error: Optional[str] = None
    processing_ms: int = 0
    strict: bool = True
