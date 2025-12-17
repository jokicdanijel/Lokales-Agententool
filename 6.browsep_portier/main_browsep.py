"""Minimal FastAPI service for Portier Browse (browsep)

Provides /health and /command endpoints and writes a safepoint for commands.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
import os

app = FastAPI(title="browsep - Portier Browse Agent")

ARCHIVP_ROOT = Path(os.getenv("ARCHIVP_ROOT", "../1.opena1&2_portier/archivp_store"))
ARCHIVP_ROOT.mkdir(parents=True, exist_ok=True)

class Command(BaseModel):
    id: str
    payload: dict

@app.get("/health")
async def health():
    return {"status": "ok", "uptime": 0}

@app.post("/command")
async def command(cmd: Command):
    # write a safepoint (minimal, append-only)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sp_id = f"SP_{ts}_{cmd.id}"
    filename = ARCHIVP_ROOT / f"{sp_id}_browsep_CMD.json"
    payload = {
        "sp_id": sp_id,
        "timestamp": ts,
        "src": "browsep",
        "dst": "opena1",
        "type": "CMD",
        "command": cmd.dict()
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"result": "saved", "path": str(filename)}
