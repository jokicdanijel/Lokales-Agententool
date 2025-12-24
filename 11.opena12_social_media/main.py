#!/usr/bin/env python3
"""
📱 OPENA12 Social Media Agent - PORTIER PAS-6.0
Port: 12358 | Kürzel: smp | Version: 6.0.0

Multi-Platform Social Media Automation:
- LinkedIn, X (Twitter), Facebook, Instagram
- AI-Powered Post Generation
- Scheduling & Queue Management
- Media Handling
- Analytics & Metrics
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ============================================================================
# CONFIGURATION
# ============================================================================

PORT = int(os.getenv("OPENA12_PORT", "12357"))
HOST = os.getenv("OPENA12_HOST", "0.0.0.0")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_OPENA12", os.getenv("OPENAI_API_KEY", ""))

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("opena12")

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class CommandRequest(BaseModel):
    """Generic command request"""

    action: str
    params: dict[str, Any] = Field(default_factory=dict)


class PostRequest(BaseModel):
    """Post request model"""

    platforms: list[str]
    text: str
    hashtags: list[str] | None = None
    media: list[str] | None = None


class ScheduleRequest(BaseModel):
    """Schedule request model"""

    platforms: list[str]
    text: str
    when: str  # ISO timestamp
    hashtags: list[str] | None = None


class SpecializedRequest(BaseModel):
    """Specialized action request"""

    action: str
    topic: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# LAZY MODULE IMPORTS
# ============================================================================

_social_core = None
_scheduler = None
_metrics = None
_media_handler = None


def get_social_core():
    global _social_core
    if _social_core is None:
        from modules.social_core import SocialCore

        _social_core = SocialCore()
    return _social_core


def get_scheduler():
    global _scheduler
    if _scheduler is None:
        from modules.scheduler import Scheduler

        _scheduler = Scheduler(get_social_core())
    return _scheduler


def get_metrics():
    global _metrics
    if _metrics is None:
        from modules.metrics import get_metrics as gm

        _metrics = gm()
    return _metrics


def get_media_handler():
    global _media_handler
    if _media_handler is None:
        from modules.media_handler import MediaHandler

        _media_handler = MediaHandler()
    return _media_handler


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info(f"🚀 opena12 (smp) starting on {HOST}:{PORT}")
    logger.info("📱 Platforms: LinkedIn, X, Facebook, Instagram")
    logger.info(f"🤖 OpenAI: {'configured' if OPENAI_API_KEY else 'not configured'}")
    yield
    logger.info("👋 opena12 shutting down")


app = FastAPI(
    title="opena12_social_media",
    description="Social Media Automation Agent - PORTIER PAS-6.0",
    version="6.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

START_TIME = time.time()

# ============================================================================
# STATIC FILES
# ============================================================================

# Mount HTML dashboard
html_path = os.path.join(os.path.dirname(__file__), "html")
if os.path.exists(html_path):
    app.mount("/html", StaticFiles(directory=html_path), name="html")

# ============================================================================
# CORE ENDPOINTS - PAS-6.0
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint - serve HTML dashboard"""
    html_path = os.path.join(os.path.dirname(__file__), "html")
    if os.path.exists(os.path.join(html_path, "index.html")):
        return FileResponse(os.path.join(html_path, "index.html"))
    else:
        # Fallback to JSON if HTML not found
        return {
            "service": "opena12",
            "name": "Social Media Agent",
            "kürzel": "smp",
            "version": "6.0.0",
            "standard": "PAS-6.0",
            "port": PORT,
            "status": "operational",
            "platforms": ["linkedin", "x", "facebook", "instagram"],
            "endpoints": ["/health", "/status", "/command", "/specialized", "/metrics", "/logs"],
        }


