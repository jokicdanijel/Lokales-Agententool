"""
opena8 Data Models
WhatsApp message schemas, media objects, classification
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class MediaType(str, Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    STICKER = "sticker"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    CONTACTS = "contacts"
    REACTION = "reaction"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    URGENT = "urgent"


class MediaObject(BaseModel):
    """Media attachment details"""
    media_type: MediaType
    media_id: str
    url: Optional[str] = None
    mime_type: str = Field(default="application/octet-stream")
    file_size_bytes: int = 0
    caption: Optional[str] = None
    sha256: Optional[str] = None  # Downloaded file hash


class WhatsAppMessage(BaseModel):
    """WhatsApp message structure"""
    message_id: str
    phone_number: str  # Sender/recipient
    name: Optional[str] = None
    timestamp: datetime
    direction: MessageDirection
    
    # Message content
    type: MessageType
    body: Optional[str] = None
    media: Optional[MediaObject] = None
    
    # Classification
    sentiment: SentimentType = SentimentType.NEUTRAL
    urgency: int = Field(default=5, ge=0, le=10)
    language: str = "unknown"
    
    # Metadata
    group_id: Optional[str] = None
    reply_to: Optional[str] = None
    status: str = "received"


class WebhookRequest(BaseModel):
    """Meta Webhook entry (from /webhook POST)"""
    object: str = "whatsapp_business_account"
    entry: List[Dict[str, Any]]


class WebhookMessageEvent(BaseModel):
    """Extracted message from webhook entry"""
    message_id: str
    phone_number: str
    timestamp: int  # Unix timestamp
    type: MessageType
    body: Optional[str] = None
    media: Optional[Dict[str, str]] = None


class SendMessageRequest(BaseModel):
    """Request to send WhatsApp message"""
    to_phone: str
    message_type: MessageType = MessageType.TEXT
    body: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[MediaType] = None


class SendMessageResponse(BaseModel):
    """Response from sending message"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: datetime


class HealthResponse(BaseModel):
    """Service health status"""
    status: Literal["ok", "degraded", "error"]
    service: str = "opena8"
    version: str = "1.0.0"
    timestamp: datetime
    meta_api_connected: bool = False
    opena2_connected: bool = False
    opena1_connected: bool = False


class Safepoint(BaseModel):
    """Archivator safepoint structure"""
    ts: datetime
    src: str = "opena8"
    dst: str = "opena2"
    kind: Literal["MSG", "MEDIA", "SEND", "ERROR", "INIT"]
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: str = "ok"


class MailRunRequest(BaseModel):
    """Generic agent request"""
    action: str  # "ingest", "send", "media_download"
    payload: Dict[str, Any] = Field(default_factory=dict)


class MailRunResponse(BaseModel):
    """Generic agent response"""
    success: bool
    action: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime
