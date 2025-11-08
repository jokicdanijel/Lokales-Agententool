"""
opena11_SocialMedia: Social Media Agent
Twitter/Facebook integration, posting, scheduling, trending analysis
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import json
import urllib.request
from datetime import datetime, timedelta
from typing import Optional, List
import os
import sys
import secrets
import hashlib

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena11_SocialMedia",
    version="1.0.0",
    description="Social Media Agent - Twitter/Facebook Integration"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12359
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_posts: List[dict] = []
_scheduled_posts: dict = {}
_analytics: dict = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class PostCreateRequest(BaseModel):
    content: str
    platform: str = "twitter"  # twitter, facebook, both
    media_url: Optional[str] = None


class PostScheduleRequest(BaseModel):
    content: str
    platform: str
    scheduled_time: str  # ISO 8601


class AnalyticsQueryRequest(BaseModel):
    post_id: str
    metric: str = "impressions"  # impressions, likes, shares, comments


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: Optional[str]):
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
            "src": "opena11_social_media",
            "dst": "opena2",
            "kind": "SOCIAL_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"}
        }
        
        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_post_id() -> str:
    """Generate unique post ID"""
    return f"POST_{secrets.token_hex(8).upper()}"


def _get_trending_topics() -> List[str]:
    """Simulated trending topics"""
    return [
        "#AI", "#Python", "#FastAPI", "#WebDevelopment", "#Technology",
        "#Innovation", "#StartupLife", "#DevOps", "#CloudComputing", "#MachineLearning"
    ]


def _analyze_sentiment(text: str) -> dict:
    """Simple sentiment analysis"""
    positive_words = ["great", "awesome", "love", "excellent", "fantastic", "amazing"]
    negative_words = ["bad", "hate", "terrible", "awful", "horrible", "disappointing"]
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "sentiment": sentiment,
        "confidence": 0.75 + (pos_count + neg_count) * 0.05
    }


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena11_SocialMedia",
        "port": PORT,
        "total_posts": len(_posts),
        "scheduled_posts": len(_scheduled_posts),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/post/create")
async def create_post(req: PostCreateRequest, authorization: str = Header(None)):
    """Create and publish post"""
    _validate_token(authorization)
    
    try:
        post_id = _generate_post_id()
        sentiment = _analyze_sentiment(req.content)
        
        post_entry = {
            "id": post_id,
            "content": req.content,
            "platform": req.platform,
            "media_url": req.media_url,
            "created_at": datetime.utcnow().isoformat(),
            "sentiment": sentiment,
            "engagement": {
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "impressions": 0
            }
        }
        
        _posts.append(post_entry)
        logger.info(f"📱 Post created: {post_id} ({req.platform})")
        
        await _archive({
            "op": "POST_CREATE",
            "post_id": post_id,
            "platform": req.platform,
            "content_len": len(req.content),
            "sentiment": sentiment["sentiment"]
        })
        
        return {
            "strict": True,
            "post_id": post_id,
            "published": True,
            "platform": req.platform,
            "sentiment": sentiment,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Post creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/post/schedule")
async def schedule_post(req: PostScheduleRequest, authorization: str = Header(None)):
    """Schedule post for later"""
    _validate_token(authorization)
    
    try:
        post_id = _generate_post_id()
        
        scheduled_entry = {
            "id": post_id,
            "content": req.content,
            "platform": req.platform,
            "scheduled_time": req.scheduled_time,
            "created_at": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }
        
        _scheduled_posts[post_id] = scheduled_entry
        logger.info(f"📅 Post scheduled: {post_id} for {req.scheduled_time}")
        
        await _archive({
            "op": "POST_SCHEDULE",
            "post_id": post_id,
            "scheduled_time": req.scheduled_time,
            "platform": req.platform
        })
        
        return {
            "strict": True,
            "post_id": post_id,
            "scheduled": True,
            "platform": req.platform,
            "scheduled_time": req.scheduled_time,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Scheduling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trending")
async def get_trending(authorization: str = Header(None)):
    """Get trending topics"""
    _validate_token(authorization)
    
    try:
        topics = _get_trending_topics()
        logger.info(f"📊 Trending topics retrieved: {len(topics)}")
        
        return {
            "strict": True,
            "trending": topics,
            "count": len(topics),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Trending retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analytics")
async def get_analytics(req: AnalyticsQueryRequest, authorization: str = Header(None)):
    """Get post analytics"""
    _validate_token(authorization)
    
    try:
        # Find post
        post = next((p for p in _posts if p["id"] == req.post_id), None)
        if not post:
            raise HTTPException(status_code=404, detail=f"Post {req.post_id} not found")
        
        analytics = {
            "post_id": req.post_id,
            "platform": post["platform"],
            "metric": req.metric,
            "value": post["engagement"].get(req.metric, 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"📈 Analytics retrieved: {req.post_id} ({req.metric})")
        
        await _archive({
            "op": "ANALYTICS_QUERY",
            "post_id": req.post_id,
            "metric": req.metric
        })
        
        return {
            "strict": True,
            "analytics": analytics,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth")
async def get_auth_status(authorization: str = Header(None)):
    """Get authentication status with social media platforms"""
    _validate_token(authorization)
    
    return {
        "strict": True,
        "authenticated": {
            "twitter": True,
            "facebook": True,
            "instagram": False
        },
        "rate_limits": {
            "twitter": 450,
            "facebook": 200
        },
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena11_SocialMedia",
        "version": "1.0.0",
        "port": PORT,
        "total_posts": len(_posts),
        "scheduled_posts": len(_scheduled_posts),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena11_SocialMedia on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
