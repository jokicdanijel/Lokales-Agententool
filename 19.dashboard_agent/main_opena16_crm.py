"""
opena16_CRM: Customer Relationship Management Agent
Customer lifecycle management, deal tracking, interaction logging
GitHub Pattern: agentverse-clean (AVGenAI) + Multi-Agent-Bot
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import json
import urllib.request
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
import sys
import secrets

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena16_CRM",
    version="1.0.0",
    description="CRM Agent - Customer & Deal Management"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12364
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_customers: Dict[str, dict] = {}
_deals: Dict[str, dict] = {}
_interactions: Dict[str, List[dict]] = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class Customer(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    lifecycle_stage: str = "prospect"  # prospect, lead, customer, churned


class CustomerUpdateRequest(BaseModel):
    customer_id: str
    lifecycle_stage: Optional[str] = None
    company: Optional[str] = None


class Deal(BaseModel):
    customer_id: str
    title: str
    amount: float
    stage: str = "lead"  # lead, qualification, proposal, negotiation, won, lost
    close_date: str


class DealUpdateRequest(BaseModel):
    deal_id: str
    stage: str


class InteractionLogRequest(BaseModel):
    customer_id: str
    interaction_type: str  # email, call, meeting, note
    notes: str
    outcome: str


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
            "src": "opena16_crm",
            "dst": "opena2",
            "kind": "CRM_OP",
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


def _generate_customer_id() -> str:
    """Generate unique customer ID"""
    return f"CUST_{secrets.token_hex(6).upper()}"


def _generate_deal_id() -> str:
    """Generate unique deal ID"""
    return f"DEAL_{secrets.token_hex(6).upper()}"


def _calculate_customer_value(customer_id: str) -> float:
    """Calculate total customer value from deals"""
    total = 0.0
    for deal in _deals.values():
        if deal.get("customer_id") == customer_id and deal.get("stage") == "won":
            total += deal.get("amount", 0.0)
    return total


def _get_customer_interactions(customer_id: str) -> List[dict]:
    """Get all interactions for a customer"""
    return _interactions.get(customer_id, [])


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena16_CRM",
        "port": PORT,
        "customers": len(_customers),
        "deals": len(_deals),
        "interactions": sum(len(v) for v in _interactions.values()),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/customer/create")
async def create_customer(req: Customer, authorization: str = Header(None)):
    """Create new customer"""
    _validate_token(authorization)
    
    try:
        customer_id = _generate_customer_id()
        
        customer_entry = {
            "id": customer_id,
            "name": req.name,
            "email": req.email,
            "phone": req.phone,
            "company": req.company,
            "lifecycle_stage": req.lifecycle_stage,
            "total_value": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "last_contact": None
        }
        
        _customers[customer_id] = customer_entry
        _interactions[customer_id] = []
        
        logger.info(f"👤 Customer created: {customer_id} ({req.name})")
        
        await _archive({
            "op": "CUSTOMER_CREATE",
            "customer_id": customer_id,
            "name": req.name,
            "company": req.company,
            "lifecycle_stage": req.lifecycle_stage
        })
        
        return {
            "strict": True,
            "customer_id": customer_id,
            "created": True,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Customer creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customer/{customer_id}")
async def get_customer(customer_id: str, authorization: str = Header(None)):
    """Get customer details"""
    _validate_token(authorization)
    
    try:
        if customer_id not in _customers:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        customer = _customers[customer_id]
        customer["total_value"] = _calculate_customer_value(customer_id)
        customer["interactions_count"] = len(_interactions.get(customer_id, []))
        
        logger.info(f"📋 Customer retrieved: {customer_id}")
        
        return {
            "strict": True,
            "customer": customer,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Customer retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/customer/{customer_id}/contact")
async def log_interaction(customer_id: str, req: InteractionLogRequest, authorization: str = Header(None)):
    """Log customer interaction"""
    _validate_token(authorization)
    
    try:
        if customer_id not in _customers:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        interaction = {
            "type": req.interaction_type,
            "notes": req.notes,
            "outcome": req.outcome,
            "logged_at": datetime.utcnow().isoformat()
        }
        
        if customer_id not in _interactions:
            _interactions[customer_id] = []
        
        _interactions[customer_id].append(interaction)
        _customers[customer_id]["last_contact"] = datetime.utcnow().isoformat()
        
        logger.info(f"📞 Interaction logged: {customer_id} ({req.interaction_type})")
        
        await _archive({
            "op": "INTERACTION_LOGGED",
            "customer_id": customer_id,
            "type": req.interaction_type,
            "outcome": req.outcome
        })
        
        return {
            "strict": True,
            "customer_id": customer_id,
            "interaction_logged": True,
            "interaction_type": req.interaction_type,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Interaction logging failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deal/create")
async def create_deal(req: Deal, authorization: str = Header(None)):
    """Create sales deal"""
    _validate_token(authorization)
    
    try:
        if req.customer_id not in _customers:
            raise HTTPException(status_code=404, detail=f"Customer {req.customer_id} not found")
        
        deal_id = _generate_deal_id()
        
        deal_entry = {
            "id": deal_id,
            "customer_id": req.customer_id,
            "title": req.title,
            "amount": req.amount,
            "stage": req.stage,
            "close_date": req.close_date,
            "created_at": datetime.utcnow().isoformat(),
            "won_at": None
        }
        
        _deals[deal_id] = deal_entry
        
        logger.info(f"🤝 Deal created: {deal_id} ({req.title}, ${req.amount:.2f})")
        
        await _archive({
            "op": "DEAL_CREATE",
            "deal_id": deal_id,
            "customer_id": req.customer_id,
            "title": req.title,
            "amount": req.amount,
            "stage": req.stage
        })
        
        return {
            "strict": True,
            "deal_id": deal_id,
            "created": True,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Deal creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/deal/{deal_id}")
async def get_deal(deal_id: str, authorization: str = Header(None)):
    """Get deal details"""
    _validate_token(authorization)
    
    try:
        if deal_id not in _deals:
            raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
        
        deal = _deals[deal_id]
        customer = _customers.get(deal.get("customer_id"), {})
        
        deal["customer_name"] = customer.get("name", "Unknown")
        deal["customer_company"] = customer.get("company", "Unknown")
        
        logger.info(f"📊 Deal retrieved: {deal_id}")
        
        return {
            "strict": True,
            "deal": deal,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Deal retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deal/{deal_id}/update")
async def update_deal(deal_id: str, req: DealUpdateRequest, authorization: str = Header(None)):
    """Update deal status"""
    _validate_token(authorization)
    
    try:
        if deal_id not in _deals:
            raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
        
        deal = _deals[deal_id]
        old_stage = deal.get("stage")
        deal["stage"] = req.stage
        deal["updated_at"] = datetime.utcnow().isoformat()
        
        if req.stage == "won":
            deal["won_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Deal updated: {deal_id} ({old_stage} → {req.stage})")
        
        await _archive({
            "op": "DEAL_UPDATE",
            "deal_id": deal_id,
            "old_stage": old_stage,
            "new_stage": req.stage,
            "customer_id": deal.get("customer_id"),
            "amount": deal.get("amount")
        })
        
        return {
            "strict": True,
            "deal_id": deal_id,
            "updated": True,
            "new_stage": req.stage,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Deal update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    # Calculate statistics
    leads_count = sum(1 for c in _customers.values() if c.get("lifecycle_stage") == "lead")
    customers_count = sum(1 for c in _customers.values() if c.get("lifecycle_stage") == "customer")
    pipeline_value = sum(d.get("amount", 0) for d in _deals.values() if d.get("stage") != "lost")
    won_deals = sum(1 for d in _deals.values() if d.get("stage") == "won")
    
    return {
        "service": "opena16_CRM",
        "version": "1.0.0",
        "port": PORT,
        "total_customers": len(_customers),
        "leads": leads_count,
        "customers": customers_count,
        "total_deals": len(_deals),
        "won_deals": won_deals,
        "pipeline_value": pipeline_value,
        "endpoints": 7,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    # Pre-populate test data
    test_cust_id = _generate_customer_id()
    _customers[test_cust_id] = {
        "id": test_cust_id,
        "name": "Acme Corporation",
        "email": "contact@acme.com",
        "phone": "+1-555-0100",
        "company": "Acme Corp",
        "lifecycle_stage": "customer",
        "total_value": 0.0,
        "created_at": datetime.utcnow().isoformat(),
        "last_contact": None
    }
    _interactions[test_cust_id] = []
    
    logger.info(f"🚀 Starting opena16_CRM on port {PORT}")
    logger.info(f"📦 Pre-loaded 1 test customer")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
