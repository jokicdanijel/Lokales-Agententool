#!/usr/bin/env python3
"""
opena10 – Call Tracking Agent (Port 12355)
===========================================

Purpose: Call Tracking, SQLAlchemy-Models, Campaign-Tracking
Kuerzel: calltrackp

Features:
- Call Event Ingestion (integration with opena9)
- Campaign-based tracking with tracking numbers
- SQLAlchemy models for CallEvent, Campaign, TrackingNumber
- Statistics aggregation (total calls, avg duration, success rate)
- Tracking number management (create, list, assign to campaigns)

Architecture:
- FastAPI 0.104+ (Python 3.13)
- SQLAlchemy 2.x for ORM
- SQLite for local storage (upgradeable to PostgreSQL)
- Option-2-Flow compliant (opena1 → opena2 → kordp → calltrackp)
- Safepoint archiving for all operations

PORTIER 3.0 Policies:
✅ Port-Policy: 12355 (allowed: 12344-12399, forbidden: 8080)
✅ Option-2-Flow: All commands via opena1 → opena2 → kordp
✅ Safepoint: Append-only archiving to archivp_store
✅ Strict JSON: extra="forbid" in all Pydantic models
✅ ENV-only: DB credentials, Bearer token from .env
✅ Logging: Structured, JSON-ready, secret masking
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
import uvicorn

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS & CONFIG
# ──────────────────────────────────────────────────────────────────────────────

PORT = 12356
KUERZEL = "calltrackp"
AGENT_ID = "opena10"

# Port-Policy Enforcement (PORTIER 3.0)
PORTS_ALLOWED = list(range(12344, 12400))
PORT_FORBIDDEN = 8080

if PORT not in PORTS_ALLOWED:
    print(f"❌ FATAL: Port {PORT} nicht im erlaubten Bereich {PORTS_ALLOWED[0]}-{PORTS_ALLOWED[-1]}")
    sys.exit(1)

if PORT == PORT_FORBIDDEN:
    print(f"❌ FATAL: Port {PORT_FORBIDDEN} ist exklusiv für OpenWebUI UI reserviert")
    sys.exit(1)

# ENV-only Secrets
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
if not BEARER_TOKEN:
    print("⚠️  WARNING: BEARER_TOKEN nicht gesetzt (Security deaktiviert)")

DB_URL = os.getenv("CALLTRACK_DB_URL", "sqlite:///./data/calltracking.db")
ARCHIVP_ROOT = os.getenv("ARCHIVP_ROOT", "../1.opena1&2_portier/archivp_store")

# Logging Setup
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s – %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(AGENT_ID)

# ──────────────────────────────────────────────────────────────────────────────
# SQLALCHEMY MODELS
# ──────────────────────────────────────────────────────────────────────────────

Base = declarative_base()


class Campaign(Base):
    """Campaign Model - Marketing campaigns with tracking numbers"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)

    # Relationships
    tracking_numbers = relationship("TrackingNumber", back_populates="campaign")
    call_events = relationship("CallEvent", back_populates="campaign")


class TrackingNumber(Base):
    """Tracking Number Model - Phone numbers assigned to campaigns"""
    __tablename__ = "tracking_numbers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(20), unique=True, nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    description = Column(String(300), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    active = Column(Boolean, default=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="tracking_numbers")
    call_events = relationship("CallEvent", back_populates="tracking_number_obj")

    __table_args__ = (
        Index("idx_tracking_campaign", "campaign_id"),
    )