@app.get("/health")
async def health():
    """Health check endpoint"""
    core = get_social_core()
    scheduler = get_scheduler()

    return {
        "status": "healthy",
        "agent": "opena12_social_media",
        "kürzel": "smp",
        "version": "6.0.0",
        "port": PORT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "queued_posts": scheduler.count(),
        "platforms": core.platforms(),
        "openai_configured": bool(OPENAI_API_KEY),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/status")
async def status():
    """Detailed status endpoint"""
    core = get_social_core()
    scheduler = get_scheduler()
    metrics = get_metrics()

    return {
        "agent": "opena12_social_media",
        "version": "6.0.0",
        "status": "operational",
        "uptime": {
            "seconds": round(time.time() - START_TIME, 2),
            "started_at": datetime.fromtimestamp(START_TIME).isoformat(),
        },
        "platforms": {p: {"status": "connected", "limit": core.get_limit(p)} for p in core.platforms()},
        "scheduler": {"queued": scheduler.count(), "pending": scheduler.pending_count()},
        "metrics_summary": metrics.get_summary(),
    }


@app.post("/command")
async def command(payload: CommandRequest):
    """Execute command - PAS-6.0 standard"""
    action = payload.action.lower()
    params = payload.params

    core = get_social_core()
    scheduler = get_scheduler()
    metrics = get_metrics()

    try:
        if action == "post":
            result = await core.post_now(
                platforms=params.get("platforms", []),
                text=params.get("text", ""),
                hashtags=params.get("hashtags"),
                media=params.get("media"),
            )
            metrics.increment("posts_created")
            return result

        elif action == "schedule":
            result = scheduler.schedule(
                platforms=params.get("platforms", []),
                text=params.get("text", ""),
                when=params.get("when", ""),
                hashtags=params.get("hashtags"),
            )
            metrics.increment("posts_scheduled")
            return result

        elif action == "cancel":
            job_id = params.get("job_id")
            result = scheduler.cancel(job_id)
            return result

        elif action == "list_queue":
            return {"queue": scheduler.dump()}

        elif action == "platforms":
            return {"platforms": core.platforms_info()}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    except Exception as e:
        logger.error(f"Command error: {e}")
        metrics.increment("errors")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/specialized")
async def specialized(payload: SpecializedRequest):
    """Specialized actions - AI features"""
    action = payload.action.lower()
    core = get_social_core()
    metrics = get_metrics()

    try:
        if action == "generate_text":
            result = await core.generate_text(payload.topic or "")
            metrics.increment("ai_generations")
            return result

        elif action == "generate_hashtags":
            result = await core.generate_hashtags(payload.topic or "")
            return result

        elif action == "optimize_post":
            result = await core.optimize_post(
                text=payload.params.get("text", ""), platform=payload.params.get("platform", "linkedin")
            )
            return result

        elif action == "analyze_engagement":
            result = await core.analyze_engagement(payload.params.get("post_id"))
            return result

        else:
            raise HTTPException(status_code=400, detail=f"Unknown specialized action: {action}")

    except Exception as e:
        logger.error(f"Specialized error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics_endpoint():
    """Metrics endpoint"""
    return get_metrics().get_detailed()


@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Prometheus format metrics"""
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(get_metrics().to_prometheus_format(), media_type="text/plain")


@app.get("/logs")
async def logs():
    """Get recent activity logs"""
    core = get_social_core()
    return {"logs": core.logs()}


@app.get("/config")
async def config():
    """Get configuration (safe values only)"""
    return {
        "port": PORT,
        "host": HOST,
        "openai_configured": bool(OPENAI_API_KEY),
        "platforms": get_social_core().platforms(),
        "character_limits": get_social_core().get_all_limits(),
    }


# ============================================================================
# CONVENIENCE ENDPOINTS
# ============================================================================


@app.post("/post")
async def post_now(req: PostRequest):
    """Direct post endpoint"""
    core = get_social_core()
    return await core.post_now(platforms=req.platforms, text=req.text, hashtags=req.hashtags, media=req.media)


@app.post("/schedule")
async def schedule_post(req: ScheduleRequest):
    """Direct schedule endpoint"""
    scheduler = get_scheduler()
    return scheduler.schedule(platforms=req.platforms, text=req.text, when=req.when, hashtags=req.hashtags)


@app.get("/queue")
async def get_queue():
    """Get scheduled posts queue"""
    return {"queue": get_scheduler().dump()}


# ============================================================================
# HTML DASHBOARD
# ============================================================================


@app.get("/dashboard")
async def dashboard():
    """Redirect to dashboard"""
    return FileResponse(os.path.join(html_path, "index.html"))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
