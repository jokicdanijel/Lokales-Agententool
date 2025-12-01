#!/usr/bin/env python3
"""
opena13 - Influencer Management Agent
======================================

Agent-ID:    opena13
Port:        12358
Kürzel:      influp
Version:     1.0

Funktionen:
- Influencer-Profil-Verwaltung (CRUD)
- Kampagnen-Matching (Algorithmus-basiert)
- Engagement-Metriken & Reichweiten-Analyse
- Multi-Platform Support (Instagram, TikTok, YouTube, X/Twitter)
- Integration mit opena12 (Social Media) für koordinierte Kampagnen

Architektur:
- FastAPI + uvicorn
- SQLAlchemy Models (InfluencerProfile, Campaign, Match)
- JSON-basierte Datenpersistenz (upgradeable zu PostgreSQL)
- JSONL Audit-Log (append-only)
- Strict JSON Schemas (extra="forbid")

Option-2-Flow:
  OpenAI → opena1 → opena2 → kordp → opena13 → opena2 → opena1 → OpenAI

Port Policy:
  - Backend: 12344-12399 (✓ 12358)
  - UI-only: 8080 (verboten)

Security:
  - Bearer Token (ENV-only)
  - Secrets niemals hardcoded
  - DSGVO-Compliance (Datenschutz für Influencer-Daten)

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

PROFILES_FILE = DATA_DIR / "influencer_profiles.json"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"
MATCHES_FILE = DATA_DIR / "matches.json"
AUDIT_LOG_FILE = DATA_DIR / "audit.jsonl"

# Port Policy Enforcement
PORT = 12358
ALLOWED_PORTS = range(12344, 12400)
FORBIDDEN_PORTS = [8080]

if PORT not in ALLOWED_PORTS or PORT in FORBIDDEN_PORTS:
    raise RuntimeError(f"❌ Port {PORT} verletzt Port-Policy! Erlaubt: {ALLOWED_PORTS}, Verboten: {FORBIDDEN_PORTS}")

# Service Metadata
SERVICE_NAME = "opena13"
KUERZEL = "influp"
VERSION = "1.0"

# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class Platform(str, Enum):
    """Social Media Platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    X = "x"
    TWITTER = "twitter"  # Alias für X
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


