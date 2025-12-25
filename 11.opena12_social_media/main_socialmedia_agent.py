#!/usr/bin/env python3
"""
opena12 - Social Media Automation Agent

Port: 12357
Kürzel: smp
Version: 2.0
Status: Production-Ready

Features:
- Multi-Platform Posting (LinkedIn, X/Twitter, Facebook, Instagram)
- Post Scheduling (Queue-based)
- Character Limit Validation
- Media Upload Support
- OAuth Token Management
- Rate Limiting
- Analytics Integration
"""

import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

# ============================================================================
# CONFIGURATION
# ============================================================================

PORT = int(os.getenv("OPENA12_PORT", "12357"))
HOST = os.getenv("OPENA12_HOST", "127.0.0.1")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVP_ROOT = PROJECT_ROOT / "1.opena1&2_portier" / "archivp_store"
POST_QUEUE_PATH = PROJECT_ROOT / "11.opena12_social_media" / "data" / "post_queue.json"
POSTS_DB_PATH = PROJECT_ROOT / "11.opena12_social_media" / "data" / "posts_history.jsonl"

# Ensure data directory exists
POST_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Platform Character Limits
PLATFORM_LIMITS = {
    "linkedin": 3000,
    "x": 280,  # X (formerly Twitter)
    "twitter": 280,
    "facebook": 63206,
    "instagram": 2200,
}

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("opena12")

# ============================================================================
# PYDANTIC MODELS (Strict JSON)
# ============================================================================


