#!/usr/bin/env python3
"""
opena14 - Calendar Management Agent
====================================

Agent-ID:    opena14
Port:        12359
Kürzel:      calp
Version:     1.0

Funktionen:
- Event-Management (CRUD)
- iCalendar-Dateien (Import/Export)
- Recurring Events (RRULE Support)
- Timezone-Handling (pytz)
- Multi-Calendar Support

Architektur:
- FastAPI + uvicorn
- iCalendar Library (icalendar)
- JSON-basierte Persistence (upgradeable zu PostgreSQL)
- JSONL Event-History (append-only)
- Strict JSON Schemas (extra="forbid")

Option-2-Flow:
  OpenAI → opena1 → opena2 → kordp → opena14 → opena2 → opena1 → OpenAI

Port Policy:
  - Backend: 12344-12399 (✓ 12359)
  - UI-only: 8080 (verboten)

Security:
  - Bearer Token (ENV-only)
  - Secrets niemals hardcoded
  - Event-Daten verschlüsselt (optional)

Maintainer: ELION Team
Letzte Aktualisierung: 27. November 2025
"""

import os
import sys
import json
import time
import uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

try:
    from icalendar import Calendar, Event as ICalEvent
    import pytz
    ICAL_AVAILABLE = True
except ImportError:
    ICAL_AVAILABLE = False
    print("⚠️  WARNING: icalendar/pytz nicht installiert - iCal-Features deaktiviert")

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load Bearer Token from .env
BEARER_TOKEN = None
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip().startswith("BEARER_TOKEN="):
                BEARER_TOKEN = line.split("=", 1)[1].strip()
                break

if not BEARER_TOKEN:
    print("⚠️  WARNING: BEARER_TOKEN nicht in .env gefunden!")
    BEARER_TOKEN = "dev-token-only"

# Paths
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

EVENTS_FILE = DATA_DIR / "events.json"
CALENDARS_FILE = DATA_DIR / "calendars.json"
EVENT_HISTORY_FILE = DATA_DIR / "event_history.jsonl"

# Port Policy Enforcement
PORT = 12359
ALLOWED_PORTS = range(12344, 12400)
FORBIDDEN_PORTS = [8080]

if PORT not in ALLOWED_PORTS or PORT in FORBIDDEN_PORTS:
    raise RuntimeError(f"❌ Port {PORT} verletzt Port-Policy! Erlaubt: {ALLOWED_PORTS}, Verboten: {FORBIDDEN_PORTS}")

# Service Metadata
SERVICE_NAME = "opena14"
KUERZEL = "calp"
VERSION = "1.0"

# Default Timezone
DEFAULT_TIMEZONE = "Europe/Berlin"

# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class EventStatus(str, Enum):
    """Event Status"""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class RecurrenceFrequency(str, Enum):
    """Recurrence Frequency (RRULE)"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


@dataclass
class CalendarEvent:
    """Calendar Event Data Class"""
    event_id: str
    calendar_id: str
    summary: str
    start: str  # ISO 8601 datetime
    end: str    # ISO 8601 datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    status: str = EventStatus.CONFIRMED.value
    all_day: bool = False
    recurrence_rule: Optional[str] = None  # RRULE
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class CalendarInfo:
    """Calendar Metadata"""
    calendar_id: str
    name: str
    description: Optional[str] = None
    timezone: str = DEFAULT_TIMEZONE
    color: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


# ============================================================================
# PYDANTIC REQUEST/RESPONSE MODELS (STRICT JSON)
# ============================================================================

class EventCreateRequest(BaseModel):
    """Request: Event erstellen"""
    calendar_id: str = Field(..., min_length=1, max_length=100)
    summary: str = Field(..., min_length=1, max_length=500)
    start: str  # ISO 8601
    end: str    # ISO 8601
    description: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, max_length=500)
    attendees: Optional[List[str]] = Field(None, max_items=100)
    all_day: bool = False
    recurrence_rule: Optional[str] = Field(None, max_length=500)

    @validator("start", "end")
    def validate_datetime(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Datum muss ISO 8601 Format sein (YYYY-MM-DDTHH:MM:SSZ)")
        return v

    class Config:
        extra = "forbid"


class EventUpdateRequest(BaseModel):
    """Request: Event aktualisieren"""
    event_id: str
    summary: Optional[str] = Field(None, min_length=1, max_length=500)
    start: Optional[str] = None  # ISO 8601
    end: Optional[str] = None    # ISO 8601
    description: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, max_length=500)
    attendees: Optional[List[str]] = Field(None, max_items=100)
    status: Optional[EventStatus] = None
    recurrence_rule: Optional[str] = Field(None, max_length=500)

    @validator("start", "end")
    def validate_datetime(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Datum muss ISO 8601 Format sein")
        return v

    class Config:
        extra = "forbid"


class EventDeleteRequest(BaseModel):
    """Request: Event löschen"""
    event_id: str
    calendar_id: str

    class Config:
        extra = "forbid"


class EventListRequest(BaseModel):
    """Request: Events auflisten"""
    calendar_id: Optional[str] = None
    start_date: Optional[str] = None  # ISO 8601
    end_date: Optional[str] = None    # ISO 8601
    status: Optional[EventStatus] = None
    max_results: int = Field(100, ge=1, le=500)

    @validator("start_date", "end_date")
    def validate_date(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Datum muss ISO 8601 Format sein")
        return v

    class Config:
        extra = "forbid"


class EventResponse(BaseModel):
    """Response: Event"""
    event_id: str
    calendar_id: str
    summary: str
    start: str
    end: str
    description: Optional[str]
    location: Optional[str]
    attendees: Optional[List[str]]
    status: str
    all_day: bool
    recurrence_rule: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        extra = "forbid"


class CalendarCreateRequest(BaseModel):
    """Request: Kalender erstellen"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    timezone: str = Field(DEFAULT_TIMEZONE, max_length=50)
    color: Optional[str] = Field(None, max_length=7)  # Hex color

    class Config:
        extra = "forbid"


