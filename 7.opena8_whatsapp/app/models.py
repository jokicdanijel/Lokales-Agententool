"""
opena8 Data Models
WhatsApp message schemas, media objects, classification
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


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
    url: str | None = None
    mime_type: str = Field(default="application/octet-stream")
    file_size_bytes: int = 0
    caption: str | None = None
    sha256: str | None = None  # Downloaded file hash


class WhatsAppMessage(BaseModel):
    """WhatsApp message structure"""

    message_id: str
    phone_number: str  # Sender/recipient
    name: str | None = None
    timestamp: datetime
    direction: MessageDirection

    # Message content
    type: MessageType
    body: str | None = None
    media: MediaObject | None = None

    # Classification
    sentiment: SentimentType = SentimentType.NEUTRAL
    urgency: int = Field(default=5, ge=0, le=10)
    language: str = "unknown"

    # Metadata
    group_id: str | None = None
    reply_to: str | None = None
    status: str = "received"


class WebhookRequest(BaseModel):
    """Meta Webhook entry (from /webhook POST)"""

    object: str = "whatsapp_business_account"
    entry: list[dict[str, Any]]


class WebhookMessageEvent(BaseModel):
    """Extracted message from webhook entry"""

    message_id: str
    phone_number: str
    timestamp: int  # Unix timestamp
    type: MessageType
    body: str | None = None
    media: dict[str, str] | None = None


class SendMessageRequest(BaseModel):
    """Request to send WhatsApp message"""

    to_phone: str
    message_type: MessageType = MessageType.TEXT
    body: str | None = None
    media_url: str | None = None
    media_type: MediaType | None = None


class SendMessageResponse(BaseModel):
    """Response from sending message"""

    success: bool
    message_id: str | None = None
    error: str | None = None
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
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = "ok"


class MailRunRequest(BaseModel):
    """Generic agent request"""

    action: str  # "ingest", "send", "media_download"
    payload: dict[str, Any] = Field(default_factory=dict)


class MailRunResponse(BaseModel):
    """Generic agent response"""

    success: bool
    action: str
    data: dict[str, Any] | None = None
    error: str | None = None
    timestamp: datetime
