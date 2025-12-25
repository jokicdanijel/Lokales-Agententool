"""
opena13_Calendar: Calendar Management Agent
Google Calendar integration, event management, availability checking, reminders
"""

import json
import logging
import os
import secrets
import sys
import urllib.request
from datetime import datetime, timedelta

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena13_Calendar", version="1.0.0", description="Calendar Management Agent - Google Calendar Integration"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12361
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_events: dict = {}
_reminders: dict = {}
_sync_status: dict = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class EventCreateRequest(BaseModel):
    title: str
    description: str | None = None
    start_time: str  # ISO 8601
    end_time: str  # ISO 8601
    calendar: str = "default"
    attendees: list[str] = []


class EventListRequest(BaseModel):
    calendar: str = "default"
    start_date: str | None = None
    end_date: str | None = None


class GoogleSyncRequest(BaseModel):
    calendar_id: str
    direction: str = "bidirectional"  # onewaypush, onewaypu ll, bidirectional


class AvailabilityCheckRequest(BaseModel):
    start_time: str  # ISO 8601
    duration_minutes: int
    calendar: str = "default"


class ReminderSetRequest(BaseModel):
    event_id: str
    reminder_time_minutes: int = 15  # Before event


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: str | None):
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
            "src": "opena13_calendar",
            "dst": "opena2",
            "kind": "CALENDAR_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"},
        }

        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_event_id() -> str:
    """Generate unique event ID"""
    return f"EVT_{secrets.token_hex(8).upper()}"


def _parse_iso_datetime(iso_str: str) -> datetime:
    """Parse ISO 8601 datetime"""
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except:
        return datetime.fromisoformat(iso_str)


def _check_time_conflicts(start_time: datetime, end_time: datetime, calendar: str) -> list[str]:
    """Check for calendar conflicts"""
    conflicts = []
    for event_id, event in _events.items():
        if event.get("calendar") != calendar:
            continue

        evt_start = _parse_iso_datetime(event["start_time"])
        evt_end = _parse_iso_datetime(event["end_time"])

        # Check overlap
        if start_time < evt_end and end_time > evt_start:
            conflicts.append(event_id)

    return conflicts


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena13_Calendar",
        "port": PORT,
        "events": len(_events),
        "reminders": len(_reminders),
        "ts": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/event/create")
async def create_event(req: EventCreateRequest, authorization: str = Header(None)):
    """Create calendar event"""
    _validate_token(authorization)

    try:
        event_id = _generate_event_id()
        start = _parse_iso_datetime(req.start_time)
        end = _parse_iso_datetime(req.end_time)

        # Check for conflicts
        conflicts = _check_time_conflicts(start, end, req.calendar)

        event_entry = {
            "title": req.title,
            "description": req.description,
            "start_time": req.start_time,
            "end_time": req.end_time,
            "calendar": req.calendar,
            "attendees": req.attendees,
            "created_at": datetime.utcnow().isoformat(),
            "conflicts": conflicts,
            "status": "confirmed",
        }

        _events[event_id] = event_entry
        logger.info(f"📅 Event created: {event_id} ({req.title})")

        await _archive(
            {
                "op": "EVENT_CREATE",
                "event_id": event_id,
                "title": req.title,
                "calendar": req.calendar,
                "attendees": len(req.attendees),
                "conflicts": len(conflicts),
            }
        )

        return {
            "strict": True,
            "event_id": event_id,
            "created": True,
            "calendar": req.calendar,
            "conflicts": conflicts,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Event creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/event/list")
async def list_events(req: EventListRequest, authorization: str = Header(None)):
    """List calendar events"""
    _validate_token(authorization)

    try:
        events_list = []

        for event_id, event in _events.items():
            if event.get("calendar") != req.calendar:
                continue

            # Filter by date range if provided
            if req.start_date:
                if event["start_time"] < req.start_date:
                    continue
            if req.end_date:
                if event["end_time"] > req.end_date:
                    continue

            events_list.append({**event, "id": event_id})

        logger.info(f"📋 Events listed: {len(events_list)} from {req.calendar}")

        return {
            "strict": True,
            "events": events_list,
            "count": len(events_list),
            "calendar": req.calendar,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Event listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/google")
async def sync_google_calendar(req: GoogleSyncRequest, authorization: str = Header(None)):
    """Sync with Google Calendar"""
    _validate_token(authorization)

    try:
        # Simulated Google Calendar API call
        sync_entry = {
            "calendar_id": req.calendar_id,
            "synced_at": datetime.utcnow().isoformat(),
            "direction": req.direction,
            "events_synced": len(_events),
            "status": "success",
        }

        _sync_status[req.calendar_id] = sync_entry
        logger.info(f"🔄 Google Calendar synced: {req.calendar_id}")

        await _archive(
            {
                "op": "GOOGLE_SYNC",
                "calendar_id": req.calendar_id,
                "direction": req.direction,
                "events_count": len(_events),
            }
        )

        return {"strict": True, "sync": sync_entry, "ts": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"❌ Google sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/availability/check")
async def check_availability(req: AvailabilityCheckRequest, authorization: str = Header(None)):
    """Check availability in calendar"""
    _validate_token(authorization)

    try:
        start = _parse_iso_datetime(req.start_time)
        end = start + timedelta(minutes=req.duration_minutes)

        conflicts = _check_time_conflicts(start, end, req.calendar)
        is_available = len(conflicts) == 0

        availability = {
            "calendar": req.calendar,
            "requested_start": req.start_time,
            "duration_minutes": req.duration_minutes,
            "is_available": is_available,
            "conflicting_events": conflicts,
        }

        logger.info(f"⏰ Availability checked: {req.calendar} (available: {is_available})")

        await _archive(
            {
                "op": "AVAILABILITY_CHECK",
                "calendar": req.calendar,
                "duration": req.duration_minutes,
                "available": is_available,
            }
        )

        return {"strict": True, "availability": availability, "ts": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"❌ Availability check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reminder/set")
async def set_reminder(req: ReminderSetRequest, authorization: str = Header(None)):
    """Set event reminder"""
    _validate_token(authorization)

    try:
        if req.event_id not in _events:
            raise HTTPException(status_code=404, detail=f"Event {req.event_id} not found")

        event = _events[req.event_id]
        event_start = _parse_iso_datetime(event["start_time"])
        reminder_time = event_start - timedelta(minutes=req.reminder_time_minutes)

        reminder_entry = {
            "event_id": req.event_id,
            "reminder_time": reminder_time.isoformat(),
            "minutes_before": req.reminder_time_minutes,
            "status": "active",
        }

        _reminders[req.event_id] = reminder_entry
        logger.info(f"🔔 Reminder set: {req.event_id} ({req.reminder_time_minutes} min before)")

        await _archive({"op": "REMINDER_SET", "event_id": req.event_id, "minutes_before": req.reminder_time_minutes})

        return {"strict": True, "reminder": reminder_entry, "ts": datetime.utcnow().isoformat() + "Z"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Reminder setting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)

    return {
        "service": "opena13_Calendar",
        "version": "1.0.0",
        "port": PORT,
        "events": len(_events),
        "reminders": len(_reminders),
        "synced_calendars": len(_sync_status),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting opena13_Calendar on port {PORT}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