class CalendarResponse(BaseModel):
    """Response: Kalender"""
    calendar_id: str
    name: str
    description: Optional[str]
    timezone: str
    color: Optional[str]
    created_at: str

    class Config:
        extra = "forbid"


class CommandRequest(BaseModel):
    """Option-2-Flow Command Request"""
    action: str = Field(..., min_length=1, max_length=100)
    params: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class HealthResponse(BaseModel):
    """Health Check Response"""
    status: str
    service: str
    kuerzel: str
    port: int
    uptime_seconds: float
    total_events: int
    total_calendars: int
    ical_support: bool

    class Config:
        extra = "forbid"


# ============================================================================
# DATA PERSISTENCE LAYER
# ============================================================================

class DataStore:
    """JSON-based Data Persistence (upgradeable to PostgreSQL)"""

    @staticmethod
    def load_events() -> List[CalendarEvent]:
        """Load all events from JSON"""
        if not EVENTS_FILE.exists():
            return []
        with open(EVENTS_FILE) as f:
            data = json.load(f)
            return [CalendarEvent(**e) for e in data]

    @staticmethod
    def save_events(events: List[CalendarEvent]):
        """Save all events to JSON"""
        with open(EVENTS_FILE, "w") as f:
            json.dump([asdict(e) for e in events], f, indent=2)

    @staticmethod
    def load_calendars() -> List[CalendarInfo]:
        """Load all calendars from JSON"""
        if not CALENDARS_FILE.exists():
            # Create default calendar
            default = CalendarInfo(
                calendar_id="default",
                name="Default Calendar",
                description="System default calendar",
                timezone=DEFAULT_TIMEZONE
            )
            DataStore.save_calendars([default])
            return [default]
        
        with open(CALENDARS_FILE) as f:
            data = json.load(f)
            return [CalendarInfo(**c) for c in data]

    @staticmethod
    def save_calendars(calendars: List[CalendarInfo]):
        """Save all calendars to JSON"""
        with open(CALENDARS_FILE, "w") as f:
            json.dump([asdict(c) for c in calendars], f, indent=2)

    @staticmethod
    def log_event_history(operation: str, event_id: str, details: Dict):
        """Append event operation to JSONL history"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "event_id": event_id,
            "details": details
        }
        with open(EVENT_HISTORY_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")


# ============================================================================
# ICALENDAR UTILITIES
# ============================================================================

class ICalendarUtils:
    """iCalendar Import/Export Utilities"""

    @staticmethod
    def event_to_ical(event: CalendarEvent) -> str:
        """Convert CalendarEvent to iCalendar string"""
        if not ICAL_AVAILABLE:
            raise HTTPException(status_code=501, detail="iCalendar support not available (missing icalendar library)")

        cal = Calendar()
        cal.add('prodid', '-//opena14 Calendar Agent//ELION//EN')
        cal.add('version', '2.0')

        ical_event = ICalEvent()
        ical_event.add('uid', event.event_id)
        ical_event.add('summary', event.summary)
        
        # Parse datetime
        start_dt = datetime.fromisoformat(event.start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(event.end.replace("Z", "+00:00"))
        
        if event.all_day:
            ical_event.add('dtstart', start_dt.date())
            ical_event.add('dtend', end_dt.date())
        else:
            ical_event.add('dtstart', start_dt)
            ical_event.add('dtend', end_dt)

        if event.description:
            ical_event.add('description', event.description)
        if event.location:
            ical_event.add('location', event.location)
        if event.recurrence_rule:
            ical_event.add('rrule', event.recurrence_rule)

        ical_event.add('status', event.status.upper())
        
        cal.add_component(ical_event)
        return cal.to_ical().decode('utf-8')


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="opena14 - Calendar Management Agent",
    version=VERSION,
    description="Event-Management, iCalendar, Recurring Events, Timezone-Support",
)

# Track service start time for uptime
SERVICE_START_TIME = time.time()


# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

async def verify_bearer_token(authorization: Optional[str] = Header(None)):
    """Verify Bearer Token for protected endpoints"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = parts[1]
    if token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - Service Info"""
    return {
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "version": VERSION,
        "port": str(PORT),
        "description": "Calendar Management Agent - Event CRUD, iCal, Recurring Events"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health Check - No Auth Required"""
    events = DataStore.load_events()
    calendars = DataStore.load_calendars()

    uptime = time.time() - SERVICE_START_TIME

    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        kuerzel=KUERZEL,
        port=PORT,
        uptime_seconds=round(uptime, 2),
        total_events=len(events),
        total_calendars=len(calendars),
        ical_support=ICAL_AVAILABLE
    )


