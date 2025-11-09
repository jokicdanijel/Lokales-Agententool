"""
main_production.py – Production entry point for opena1
FastAPI application with 7.1 validation and health endpoint.
"""

import sys
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
import uvicorn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from koordinator import router as opena1_router
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from portier_openai.koordinator import router as opena1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="opena1 – Portier Koordinator",
    description="Coordinator service with 7.1 strict validation",
    version="1.0.0"
)

# Include routers
app.include_router(opena1_router)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "service": "opena1",
        "status": "ok",
        "timestamp": now_utc,
        "port_policy": {
            "window": [12344, 12349],
            "forbidden": [8080]
        }
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": "opena1",
        "message": "Portier Koordinator – 7.1 Validation",
        "docs": "/docs",
        "health": "/health",
        "log_endpoint": "/log/opena1"
    }


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="opena1 Production Server")
    parser.add_argument("--port", type=int, default=12344, help="Port (default 12344)")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default 127.0.0.1)")
    args = parser.parse_args()
    
    # Validate port policy
    if args.port == 8080:
        logger.error("❌ Port 8080 is forbidden by policy")
        sys.exit(1)
    
    if not (12344 <= args.port <= 12349):
        logger.warning(f"⚠️  Port {args.port} outside recommended range [12344-12349]")
    
    logger.info(f"Starting opena1 on {args.host}:{args.port}")
    
    uvicorn.run(
        "main_production:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
