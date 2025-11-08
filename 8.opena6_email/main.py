#!/usr/bin/env python3
"""Agent main.py - FastAPI Einstiegspunkt"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ELION Agent", version="1.0.0", docs_url="/docs")

AGENT_ID = os.getenv("AGENT_ID", "opena_unknown")
PORT = int(os.getenv("PORT", "12344"))

@app.get("/health")
async def health():
    return {"status": "ok", "service": AGENT_ID, "port": PORT, "version": "1.0.0"}

@app.get("/status")
async def status():
    return {"agent_id": AGENT_ID, "port": PORT, "uptime": "running", "log_file": str(LOG_FILE)}

@app.post("/invoke")
async def invoke(payload: dict):
    logger.info(f"Invoke: {payload}")
    return {"status": "ok", "agent_id": AGENT_ID, "result": "Processing..."}

@app.get("/info")
async def info():
    return {"agent_id": AGENT_ID, "port": PORT, "running": True}

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

if __name__ == "__main__":
    logger.info(f"Starting {AGENT_ID} on port {PORT}")
    try:
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)