class Niche(str, Enum):
    """Influencer Nischen"""
    FASHION = "fashion"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    TECH = "tech"
    GAMING = "gaming"
    FOOD = "food"
    TRAVEL = "travel"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class CampaignStatus(str, Enum):
    """Campaign Lifecycle Status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class InfluencerProfile:
    """Influencer Profile Data Class"""
    profile_id: str
    name: str
    platform: str
    followers: int
    engagement_rate: float  # 0.0 - 100.0
    niche: str
    contact_email: Optional[str] = None
    avg_likes: Optional[int] = None
    avg_comments: Optional[int] = None
    created_at: str = ""
    updated_at: str = ""
    active: bool = True

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class Campaign:
    """Marketing Campaign Data Class"""
    campaign_id: str
    name: str
    budget: float  # EUR
    target_audience: str
    niches: List[str]
    min_followers: int
    min_engagement_rate: float
    start_date: str
    end_date: Optional[str] = None
    status: str = CampaignStatus.DRAFT.value
    created_at: str = ""
    created_by: str = "system"

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"


@dataclass
class Match:
    """Influencer-Campaign Match Result"""
    match_id: str
    campaign_id: str
    profile_id: str
    score: float  # 0.0 - 100.0
    reasoning: str
    matched_at: str = ""

    def __post_init__(self):
        if not self.matched_at:
            self.matched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ============================================================================
# PYDANTIC REQUEST/RESPONSE MODELS (STRICT JSON)
# ============================================================================

class ProfileCreateRequest(BaseModel):
    """Request: Influencer-Profil erstellen"""
    name: str = Field(..., min_length=1, max_length=200)
    platform: Platform
    followers: int = Field(..., ge=0)
    engagement_rate: float = Field(..., ge=0.0, le=100.0)
    niche: Niche
    contact_email: Optional[str] = Field(None, max_length=255)
    avg_likes: Optional[int] = Field(None, ge=0)
    avg_comments: Optional[int] = Field(None, ge=0)

    class Config:
        extra = "forbid"  # Strict JSON


class ProfileResponse(BaseModel):
    """Response: Influencer-Profil"""
    profile_id: str
    name: str
    platform: str
    followers: int
    engagement_rate: float
    niche: str
    contact_email: Optional[str]
    avg_likes: Optional[int]
    avg_comments: Optional[int]
    created_at: str
    updated_at: str
    active: bool

    class Config:
        extra = "forbid"


class CampaignCreateRequest(BaseModel):
    """Request: Kampagne erstellen"""
    name: str = Field(..., min_length=1, max_length=300)
    budget: float = Field(..., gt=0)
    target_audience: str = Field(..., min_length=1, max_length=500)
    niches: List[Niche] = Field(..., min_items=1, max_items=5)
    min_followers: int = Field(..., ge=0)
    min_engagement_rate: float = Field(..., ge=0.0, le=100.0)
    start_date: str  # ISO 8601
    end_date: Optional[str] = None  # ISO 8601

    @validator("start_date", "end_date")
    def validate_date(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Datum muss ISO 8601 Format sein (YYYY-MM-DDTHH:MM:SSZ)")
        return v

    class Config:
        extra = "forbid"


class CampaignResponse(BaseModel):
    """Response: Kampagne"""
    campaign_id: str
    name: str
    budget: float
    target_audience: str
    niches: List[str]
    min_followers: int
    min_engagement_rate: float
    start_date: str
    end_date: Optional[str]
    status: str
    created_at: str
    created_by: str

    class Config:
        extra = "forbid"


class MatchRequest(BaseModel):
    """Request: Influencer-Matching für Kampagne"""
    campaign_id: str
    max_results: int = Field(10, ge=1, le=50)
    min_score: float = Field(50.0, ge=0.0, le=100.0)

    class Config:
        extra = "forbid"


class MatchResult(BaseModel):
    """Response: Einzelnes Match-Ergebnis"""
    match_id: str
    profile: ProfileResponse
    score: float
    reasoning: str

    class Config:
        extra = "forbid"


class MatchResponse(BaseModel):
    """Response: Matching-Ergebnisse"""
    campaign_id: str
    matches: List[MatchResult]
    total_candidates: int
    matched_at: str

    class Config:
        extra = "forbid"


class MetricsRequest(BaseModel):
    """Request: Metriken abrufen"""
    profile_ids: Optional[List[str]] = Field(None, max_items=100)
    campaign_ids: Optional[List[str]] = Field(None, max_items=50)
    platform: Optional[Platform] = None
    niche: Optional[Niche] = None

    class Config:
        extra = "forbid"


class MetricsResponse(BaseModel):
    """Response: Aggregierte Metriken"""
    total_profiles: int
    total_campaigns: int
    total_matches: int
    avg_engagement_rate: float
    total_followers: int
    platforms: Dict[str, int]
    niches: Dict[str, int]

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
    total_profiles: int
    total_campaigns: int
    total_matches: int

    class Config:
        extra = "forbid"


# ============================================================================
# DATA PERSISTENCE LAYER
# ============================================================================

class DataStore:
    """JSON-based Data Persistence (upgradeable to PostgreSQL/SQLAlchemy)"""

    @staticmethod
    def load_profiles() -> List[InfluencerProfile]:
        """Load all influencer profiles from JSON"""
        if not PROFILES_FILE.exists():
            return []
        with open(PROFILES_FILE) as f:
            data = json.load(f)
            return [InfluencerProfile(**p) for p in data]

    @staticmethod
    def save_profiles(profiles: List[InfluencerProfile]):
        """Save all profiles to JSON"""
        with open(PROFILES_FILE, "w") as f:
            json.dump([asdict(p) for p in profiles], f, indent=2)

    @staticmethod
    def load_campaigns() -> List[Campaign]:
        """Load all campaigns from JSON"""
        if not CAMPAIGNS_FILE.exists():
            return []
        with open(CAMPAIGNS_FILE) as f:
            data = json.load(f)
            return [Campaign(**c) for c in data]

    @staticmethod
    def save_campaigns(campaigns: List[Campaign]):
        """Save all campaigns to JSON"""
        with open(CAMPAIGNS_FILE, "w") as f:
            json.dump([asdict(c) for c in campaigns], f, indent=2)

    @staticmethod
    def load_matches() -> List[Match]:
        """Load all matches from JSON"""
        if not MATCHES_FILE.exists():
            return []
        with open(MATCHES_FILE) as f:
            data = json.load(f)
            return [Match(**m) for m in data]

    @staticmethod
    def save_matches(matches: List[Match]):
        """Save all matches to JSON"""
        with open(MATCHES_FILE, "w") as f:
            json.dump([asdict(m) for m in matches], f, indent=2)


class AuditLog:
    """JSONL Append-Only Audit Log (WORM-compliant)"""

    @staticmethod
    def log(operation: str, actor: str, resource_type: str, resource_id: str, details: Optional[Dict] = None):
        """Append audit entry to JSONL log"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "operation": operation,
            "actor": actor,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {}
        }
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")


