#!/usr/bin/env python3
"""
Agent main entry point
"""
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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
