"""
Data Models für opena8 WhatsApp Agent
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class MessageDirection(Enum):
    """Nachrichtenrichtung"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageType(Enum):
    """Nachrichtentyp"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class SentimentType(Enum):
    """Sentiment-Klassifikation"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    URGENT = "urgent"


class MediaType(Enum):
    """Media-Typ"""
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class MediaObject(BaseModel):
    """Media-Objekt in WhatsApp-Nachricht"""
    media_type: MediaType
    media_id: str
    mime_type: str
    caption: Optional[str] = None
    url: Optional[str] = None
    size_bytes: Optional[int] = None


class WhatsAppMessage(BaseModel):
    """WhatsApp-Nachricht"""
    message_id: str
    phone_number: str
    name: str
    timestamp: datetime
    direction: MessageDirection
    type: MessageType
    body: Optional[str] = None
    media: Optional[MediaObject] = None
    sentiment: SentimentType = SentimentType.NEUTRAL
    urgency: int = 5  # 1-10 scale
    language: str = "unknown"
    status: str = "received"
    metadata: Optional[Dict[str, Any]] = None