"""
Data Models für opena9 Telephone Agent
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class CallDirection(Enum):
    """Anrufrichtung"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatus(Enum):
    """Anrufstatus"""
    INITIATED = "initiated"
    RINGING = "ringing"
    ACTIVE = "active"
    HELD = "held"
    TRANSFERRING = "transferring"
    ENDED = "ended"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"


class CallRecord(BaseModel):
    """Anruf-Datensatz"""
    call_id: str
    from_number: str
    to_number: str
    direction: CallDirection
    status: CallStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    caller_id: Optional[str] = None
    recording_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SIPAccount(BaseModel):
    """SIP-Account Konfiguration"""
    username: str
    password: str
    server: str
    port: int = 5060
    domain: str
    display_name: Optional[str] = None
    enabled: bool = True


class CallEvent(BaseModel):
    """Anruf-Event für Webhooks"""
    event_type: str  # incoming_call, call_answered, call_ended, etc.
    call_id: str
    timestamp: datetime
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class VoicemailMessage(BaseModel):
    """Voicemail-Nachricht"""
    message_id: str
    caller_number: str
    caller_name: Optional[str] = None
    duration_seconds: int
    recorded_at: datetime
    audio_url: str
    transcription: Optional[str] = None
    is_read: bool = False