"""
kordp/main_production.py — Coordinator Gateway (Port 12346)
Production entry point for kordp dispatch service.
LOCATION: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/kordp/main_production.py
"""

import sys
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
import uvicorn

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kordp.router import router as kordp_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("kordp")

# Initialize FastAPI app
app = FastAPI(
    title="kordp – Coordinator Gateway",
    description="Dispatch gateway with tool routing and safepoint tracking",
    version="2.0.0"
)

# Include routers
app.include_router(kordp_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "service": "kordp",
        "status": "ok",
        "role": "gateway",
        "timestamp": now,
        "port_policy": {"window": [12344, 12399], "forbidden": [8080]}
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "kordp",
        "message": "Coordinator Gateway – Tool Dispatch",
        "docs": "/docs",
        "health": "/health",
        "dispatch_endpoint": "/dispatch/kordp"
    }


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="kordp Gateway Server")
    parser.add_argument("--port", type=int, default=12346)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    
    # Validate port policy
    if args.port == 8080:
        logger.error("PORT 8080 FORBIDDEN")
        sys.exit(1)
    
    if not (12344 <= args.port <= 12399):
        logger.warning(f"Port {args.port} outside recommended range [12344-12399]")
    
    logger.info(f"Starting kordp on {args.host}:{args.port}")
    
    uvicorn.run(
        "kordp.main_production:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
