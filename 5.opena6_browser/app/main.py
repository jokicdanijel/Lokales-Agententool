"""
opena6 Main FastAPI Application
Browser Automation Agent — REST API & Orchestration
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from .config import config
from .models import (
    PlaybookRequest, PlaybookResponse, HealthResponse, ReadyResponse,
    CancelRequest, CancelResponse, Safepoint
)
from .browser_client import get_executor, BrowserExecutor

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create logs directory
log_dir = Path(config.LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)

# FastAPI app
app = FastAPI(
    title="opena6 — Browser Automation Agent",
    version="1.0.0",
    description="Deterministic web automation with compliance enforcement"
)

# Global state
browser_executor: Optional[BrowserExecutor] = None
active_runs: Dict[str, asyncio.Task] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize browser executor on app startup"""
    global browser_executor
    try:
        browser_executor = await get_executor()
        logger.info("✅ opena6 Browser Executor initialized")
        
        # Register route with opena1 (coordinator)
        await register_route_with_opena1()
    except Exception as e:
        logger.error(f"❌ Failed to start opena6: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup browser executor on app shutdown"""
    global browser_executor
    try:
        if browser_executor:
            await browser_executor.shutdown()
            logger.info("✅ opena6 Browser Executor shut down")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


async def register_route_with_opena1():
    """Register this agent's route with the coordinator (opena1)"""
    try:
        import httpx
        
        route_data = {
            "agent_id": config.SERVICE_NAME,
            "endpoint": f"http://127.0.0.1:{config.PORT}",
            "component": config.SERVICE_COMPONENT,
            "status": "healthy"
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{config.OPENA1_URL}/route/update",
                json=route_data
            )
            if response.status_code == 200:
                logger.info(f"✅ Registered with opena1: {route_data}")
            else:
                logger.warning(f"⚠️  opena1 registration returned {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️  Could not register with opena1: {e}")


async def write_safepoint_to_opena2(safepoint: Safepoint):
    """Write safepoint to archivator (opena2)"""
    try:
        import httpx
        
        payload = {
            "src": safepoint.src,
            "dst": safepoint.dst,
            "kind": safepoint.kind,
            "payload": safepoint.payload
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{config.OPENA2_URL}/store/archivp",
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Safepoint written to opena2: {result.get('path')}")
            else:
                logger.warning(f"⚠️  opena2 write returned {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️  Could not write safepoint to opena2: {e}")


# ============================================================================
# HEALTH & READINESS ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        service=config.SERVICE_NAME,
        status="ok",
        component=config.SERVICE_COMPONENT,
        port=config.PORT,
        browser="playwright-chromium",
        ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )


@app.get("/ready")
async def readiness_check() -> ReadyResponse:
    """Readiness check endpoint"""
    return ReadyResponse(
        ready=browser_executor is not None,
        browser="playwright-chromium",
        version="1.0.0"
    )


# ============================================================================
# CONTROL PLANE ENDPOINTS
# ============================================================================

@app.post("/run")
async def execute_playbook(request: PlaybookRequest) -> PlaybookResponse:
    """
    Execute a browser automation playbook
    
    Request format:
    {
        "request_id": "uuid",
        "steps": [
            {"action": "goto", "url": "https://example.org", "wait": "load"},
            {"action": "screenshot", "label": "homepage"}
        ],
        "compliance": {
            "allow_domains": ["example.org"],
            "obey_robots": true
        },
        "archiv": {
            "attach_screenshot": true,
            "attach_html": true
        }
    }
    """
    
    if not browser_executor:
        raise HTTPException(status_code=503, detail="Browser executor not ready")
    
    try:
        # Execute playbook
        response = await browser_executor.execute_playbook(request)
        
        # Write RESP safepoint to opena2
        safepoint = Safepoint(
            ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            src=config.SERVICE_NAME,
            dst="opena2",
            kind="RESP",
            request_id=request.request_id,
            payload=response.dict()
        )
        await write_safepoint_to_opena2(safepoint)
        
        # Log event
        logger.info(f"✅ Playbook executed: {request.request_id} → {response.status}")
        
        return response
    
    except Exception as e:
        logger.error(f"❌ Playbook execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cancel")
async def cancel_playbook(request: CancelRequest) -> CancelResponse:
    """
    Cancel a running playbook execution
    
    Currently: simple response (full cancellation requires session tracking)
    """
    
    return CancelResponse(
        request_id=request.request_id,
        canceled=False,  # Placeholder
        at_step=None
    )


# ============================================================================
# OBSERVABILITY ENDPOINTS
# ============================================================================

@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    
    # Placeholder: return mock metrics
    metrics_text = """# HELP opena6_runs_total Total playbook runs
# TYPE opena6_runs_total counter
opena6_runs_total{status="success"} 42
opena6_runs_total{status="failed"} 3
opena6_runs_total{status="canceled"} 1

# HELP opena6_duration_ms Playbook execution duration
# TYPE opena6_duration_ms histogram
opena6_duration_ms_bucket{le="1000"} 10
opena6_duration_ms_bucket{le="5000"} 35
opena6_duration_ms_bucket{le="10000"} 46

# HELP opena6_artifacts_bytes_total Total artifact bytes written
# TYPE opena6_artifacts_bytes_total counter
opena6_artifacts_bytes_total 524288

# HELP opena6_rate_limit_delays_total Rate limit delays applied
# TYPE opena6_rate_limit_delays_total counter
opena6_rate_limit_delays_total 5
"""
    
    return JSONResponse(
        content=metrics_text,
        media_type="text/plain"
    )


@app.get("/logs")
async def list_logs():
    """List available log files"""
    
    try:
        log_files = list(log_dir.glob("*.jsonl"))
        return {
            "count": len(log_files),
            "files": [f.name for f in log_files]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DEBUG & ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/status")
async def status():
    """Overall agent status"""
    
    return {
        "service": config.SERVICE_NAME,
        "port": config.PORT,
        "browser_ready": browser_executor is not None,
        "headless": config.HEADLESS,
        "max_artifact_size_mb": config.MAX_ARTIFACT_SIZE_MB,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


@app.post("/api/test-playbook")
async def test_playbook():
    """Test playbook (for development/debugging)"""
    
    if not browser_executor:
        raise HTTPException(status_code=503, detail="Browser executor not ready")
    
    # Simple test: navigate & screenshot
    test_request = PlaybookRequest(
        request_id="test-000",
        steps=[
            {
                "action": "goto",
                "url": "https://example.org",
                "wait": "load"
            },
            {
                "action": "screenshot",
                "label": "example",
                "full_page": False
            }
        ],
        compliance={
            "allow_domains": ["example.org"],
            "obey_robots": True
        }
    )
    
    try:
        response = await browser_executor.execute_playbook(test_request)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROOT & FALLBACK
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "opena6 — Browser Automation Agent",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "run": "POST /run (execute playbook)",
            "cancel": "POST /cancel",
            "metrics": "/metrics",
            "status": "/api/status"
        }
    }


@app.get("/docs")
async def openapi_docs():
    """OpenAPI documentation"""
    return {
        "message": "OpenAPI docs available at /docs (Swagger UI)",
        "redoc": "/redoc (ReDoc)"
    }


# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": str(request.url)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower()
    )
