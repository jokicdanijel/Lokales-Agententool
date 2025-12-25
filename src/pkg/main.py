#!/usr/bin/env python3
"""
Agent main entry point
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging

import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Initialize OpenTelemetry tracing based on Settings at startup (no-op if disabled)
# Use OTEL_* env vars or the Settings object to control behavior.
@app.on_event("startup")
async def _startup_init_tracing():
    try:
        from pkg.shared.config import init_tracing_from_settings

        init_tracing_from_settings(app, service_name=os.environ.get("SERVICE_NAME", "opena1"))
    except Exception as e:  # pragma: no cover - defensive
        # Non-fatal: tracing is optional and import may fail if deps are not present
        logger.debug("Tracing startup hook failed or is disabled: %s", e)


PORT = int(os.getenv("PORT", "12344"))
TOKEN = os.getenv("TOKEN", "")


@app.get("/health")
async def health():
    return {"status": "ok", "port": PORT}


@app.post("/invoke")
async def invoke(payload: dict):
    """Main agent endpoint"""
    logger.info(f"Invoke: {payload}")
    return {"result": "ok", "payload": payload}


if __name__ == "__main__":
    logger.info(f"Starting agent on port {PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