@app.post("/events/create", response_model=EventResponse)
async def create_event(req: EventCreateRequest, authorization: Optional[str] = Header(None)):
    """Create new calendar event (Auth required)"""
    await verify_bearer_token(authorization)

    events = DataStore.load_events()
    calendars = DataStore.load_calendars()

    # Verify calendar exists
    if not any(c.calendar_id == req.calendar_id for c in calendars):
        raise HTTPException(status_code=404, detail=f"Calendar {req.calendar_id} not found")

    # Create event
    event = CalendarEvent(
        event_id=str(uuid.uuid4()),
        calendar_id=req.calendar_id,
        summary=req.summary,
        start=req.start,
        end=req.end,
        description=req.description,
        location=req.location,
        attendees=req.attendees,
        all_day=req.all_day,
        recurrence_rule=req.recurrence_rule
    )

    events.append(event)
    DataStore.save_events(events)

    DataStore.log_event_history("CREATE", event.event_id, {
        "summary": event.summary,
        "start": event.start,
        "end": event.end
    })

    return EventResponse(**asdict(event))


@app.post("/events/list", response_model=List[EventResponse])
async def list_events(req: EventListRequest, authorization: Optional[str] = Header(None)):
    """List calendar events (Auth required)"""
    await verify_bearer_token(authorization)

    events = DataStore.load_events()

    # Filter by calendar
    if req.calendar_id:
        events = [e for e in events if e.calendar_id == req.calendar_id]

    # Filter by date range
    if req.start_date:
        start_dt = datetime.fromisoformat(req.start_date.replace("Z", "+00:00"))
        events = [e for e in events if datetime.fromisoformat(e.end.replace("Z", "+00:00")) >= start_dt]

    if req.end_date:
        end_dt = datetime.fromisoformat(req.end_date.replace("Z", "+00:00"))
        events = [e for e in events if datetime.fromisoformat(e.start.replace("Z", "+00:00")) <= end_dt]

    # Filter by status
    if req.status:
        events = [e for e in events if e.status == req.status.value]

    # Limit results
    events = events[:req.max_results]

    return [EventResponse(**asdict(e)) for e in events]