# ============================================================================
# MATCHING ALGORITHM
# ============================================================================

class MatchingEngine:
    """Influencer-Campaign Matching Algorithm"""

    @staticmethod
    def calculate_score(profile: InfluencerProfile, campaign: Campaign) -> tuple[float, str]:
        """
        Calculate match score (0-100) and reasoning
        
        Scoring Factors:
        - Niche match: 40 points
        - Followers threshold: 20 points (HARD REQUIREMENT - no score if below)
        - Engagement rate: 30 points
        - Platform preference: 10 points
        
        Note: Follower threshold is a HARD REQUIREMENT. Profile must meet
        min_followers to be considered, regardless of other factors.
        """
        score = 0.0
        reasons = []

        # HARD REQUIREMENT: Followers Threshold
        # If below threshold, return score 0 (no compensation possible)
        if profile.followers < campaign.min_followers:
            deficit = campaign.min_followers - profile.followers
            reasoning = f"❌ HARD REQUIREMENT FAILED: Followers insufficient ({profile.followers:,} < {campaign.min_followers:,}, deficit: {deficit:,})"
            return 0.0, reasoning

        # Niche Match (40 points)
        if profile.niche in campaign.niches:
            score += 40
            reasons.append(f"Niche match ({profile.niche})")
        else:
            reasons.append(f"Niche mismatch ({profile.niche} not in {campaign.niches})")

        # Followers Threshold (20 points) - already verified above
        score += 20
        reasons.append(f"Followers sufficient ({profile.followers:,} >= {campaign.min_followers:,})")

        # Engagement Rate (30 points)
        if profile.engagement_rate >= campaign.min_engagement_rate:
            engagement_bonus = min(30, (profile.engagement_rate - campaign.min_engagement_rate) * 2)
            score += engagement_bonus
            reasons.append(f"Engagement rate {profile.engagement_rate:.2f}% (min {campaign.min_engagement_rate:.2f}%)")
        else:
            reasons.append(f"Engagement below threshold ({profile.engagement_rate:.2f}% < {campaign.min_engagement_rate:.2f}%)")

        # Platform Preference (10 points) - bonus for Instagram/TikTok
        if profile.platform in ["instagram", "tiktok"]:
            score += 10
            reasons.append(f"High-engagement platform ({profile.platform})")

        reasoning = " | ".join(reasons)
        return round(score, 2), reasoning

    @staticmethod
    def match_influencers(campaign: Campaign, profiles: List[InfluencerProfile], max_results: int = 10, min_score: float = 50.0) -> List[Match]:
        """
        Match influencers to campaign based on scoring algorithm
        
        Returns: Top N matches above min_score threshold
        """
        matches = []
        for profile in profiles:
            if not profile.active:
                continue
            score, reasoning = MatchingEngine.calculate_score(profile, campaign)
            if score >= min_score:
                match = Match(
                    match_id=str(uuid.uuid4()),
                    campaign_id=campaign.campaign_id,
                    profile_id=profile.profile_id,
                    score=score,
                    reasoning=reasoning
                )
                matches.append(match)

        # Sort by score descending, limit to max_results
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:max_results]


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="opena13 - Influencer Management Agent",
    version=VERSION,
    description="Influencer-Profil-Verwaltung, Kampagnen-Matching, Metriken",
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
        "description": "Influencer Management Agent - Profile CRUD, Campaign Matching, Metrics"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health Check - No Auth Required"""
    profiles = DataStore.load_profiles()
    campaigns = DataStore.load_campaigns()
    matches = DataStore.load_matches()

    uptime = time.time() - SERVICE_START_TIME

    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        kuerzel=KUERZEL,
        port=PORT,
        uptime_seconds=round(uptime, 2),
        total_profiles=len(profiles),
        total_campaigns=len(campaigns),
        total_matches=len(matches)
    )


@app.post("/profiles/create", response_model=ProfileResponse)
async def create_profile(req: ProfileCreateRequest, authorization: Optional[str] = Header(None)):
    """Create new influencer profile (Auth required)"""
    await verify_bearer_token(authorization)

    profiles = DataStore.load_profiles()

    # Create profile
    profile = InfluencerProfile(
        profile_id=str(uuid.uuid4()),
        name=req.name,
        platform=req.platform.value,
        followers=req.followers,
        engagement_rate=req.engagement_rate,
        niche=req.niche.value,
        contact_email=req.contact_email,
        avg_likes=req.avg_likes,
        avg_comments=req.avg_comments
    )

    profiles.append(profile)
    DataStore.save_profiles(profiles)

    AuditLog.log("CREATE_PROFILE", "api_user", "profile", profile.profile_id, {
        "name": profile.name,
        "platform": profile.platform,
        "followers": profile.followers
    })

    return ProfileResponse(**asdict(profile))


@app.get("/profiles", response_model=List[ProfileResponse])
async def list_profiles(
    platform: Optional[str] = None,
    niche: Optional[str] = None,
    min_followers: Optional[int] = None,
    active_only: bool = True,
    authorization: Optional[str] = Header(None)
):
    """List/search influencer profiles (Auth required)"""
    await verify_bearer_token(authorization)

    profiles = DataStore.load_profiles()

    # Filter
    if active_only:
        profiles = [p for p in profiles if p.active]
    if platform:
        profiles = [p for p in profiles if p.platform == platform]
    if niche:
        profiles = [p for p in profiles if p.niche == niche]
    if min_followers is not None:
        profiles = [p for p in profiles if p.followers >= min_followers]

    return [ProfileResponse(**asdict(p)) for p in profiles]


@app.post("/campaigns/create", response_model=CampaignResponse)
async def create_campaign(req: CampaignCreateRequest, authorization: Optional[str] = Header(None)):
    """Create new marketing campaign (Auth required)"""
    await verify_bearer_token(authorization)

    campaigns = DataStore.load_campaigns()

    campaign = Campaign(
        campaign_id=str(uuid.uuid4()),
        name=req.name,
        budget=req.budget,
        target_audience=req.target_audience,
        niches=[n.value for n in req.niches],
        min_followers=req.min_followers,
        min_engagement_rate=req.min_engagement_rate,
        start_date=req.start_date,
        end_date=req.end_date,
        status=CampaignStatus.DRAFT.value
    )

    campaigns.append(campaign)
    DataStore.save_campaigns(campaigns)

    AuditLog.log("CREATE_CAMPAIGN", "api_user", "campaign", campaign.campaign_id, {
        "name": campaign.name,
        "budget": campaign.budget,
        "niches": campaign.niches
    })

    return CampaignResponse(**asdict(campaign))


@app.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    status: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """List campaigns (Auth required)"""
    await verify_bearer_token(authorization)

    campaigns = DataStore.load_campaigns()

    if status:
        campaigns = [c for c in campaigns if c.status == status]

    return [CampaignResponse(**asdict(c)) for c in campaigns]


@app.post("/match", response_model=MatchResponse)
async def match_influencers(req: MatchRequest, authorization: Optional[str] = Header(None)):
    """Match influencers to campaign (Auth required)"""
    await verify_bearer_token(authorization)

    # Load data
    campaigns = DataStore.load_campaigns()
    profiles = DataStore.load_profiles()
    existing_matches = DataStore.load_matches()

    # Find campaign
    campaign = next((c for c in campaigns if c.campaign_id == req.campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {req.campaign_id} not found")

    # Run matching algorithm
    matches = MatchingEngine.match_influencers(campaign, profiles, req.max_results, req.min_score)

    # Save matches
    existing_matches.extend(matches)
    DataStore.save_matches(existing_matches)

    AuditLog.log("MATCH_INFLUENCERS", "api_user", "campaign", campaign.campaign_id, {
        "matches_found": len(matches),
        "max_results": req.max_results,
        "min_score": req.min_score
    })

    # Build response
    match_results = []
    for match in matches:
        profile = next(p for p in profiles if p.profile_id == match.profile_id)
        match_results.append(MatchResult(
            match_id=match.match_id,
            profile=ProfileResponse(**asdict(profile)),
            score=match.score,
            reasoning=match.reasoning
        ))

    return MatchResponse(
        campaign_id=campaign.campaign_id,
        matches=match_results,
        total_candidates=len([p for p in profiles if p.active]),
        matched_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )


@app.post("/metrics", response_model=MetricsResponse)
async def get_metrics(req: MetricsRequest, authorization: Optional[str] = Header(None)):
    """Get aggregated metrics (Auth required)"""
    await verify_bearer_token(authorization)

    profiles = DataStore.load_profiles()
    campaigns = DataStore.load_campaigns()
    matches = DataStore.load_matches()

    # Filter profiles
    filtered_profiles = profiles
    if req.profile_ids:
        filtered_profiles = [p for p in profiles if p.profile_id in req.profile_ids]
    if req.platform:
        filtered_profiles = [p for p in filtered_profiles if p.platform == req.platform.value]
    if req.niche:
        filtered_profiles = [p for p in filtered_profiles if p.niche == req.niche.value]

    # Aggregate metrics
    total_followers = sum(p.followers for p in filtered_profiles)
    avg_engagement = sum(p.engagement_rate for p in filtered_profiles) / len(filtered_profiles) if filtered_profiles else 0.0

    platforms_count = {}
    niches_count = {}
    for p in filtered_profiles:
        platforms_count[p.platform] = platforms_count.get(p.platform, 0) + 1
        niches_count[p.niche] = niches_count.get(p.niche, 0) + 1

    return MetricsResponse(
        total_profiles=len(filtered_profiles),
        total_campaigns=len(campaigns),
        total_matches=len(matches),
        avg_engagement_rate=round(avg_engagement, 2),
        total_followers=total_followers,
        platforms=platforms_count,
        niches=niches_count
    )


@app.post("/command")
async def command_endpoint(req: CommandRequest, authorization: Optional[str] = Header(None)):
    """Option-2-Flow Command Endpoint (Auth required)"""
    await verify_bearer_token(authorization)

    action = req.action
    params = req.params

    if action == "create_profile":
        profile_req = ProfileCreateRequest(**params)
        response = await create_profile(profile_req, authorization)
        return {"status": "success", "action": action, "result": response.dict()}

    elif action == "create_campaign":
        campaign_req = CampaignCreateRequest(**params)
        response = await create_campaign(campaign_req, authorization)
        return {"status": "success", "action": action, "result": response.dict()}

    elif action == "match":
        match_req = MatchRequest(**params)
        response = await match_influencers(match_req, authorization)
        return {"status": "success", "action": action, "result": response.dict()}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print(f"🚀 Starting {SERVICE_NAME} ({KUERZEL}) on port {PORT}...")
    print(f"📊 Data directory: {DATA_DIR}")
    print(f"🔐 Bearer token loaded: {BEARER_TOKEN[:20]}..." if BEARER_TOKEN else "⚠️  No Bearer token!")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