class CallEvent(Base):
    """Call Event Model - Individual call records"""
    __tablename__ = "call_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(String(100), unique=True, nullable=False, index=True)
    tracking_number = Column(String(20), ForeignKey("tracking_numbers.number"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    caller_number = Column(String(20), nullable=True)  # Masked: +4912345****
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False)  # completed, busy, no-answer, failed
    timestamp = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    extra_data = Column(String(1000), nullable=True)  # JSON string for extra data (renamed from 'metadata')

    # Relationships
    campaign = relationship("Campaign", back_populates="call_events")
    tracking_number_obj = relationship("TrackingNumber", back_populates="call_events")

    __table_args__ = (
        Index("idx_call_campaign", "campaign_id"),
        Index("idx_call_timestamp", "timestamp"),
        Index("idx_call_status", "status"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# DATABASE SETUP
# ──────────────────────────────────────────────────────────────────────────────

# Create engine
engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})

# Create all tables
Base.metadata.create_all(bind=engine)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# PYDANTIC MODELS (Strict JSON - extra="forbid")
# ──────────────────────────────────────────────────────────────────────────────

class CallEventIngest(BaseModel):
    """Model for ingesting call events from opena9 or external sources"""
    model_config = ConfigDict(extra="forbid")

    call_id: str = Field(..., description="Unique call ID from telephony provider")
    tracking_number: str = Field(..., description="Tracking phone number (E.164 format)")
    caller_number: Optional[str] = Field(None, description="Caller phone number (masked)")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Call duration in seconds")
    status: str = Field(..., description="Call status: completed, busy, no-answer, failed")
    timestamp: str = Field(..., description="ISO 8601 timestamp (UTC)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["completed", "busy", "no-answer", "failed", "canceled"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v


class TrackingNumberCreate(BaseModel):
    """Model for creating tracking numbers"""
    model_config = ConfigDict(extra="forbid")

    number: str = Field(..., description="Phone number in E.164 format")
    campaign_id: str = Field(..., description="Campaign ID to assign this number to")
    description: Optional[str] = Field(None, max_length=300, description="Optional description")


class CampaignCreate(BaseModel):
    """Model for creating campaigns"""
    model_config = ConfigDict(extra="forbid")

    campaign_id: str = Field(..., max_length=100, description="Unique campaign identifier")
    name: str = Field(..., max_length=200, description="Campaign name")
    description: Optional[str] = Field(None, max_length=500, description="Campaign description")


class CommandRequest(BaseModel):
    """Generic command request for Option-2-Flow integration"""
    model_config = ConfigDict(extra="forbid")

    command: str = Field(..., description="Command to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")


# ──────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ──────────────────────────────────────────────────────────────────────────────

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Bearer token verification"""
    if not BEARER_TOKEN:
        return True  # Security disabled if no token configured
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return True


# ──────────────────────────────────────────────────────────────────────────────
# SAFEPOINT ARCHIVING
# ──────────────────────────────────────────────────────────────────────────────

def write_safepoint(direction: str, data: Dict[str, Any], sp_type: str):
    """Write safepoint to archivp_store (append-only, YYYY/MM/DD structure)"""
    try:
        now = datetime.now(timezone.utc)
        date_path = now.strftime("%Y/%m/%d")
        ts = int(now.timestamp() * 1000)

        # Unicode arrow → (U+2192)
        filename = f"SP{ts:015d}_{AGENT_ID}→{direction}_{sp_type}.json"

        full_path = Path(ARCHIVP_ROOT) / date_path
        full_path.mkdir(parents=True, exist_ok=True)

        file_path = full_path / filename

        envelope = {
            "sp_id": str(ts),
            "timestamp": now.isoformat(),
            "source": AGENT_ID,
            "destination": direction,
            "type": sp_type,
            "data": data
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2, ensure_ascii=False)

        logger.info(f"📦 Safepoint: {filename}")

    except Exception as e:
        logger.error(f"❌ Safepoint-Fehler: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# STARTUP / SHUTDOWN
# ──────────────────────────────────────────────────────────────────────────────

startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle handler for startup/shutdown"""
    logger.info(f"🚀 Starting {AGENT_ID} on port {PORT}")
    logger.info(f"🚀 {AGENT_ID} (Call Tracking Agent) startet...")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Kürzel: {KUERZEL}")
    logger.info(f"   DB: {DB_URL}")
    logger.info(f"   Archiv: {ARCHIVP_ROOT}")
    logger.info(f"✅ {AGENT_ID} bereit!")
    yield
    logger.info(f"🛑 {AGENT_ID} wird heruntergefahren...")


# ──────────────────────────────────────────────────────────────────────────────
# FASTAPI APP
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"{AGENT_ID} (Call Tracking Agent)",
    description="Call Tracking, SQLAlchemy-Models, Campaign-Tracking",
    version="1.0.0",
    lifespan=lifespan
)


# ──────────────────────────────────────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Agent info endpoint (public)"""
    return {
        "agent": AGENT_ID,
        "kuerzel": KUERZEL,
        "port": PORT,
        "status": "running",
        "capabilities": [
            "events/ingest",
            "stats/summary",
            "stats/by_campaign",
            "tracking_numbers/list",
            "tracking_numbers/create",
            "campaigns/create",
            "campaigns/list"
        ],
        "database": {
            "type": "sqlite" if "sqlite" in DB_URL else "postgresql",
            "url": DB_URL.replace(os.getenv("DB_PASSWORD", ""), "***") if "DB_PASSWORD" in os.environ else DB_URL
        }
    }


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check endpoint"""
    uptime = time.time() - startup_time

    # Check DB connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "agent": AGENT_ID,
        "port": PORT,
        "kuerzel": KUERZEL,
        "uptime": round(uptime, 2),
        "database": db_status
    }


@app.post("/command")
async def command(req: CommandRequest, _auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Generic command endpoint for Option-2-Flow integration
    
    Receives commands from opena1 → opena2 → kordp
    """
    write_safepoint("opena2", {"command": req.command, "params": req.params}, "CMD")

    result = {
        "status": "executed",
        "command": req.command,
        "agent": AGENT_ID,
        "result": "Command received (use specific endpoints for call tracking operations)"
    }

    write_safepoint("opena2", result, "RESP")

    return result


@app.post("/events/ingest")
async def ingest_event(event: CallEventIngest, _auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Ingest call event from opena9 or external telephony system
    
    Creates CallEvent record linked to tracking number and campaign
    """
    write_safepoint("opena9", event.model_dump(), "CMD")

    # Check for duplicate call_id
    existing = db.query(CallEvent).filter(CallEvent.call_id == event.call_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Call ID {event.call_id} already exists")

    # Find tracking number
    tracking_num = db.query(TrackingNumber).filter(TrackingNumber.number == event.tracking_number).first()
    if not tracking_num:
        raise HTTPException(status_code=404, detail=f"Tracking number {event.tracking_number} not found")

    # Parse timestamp
    try:
        timestamp = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format (use ISO 8601)")

    # Create CallEvent
    call_event = CallEvent(
        call_id=event.call_id,
        tracking_number=event.tracking_number,
        campaign_id=tracking_num.campaign_id,
        caller_number=event.caller_number,
        duration_seconds=event.duration_seconds,
        status=event.status,
        timestamp=timestamp,
        extra_data=json.dumps(event.metadata) if event.metadata else None
    )

    db.add(call_event)
    db.commit()
    db.refresh(call_event)

    result = {
        "status": "success",
        "event_id": call_event.id,
        "call_id": call_event.call_id,
        "campaign_id": tracking_num.campaign.campaign_id,
        "ingested_at": call_event.ingested_at.isoformat()
    }

    write_safepoint("opena9", result, "RESP")

    return result


@app.get("/stats/summary")
async def stats_summary(_auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Get overall call statistics
    
    Returns total calls, avg duration, success rate
    """
    write_safepoint("opena1", {"endpoint": "stats/summary"}, "CMD")

    total_calls = db.query(func.count(CallEvent.id)).scalar() or 0
    avg_duration = db.query(func.avg(CallEvent.duration_seconds)).scalar() or 0
    completed_calls = db.query(func.count(CallEvent.id)).filter(CallEvent.status == "completed").scalar() or 0

    success_rate = (completed_calls / total_calls * 100) if total_calls > 0 else 0

    result = {
        "total_calls": total_calls,
        "avg_duration_seconds": round(avg_duration, 2),
        "completed_calls": completed_calls,
        "success_rate_percent": round(success_rate, 2)
    }

    write_safepoint("opena1", result, "RESP")

    return result


@app.get("/stats/by_campaign")
async def stats_by_campaign(campaign_id: Optional[str] = None, _auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Get statistics by campaign
    
    If campaign_id provided, returns stats for that campaign only
    Otherwise returns stats for all campaigns
    """
    write_safepoint("opena1", {"endpoint": "stats/by_campaign", "campaign_id": campaign_id}, "CMD")

    query = db.query(
        Campaign.campaign_id,
        Campaign.name,
        func.count(CallEvent.id).label("total_calls"),
        func.avg(CallEvent.duration_seconds).label("avg_duration"),
        func.count(CallEvent.id).filter(CallEvent.status == "completed").label("completed_calls")
    ).join(CallEvent, Campaign.id == CallEvent.campaign_id, isouter=True).group_by(Campaign.id)

    if campaign_id:
        query = query.filter(Campaign.campaign_id == campaign_id)

    results = query.all()

    campaigns_stats = []
    for row in results:
        total = row.total_calls or 0
        completed = row.completed_calls or 0
        success_rate = (completed / total * 100) if total > 0 else 0

        campaigns_stats.append({
            "campaign_id": row.campaign_id,
            "campaign_name": row.name,
            "total_calls": total,
            "avg_duration_seconds": round(row.avg_duration or 0, 2),
            "completed_calls": completed,
            "success_rate_percent": round(success_rate, 2)
        })

    result = {"campaigns": campaigns_stats}

    write_safepoint("opena1", result, "RESP")

    return result


@app.get("/tracking_numbers/list")
async def list_tracking_numbers(_auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """List all tracking numbers with campaign assignments"""
    write_safepoint("opena1", {"endpoint": "tracking_numbers/list"}, "CMD")

    tracking_nums = db.query(TrackingNumber).join(Campaign).all()

    result = {
        "tracking_numbers": [
            {
                "number": tn.number,
                "campaign_id": tn.campaign.campaign_id,
                "campaign_name": tn.campaign.name,
                "description": tn.description,
                "active": tn.active,
                "created_at": tn.created_at.isoformat()
            }
            for tn in tracking_nums
        ]
    }

    write_safepoint("opena1", result, "RESP")

    return result


@app.post("/tracking_numbers/create")
async def create_tracking_number(req: TrackingNumberCreate, _auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """Create a new tracking number assigned to a campaign"""
    write_safepoint("opena1", req.model_dump(), "CMD")

    # Check for duplicate
    existing = db.query(TrackingNumber).filter(TrackingNumber.number == req.number).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Tracking number {req.number} already exists")

    # Find campaign
    campaign = db.query(Campaign).filter(Campaign.campaign_id == req.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {req.campaign_id} not found")

    # Create tracking number
    tracking_num = TrackingNumber(
        number=req.number,
        campaign_id=campaign.id,
        description=req.description
    )

    db.add(tracking_num)
    db.commit()
    db.refresh(tracking_num)

    result = {
        "status": "success",
        "tracking_number": {
            "id": tracking_num.id,
            "number": tracking_num.number,
            "campaign_id": campaign.campaign_id,
            "description": tracking_num.description,
            "created_at": tracking_num.created_at.isoformat()
        }
    }

    write_safepoint("opena1", result, "RESP")

    return result


@app.post("/campaigns/create")
async def create_campaign(req: CampaignCreate, _auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """Create a new campaign"""
    write_safepoint("opena1", req.model_dump(), "CMD")

    # Check for duplicate
    existing = db.query(Campaign).filter(Campaign.campaign_id == req.campaign_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Campaign {req.campaign_id} already exists")

    # Create campaign
    campaign = Campaign(
        campaign_id=req.campaign_id,
        name=req.name,
        description=req.description
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    result = {
        "status": "success",
        "campaign": {
            "id": campaign.id,
            "campaign_id": campaign.campaign_id,
            "name": campaign.name,
            "description": campaign.description,
            "created_at": campaign.created_at.isoformat()
        }
    }

    write_safepoint("opena1", result, "RESP")

    return result


@app.get("/campaigns/list")
async def list_campaigns(_auth: bool = Depends(verify_token), db: Session = Depends(get_db)):
    """List all campaigns"""
    write_safepoint("opena1", {"endpoint": "campaigns/list"}, "CMD")

    campaigns = db.query(Campaign).all()

    result = {
        "campaigns": [
            {
                "campaign_id": c.campaign_id,
                "name": c.name,
                "description": c.description,
                "active": c.active,
                "created_at": c.created_at.isoformat()
            }
            for c in campaigns
        ]
    }

    write_safepoint("opena1", result, "RESP")

    return result


# ──────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