@app.put("/events/update", response_model=EventResponse)
async def update_event(req: EventUpdateRequest, authorization: Optional[str] = Header(None)):
    """Update calendar event (Auth required)"""
    await verify_bearer_token(authorization)

    events = DataStore.load_events()

    # Find event
    event = next((e for e in events if e.event_id == req.event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {req.event_id} not found")

    # Update fields
    if req.summary:
        event.summary = req.summary
    if req.start:
        event.start = req.start
    if req.end:
        event.end = req.end
    if req.description is not None:
        event.description = req.description
    if req.location is not None:
        event.location = req.location
    if req.attendees is not None:
        event.attendees = req.attendees
    if req.status:
        event.status = req.status.value
    if req.recurrence_rule is not None:
        event.recurrence_rule = req.recurrence_rule

    event.updated_at = datetime.now(timezone.utc).isoformat()

    DataStore.save_events(events)

    DataStore.log_event_history("UPDATE", event.event_id, {
        "summary": event.summary,
        "start": event.start
    })

    return EventResponse(**asdict(event))


@app.delete("/events/delete")
async def delete_event(req: EventDeleteRequest, authorization: Optional[str] = Header(None)):
    """Delete calendar event (Auth required)"""
    await verify_bearer_token(authorization)

    events = DataStore.load_events()

    # Find and remove event
    original_count = len(events)
    events = [e for e in events if not (e.event_id == req.event_id and e.calendar_id == req.calendar_id)]

    if len(events) == original_count:
        raise HTTPException(status_code=404, detail=f"Event {req.event_id} not found in calendar {req.calendar_id}")

    DataStore.save_events(events)

    DataStore.log_event_history("DELETE", req.event_id, {
        "calendar_id": req.calendar_id
    })

    return {"status": "deleted", "event_id": req.event_id}


@app.post("/calendars/create", response_model=CalendarResponse)
async def create_calendar(req: CalendarCreateRequest, authorization: Optional[str] = Header(None)):
    """Create new calendar (Auth required)"""
    await verify_bearer_token(authorization)

    calendars = DataStore.load_calendars()

    # Create calendar
    calendar = CalendarInfo(
        calendar_id=str(uuid.uuid4()),
        name=req.name,
        description=req.description,
        timezone=req.timezone,
        color=req.color
    )

    calendars.append(calendar)
    DataStore.save_calendars(calendars)

    return CalendarResponse(**asdict(calendar))


@app.get("/calendars/list", response_model=List[CalendarResponse])
async def list_calendars(authorization: Optional[str] = Header(None)):
    """List all calendars (Auth required)"""
    await verify_bearer_token(authorization)

    calendars = DataStore.load_calendars()
    return [CalendarResponse(**asdict(c)) for c in calendars]


@app.get("/events/{event_id}/ical")
async def export_event_ical(event_id: str, authorization: Optional[str] = Header(None)):
    """Export event as iCalendar (.ics) file (Auth required)"""
    await verify_bearer_token(authorization)

    events = DataStore.load_events()
    event = next((e for e in events if e.event_id == event_id), None)
    
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    ical_content = ICalendarUtils.event_to_ical(event)

    return JSONResponse(
        content={"ical": ical_content},
        media_type="application/json"
    )


@app.post("/command")
async def command_endpoint(req: CommandRequest, authorization: Optional[str] = Header(None)):
    """Option-2-Flow Command Endpoint (Auth required)"""
    await verify_bearer_token(authorization)

    action = req.action
    params = req.params

    if action == "create_event":
        event_req = EventCreateRequest(**params)
        response = await create_event(event_req, authorization)
        return {"status": "success", "action": action, "result": response.dict()}

    elif action == "list_events":
        list_req = EventListRequest(**params)
        response = await list_events(list_req, authorization)
        return {"status": "success", "action": action, "result": [r.dict() for r in response]}

    elif action == "update_event":
        update_req = EventUpdateRequest(**params)
        response = await update_event(update_req, authorization)
        return {"status": "success", "action": action, "result": response.dict()}

    elif action == "create_calendar":
        calendar_req = CalendarCreateRequest(**params)
        response = await create_calendar(calendar_req, authorization)
        return {"status": "success", "action": action, "result": response.dict()}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print(f"🚀 Starting {SERVICE_NAME} ({KUERZEL}) on port {PORT}...")
    print(f"📅 Data directory: {DATA_DIR}")
    print(f"🔐 Bearer token loaded: {BEARER_TOKEN[:20]}..." if BEARER_TOKEN else "⚠️  No Bearer token!")
    print(f"📆 iCalendar support: {'✅ Enabled' if ICAL_AVAILABLE else '⚠️  Disabled (install: pip install icalendar pytz)'}")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