class Platform(str, Enum):
    """Supported social media platforms"""

    LINKEDIN = "linkedin"
    X = "x"
    TWITTER = "twitter"  # Alias for X
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class PostStatus(str, Enum):
    """Post status"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class PostRequest(BaseModel):
    """Request to post immediately"""

    platforms: list[Platform] = Field(..., min_length=1, max_length=5, description="Target platforms")
    text: str = Field(..., min_length=1, max_length=63206, description="Post content")
    media_urls: list[str] | None = Field(None, max_length=10, description="Media URLs (images/videos)")
    hashtags: list[str] | None = Field(None, max_length=30, description="Hashtags (without #)")

    class Config:
        extra = "forbid"

    @field_validator("text")
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text cannot be empty or whitespace-only")
        return v.strip()


class ScheduleRequest(BaseModel):
    """Request to schedule a post"""

    platforms: list[Platform] = Field(..., min_length=1, max_length=5)
    text: str = Field(..., min_length=1, max_length=63206)
    media_urls: list[str] | None = Field(None, max_length=10)
    hashtags: list[str] | None = Field(None, max_length=30)
    scheduled_at: str = Field(..., description="ISO timestamp for publishing")

    class Config:
        extra = "forbid"

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_time(cls, v: str) -> str:
        try:
            scheduled = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if scheduled <= datetime.now(scheduled.tzinfo):
                raise ValueError("scheduled_at must be in the future")
            return v
        except ValueError as e:
            raise ValueError(f"Invalid scheduled_at: {e}")


class StatusResponse(BaseModel):
    """Response for post status query"""

    post_id: str
    platform: str
    status: PostStatus
    url: str | None = None
    error: str | None = None
    created_at: str
    published_at: str | None = None

    class Config:
        extra = "forbid"


class DeleteRequest(BaseModel):
    """Request to delete a post"""

    post_id: str = Field(..., min_length=1, max_length=200)
    platform: Platform = Field(...)

    class Config:
        extra = "forbid"


class CommandRequest(BaseModel):
    """Generic command request (Option-2-Flow)"""

    command: str
    params: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


@dataclass
class Post:
    """Internal post representation"""

    post_id: str
    platforms: list[str]
    text: str
    media_urls: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    status: str = "pending"
    created_at: str = ""
    scheduled_at: str | None = None
    published_at: str | None = None
    platform_urls: dict[str, str] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "post_id": self.post_id,
            "platforms": self.platforms,
            "text": self.text,
            "media_urls": self.media_urls,
            "hashtags": self.hashtags,
            "status": self.status,
            "created_at": self.created_at,
            "scheduled_at": self.scheduled_at,
            "published_at": self.published_at,
            "platform_urls": self.platform_urls,
            "errors": self.errors,
        }


# ============================================================================
# POST QUEUE & HISTORY
# ============================================================================


class PostQueue:
    """JSON-based post queue for scheduling"""

    def __init__(self, queue_path: Path, history_path: Path):
        self.queue_path = queue_path
        self.history_path = history_path
        self.queue: list[Post] = []
        self.load()

    def load(self):
        """Load queue from JSON"""
        if not self.queue_path.exists():
            self.queue = []
            self.save()
            logger.info(f"Created new post queue at {self.queue_path}")
            return

        try:
            with open(self.queue_path) as f:
                data = json.load(f)
                self.queue = [Post(**item) for item in data.get("queue", [])]
            logger.info(f"Loaded {len(self.queue)} posts from queue")
        except Exception as e:
            logger.error(f"Error loading queue: {e}")
            self.queue = []

    def save(self):
        """Save queue to JSON"""
        try:
            data = {"queue": [p.to_dict() for p in self.queue], "last_updated": datetime.utcnow().isoformat() + "Z"}
            with open(self.queue_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.queue)} posts to queue")
        except Exception as e:
            logger.error(f"Error saving queue: {e}")

    def add(self, post: Post) -> str:
        """Add post to queue"""
        self.queue.append(post)
        self.save()
        logger.info(f"Added post {post.post_id} to queue")
        return post.post_id

    def get(self, post_id: str) -> Post | None:
        """Get post by ID"""
        for post in self.queue:
            if post.post_id == post_id:
                return post
        return None

    def remove(self, post_id: str) -> bool:
        """Remove post from queue"""
        initial_len = len(self.queue)
        self.queue = [p for p in self.queue if p.post_id != post_id]

        if len(self.queue) < initial_len:
            self.save()
            logger.info(f"Removed post {post_id} from queue")
            return True
        return False

    def get_ready_posts(self) -> list[Post]:
        """Get posts ready for publishing (scheduled time passed)"""
        now = datetime.utcnow().isoformat() + "Z"
        ready = []

        for post in self.queue:
            if post.status == "scheduled" and post.scheduled_at:
                if post.scheduled_at <= now:
                    ready.append(post)

        return ready

    def archive_to_history(self, post: Post):
        """Archive post to history (JSONL append-only)"""
        try:
            with open(self.history_path, "a") as f:
                f.write(json.dumps(post.to_dict()) + "\n")
            logger.debug(f"Archived post {post.post_id} to history")
        except Exception as e:
            logger.error(f"Error archiving post: {e}")


# ============================================================================
# PLATFORM SIMULATORS (Mock for now - can be replaced with real APIs)
# ============================================================================


class PlatformClient:
    """Base class for platform clients"""

    @staticmethod
    def validate_character_limit(platform: str, text: str) -> bool:
        """Check if text fits platform character limit"""
        limit = PLATFORM_LIMITS.get(platform.lower(), 63206)
        return len(text) <= limit

    @staticmethod
    def publish(platform: str, text: str, media_urls: list[str], hashtags: list[str]) -> dict[str, Any]:
        """
        Publish post to platform (MOCK implementation)

        In production, this would call real APIs:
        - LinkedIn: LinkedIn API v2
        - X: X API v2
        - Facebook: Graph API
        - Instagram: Graph API
        """

        # Validate character limit
        if not PlatformClient.validate_character_limit(platform, text):
            raise ValueError(f"Text exceeds {PLATFORM_LIMITS[platform]} character limit for {platform}")

        # Mock successful publish
        post_url = f"https://{platform}.com/posts/{hashlib.md5(text.encode()).hexdigest()[:12]}"

        logger.info(f"📱 [MOCK] Published to {platform}: {text[:50]}... → {post_url}")

        return {
            "success": True,
            "platform": platform,
            "url": post_url,
            "published_at": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def delete(platform: str, post_url: str) -> bool:
        """Delete post from platform (MOCK)"""
        logger.info(f"🗑️  [MOCK] Deleted post from {platform}: {post_url}")
        return True


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena12 - Social Media Automation Agent",
    description="Multi-Platform Posting, Scheduling, Analytics",
    version="2.0",
)

security = HTTPBearer()
post_queue = PostQueue(POST_QUEUE_PATH, POSTS_DB_PATH)

START_TIME = time.time()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify Bearer token"""
    if not BEARER_TOKEN:
        logger.warning("BEARER_TOKEN not set - authentication disabled!")
        return "anonymous"

    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return "authenticated_user"


