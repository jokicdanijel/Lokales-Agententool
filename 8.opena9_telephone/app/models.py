"""
Data Models für opena9 Telephone Agent
"""

from datetime import datetime
from enum import Enum
from typing import Any

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
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    caller_id: str | None = None
    recording_url: str | None = None
    metadata: dict[str, Any] | None = None


class SIPAccount(BaseModel):
    """SIP-Account Konfiguration"""

    username: str
    password: str
    server: str
    port: int = 5060
    domain: str
    display_name: str | None = None
    enabled: bool = True


class CallEvent(BaseModel):
    """Anruf-Event für Webhooks"""

    event_type: str  # incoming_call, call_answered, call_ended, etc.
    call_id: str
    timestamp: datetime
    from_number: str | None = None
    to_number: str | None = None
    data: dict[str, Any] | None = None


class VoicemailMessage(BaseModel):
    """Voicemail-Nachricht"""

    message_id: str
    caller_number: str
    caller_name: str | None = None
    duration_seconds: int
    recorded_at: datetime
    audio_url: str
    transcription: str | None = None
    is_read: bool = False
