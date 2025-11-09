"""
opena12_Influencer: Influencer Management Agent
Campaign creation, performance tracking, ROI calculation, audience analysis
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import json
import urllib.request
from datetime import datetime
from typing import Optional, List
import os
import sys
import secrets

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena12_Influencer",
    version="1.0.0",
    description="Influencer Management Agent - Campaign & Performance"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12360
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_influencers: dict = {}
_campaigns: dict = {}
_performance_data: dict = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class InfluencerCreateRequest(BaseModel):
    name: str
    platform: str
    follower_count: int
    engagement_rate: float
    category: str


class CampaignCreateRequest(BaseModel):
    name: str
    influencer_ids: List[str]
    budget: float
    duration_days: int
    target_audience: str


class PerformanceQueryRequest(BaseModel):
    campaign_id: str


class ROICalculationRequest(BaseModel):
    campaign_id: str


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
            "src": "opena12_influencer",
            "dst": "opena2",
            "kind": "INFLUENCER_OP",
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


def _generate_influencer_id() -> str:
    """Generate unique influencer ID"""
    return f"INF_{secrets.token_hex(6).upper()}"


def _generate_campaign_id() -> str:
    """Generate unique campaign ID"""
    return f"CMP_{secrets.token_hex(6).upper()}"


def _calculate_reach(influencer_ids: List[str]) -> int:
    """Calculate total reach"""
    total = 0
    for inf_id in influencer_ids:
        if inf_id in _influencers:
            total += _influencers[inf_id].get("follower_count", 0)
    return total


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena12_Influencer",
        "port": PORT,
        "influencers": len(_influencers),
        "campaigns": len(_campaigns),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/influencers/list")
async def list_influencers(authorization: str = Header(None)):
    """List all influencers"""
    _validate_token(authorization)
    
    try:
        influencers_list = [
            {**v, "id": k} for k, v in _influencers.items()
        ]
        
        logger.info(f"📋 Influencers listed: {len(influencers_list)}")
        
        return {
            "strict": True,
            "influencers": influencers_list,
            "count": len(influencers_list),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ List influencers failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/campaign/create")
async def create_campaign(req: CampaignCreateRequest, authorization: str = Header(None)):
    """Create new campaign"""
    _validate_token(authorization)
    
    try:
        campaign_id = _generate_campaign_id()
        reach = _calculate_reach(req.influencer_ids)
        
        campaign_entry = {
            "name": req.name,
            "influencer_ids": req.influencer_ids,
            "budget": req.budget,
            "duration_days": req.duration_days,
            "target_audience": req.target_audience,
            "created_at": datetime.utcnow().isoformat(),
            "reach": reach,
            "status": "active"
        }
        
        _campaigns[campaign_id] = campaign_entry
        logger.info(f"🎯 Campaign created: {campaign_id} (reach: {reach})")
        
        await _archive({
            "op": "CAMPAIGN_CREATE",
            "campaign_id": campaign_id,
            "influencer_count": len(req.influencer_ids),
            "budget": req.budget,
            "reach": reach
        })
        
        return {
            "strict": True,
            "campaign_id": campaign_id,
            "created": True,
            "reach": reach,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Campaign creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/performance/track")
async def track_performance(req: PerformanceQueryRequest, authorization: str = Header(None)):
    """Track campaign performance"""
    _validate_token(authorization)
    
    try:
        if req.campaign_id not in _campaigns:
            raise HTTPException(status_code=404, detail=f"Campaign {req.campaign_id} not found")
        
        campaign = _campaigns[req.campaign_id]
        
        # Simulated performance metrics
        performance = {
            "campaign_id": req.campaign_id,
            "impressions": int(campaign["reach"] * 0.8),
            "clicks": int(campaign["reach"] * 0.15),
            "conversions": int(campaign["reach"] * 0.05),
            "engagement_rate": 0.12,
            "sentiment_score": 0.78
        }
        
        _performance_data[req.campaign_id] = performance
        logger.info(f"📊 Performance tracked: {req.campaign_id}")
        
        await _archive({
            "op": "PERFORMANCE_TRACK",
            "campaign_id": req.campaign_id,
            "impressions": performance["impressions"],
            "conversions": performance["conversions"]
        })
        
        return {
            "strict": True,
            "performance": performance,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Performance tracking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/roi/calculate")
async def calculate_roi(req: ROICalculationRequest, authorization: str = Header(None)):
    """Calculate ROI for campaign"""
    _validate_token(authorization)
    
    try:
        if req.campaign_id not in _campaigns:
            raise HTTPException(status_code=404, detail=f"Campaign {req.campaign_id} not found")
        
        campaign = _campaigns[req.campaign_id]
        perf = _performance_data.get(req.campaign_id, {})
        
        conversions = perf.get("conversions", 0)
        avg_order_value = 50.0  # Simulated
        revenue = conversions * avg_order_value
        
        roi = ((revenue - campaign["budget"]) / campaign["budget"] * 100) if campaign["budget"] > 0 else 0
        
        roi_data = {
            "campaign_id": req.campaign_id,
            "budget_spent": campaign["budget"],
            "revenue_generated": revenue,
            "roi_percentage": roi,
            "roi_status": "positive" if roi > 0 else "negative"
        }
        
        logger.info(f"💰 ROI calculated: {req.campaign_id} (ROI: {roi:.1f}%)")
        
        await _archive({
            "op": "ROI_CALCULATE",
            "campaign_id": req.campaign_id,
            "roi_percentage": roi,
            "revenue": revenue
        })
        
        return {
            "strict": True,
            "roi": roi_data,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ROI calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audience/analyze")
async def analyze_audience(req: PerformanceQueryRequest, authorization: str = Header(None)):
    """Analyze campaign audience"""
    _validate_token(authorization)
    
    try:
        if req.campaign_id not in _campaigns:
            raise HTTPException(status_code=404, detail=f"Campaign {req.campaign_id} not found")
        
        campaign = _campaigns[req.campaign_id]
        
        audience_data = {
            "campaign_id": req.campaign_id,
            "target_audience": campaign["target_audience"],
            "demographics": {
                "age_18_24": 0.25,
                "age_25_34": 0.40,
                "age_35_44": 0.20,
                "age_45_plus": 0.15
            },
            "interests": ["Technology", "Lifestyle", "Fashion", "Business"],
            "geographic": {
                "US": 0.45,
                "EU": 0.35,
                "APAC": 0.20
            }
        }
        
        logger.info(f"👥 Audience analyzed: {req.campaign_id}")
        
        return {
            "strict": True,
            "audience": audience_data,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Audience analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena12_Influencer",
        "version": "1.0.0",
        "port": PORT,
        "influencers": len(_influencers),
        "campaigns": len(_campaigns),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    # Pre-populate some influencers for testing
    _influencers["INF_TEST001"] = {
        "name": "TechInfluencer",
        "platform": "twitter",
        "follower_count": 100000,
        "engagement_rate": 0.08,
        "category": "technology"
    }
    
    logger.info(f"🚀 Starting opena12_Influencer on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