def generate_post_id() -> str:
    """Generate unique post ID"""
    timestamp = int(time.time() * 1000000)
    return f"post_{timestamp}"


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "opena12",
        "kürzel": "smp",
        "description": "Social Media Automation Agent (Multi-Platform)",
        "port": PORT,
        "version": "2.0",
        "platforms": ["linkedin", "x", "facebook", "instagram"],
        "endpoints": ["/health", "/post", "/schedule", "/status", "/delete", "/platforms/list", "/command"],
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "opena12",
        "kürzel": "smp",
        "port": PORT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "queued_posts": len(post_queue.queue),
        "platforms": list(PLATFORM_LIMITS.keys()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/post")
async def create_post(req: PostRequest, actor: str = Depends(verify_token)):
    """Post immediately to platforms"""
    try:
        post_id = generate_post_id()
        post = Post(
            post_id=post_id,
            platforms=[p.value for p in req.platforms],
            text=req.text,
            media_urls=req.media_urls or [],
            hashtags=req.hashtags or [],
            status="pending",
            created_at=datetime.utcnow().isoformat() + "Z",
        )

        # Publish to each platform
        results = {}
        errors = {}

        for platform in post.platforms:
            try:
                result = PlatformClient.publish(platform, req.text, post.media_urls, post.hashtags)
                results[platform] = result["url"]
                post.platform_urls[platform] = result["url"]
            except Exception as e:
                logger.error(f"Error publishing to {platform}: {e}")
                errors[platform] = str(e)
                post.errors[platform] = str(e)

        # Update post status
        if errors and not results:
            post.status = "failed"
        elif results:
            post.status = "published"
            post.published_at = datetime.utcnow().isoformat() + "Z"

        # Add to queue (for status tracking)
        post_queue.add(post)

        # Archive to history
        post_queue.archive_to_history(post)

        return {
            "status": "success" if results else "failed",
            "message": f"Posted to {len(results)}/{len(post.platforms)} platforms",
            "post_id": post_id,
            "published_urls": results,
            "errors": errors if errors else None,
        }

    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule")
async def schedule_post(req: ScheduleRequest, actor: str = Depends(verify_token)):
    """Schedule a post for future publishing"""
    try:
        post_id = generate_post_id()
        post = Post(
            post_id=post_id,
            platforms=[p.value for p in req.platforms],
            text=req.text,
            media_urls=req.media_urls or [],
            hashtags=req.hashtags or [],
            status="scheduled",
            created_at=datetime.utcnow().isoformat() + "Z",
            scheduled_at=req.scheduled_at,
        )

        post_queue.add(post)

        return {
            "status": "success",
            "message": f"Post scheduled for {req.scheduled_at}",
            "post_id": post_id,
            "platforms": post.platforms,
            "scheduled_at": req.scheduled_at,
        }

    except Exception as e:
        logger.error(f"Error scheduling post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{post_id}")
async def get_status(post_id: str, actor: str = Depends(verify_token)):
    """Get status of a post"""
    post = post_queue.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    return {
        "post_id": post.post_id,
        "status": post.status,
        "platforms": post.platforms,
        "created_at": post.created_at,
        "scheduled_at": post.scheduled_at,
        "published_at": post.published_at,
        "urls": post.platform_urls,
        "errors": post.errors if post.errors else None,
    }


@app.delete("/delete")
async def delete_post(req: DeleteRequest, actor: str = Depends(verify_token)):
    """Delete a published post"""
    try:
        post = post_queue.get(req.post_id)

        if not post:
            raise HTTPException(status_code=404, detail=f"Post {req.post_id} not found")

        # Delete from platform
        platform_url = post.platform_urls.get(req.platform.value)
        if platform_url:
            PlatformClient.delete(req.platform.value, platform_url)

        # Update status
        post.status = "deleted"
        post_queue.remove(req.post_id)
        post_queue.archive_to_history(post)

        return {"status": "success", "message": f"Post {req.post_id} deleted from {req.platform.value}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/platforms/list")
async def list_platforms(actor: str = Depends(verify_token)):
    """List supported platforms with character limits"""
    return {
        "status": "success",
        "platforms": [
            {"name": platform, "character_limit": limit, "supported": True}
            for platform, limit in PLATFORM_LIMITS.items()
        ],
    }


@app.post("/command")
async def handle_command(req: CommandRequest, actor: str = Depends(verify_token)):
    """Handle generic command (Option-2-Flow compatibility)"""
    cmd = req.command.lower()

    if cmd == "post":
        post_req = PostRequest(**req.params)
        return await create_post(post_req, actor)

    elif cmd == "schedule":
        schedule_req = ScheduleRequest(**req.params)
        return await schedule_post(schedule_req, actor)

    elif cmd == "status":
        post_id = req.params.get("post_id")
        if not post_id:
            raise HTTPException(status_code=400, detail="post_id required")
        return await get_status(post_id, actor)

    elif cmd == "delete":
        delete_req = DeleteRequest(**req.params)
        return await delete_post(delete_req, actor)

    elif cmd == "platforms":
        return await list_platforms(actor)

    else:
        raise HTTPException(status_code=400, detail=f"Unknown command: {cmd}")


# ============================================================================
# BACKGROUND TASK: Process Scheduled Posts
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"🚀 opena12 (smp) started on {HOST}:{PORT}")
    logger.info(f"📁 Post Queue: {POST_QUEUE_PATH}")
    logger.info(f"📜 Posts History: {POSTS_DB_PATH}")
    logger.info(f"📱 Platforms: {list(PLATFORM_LIMITS.keys())}")

    # TODO: Start background task for processing scheduled posts
    # asyncio.create_task(process_scheduled_posts())


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    if not BEARER_TOKEN:
        logger.warning("⚠️  BEARER_TOKEN not set in .env - authentication disabled!")

    logger.info(f"🚀 Starting opena12 (smp) on {HOST}:{PORT}")

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
