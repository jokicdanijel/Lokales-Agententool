"""
opena6: Mail Agent
Port: 12349
Relayed zu opena2 (Archivator)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import requests
import os
import json

AGENT = "opena6"
ARCHIVATOR = "http://127.0.0.1:12345/finalize/opena2"
app = FastAPI(title=f"{AGENT} Service", version="1.0.0")

@app.get("/health")
def health():
    return {
        "service": AGENT,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": 12349
    }

@app.post("/message")
async def message(request: Request):
    """Nachricht empfangen und via Archivator weiterleiten"""
    body = await request.json()
    
    env = {
        "os": "Ubuntu 25.04",
        "python": "3.13",
        "venv": "venv313",
        "ports_allowed": [12344, 12345, 12346, 12347, 12348, 12349, 12350],
        "port_forbidden": [8080]
    }
    
    envelope = {
        "request_id": body.get("request_id", "auto"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": AGENT,
        "command": body.get("command", "MSG_IN"),
        "payload": body.get("payload", {}),
        "routing": {"via": ["opena2", "kordp"]},
        "env": env,
        "strict": True
    }
    
    try:
        r = requests.post(ARCHIVATOR, json=envelope, timeout=10)
        return JSONResponse({
            "status": "forwarded",
            "code": r.status_code,
            "strict": True
        })
    except Exception as e:
        raise HTTPException(500, f"forward error: {e}")
