#!/usr/bin/env python3
"""
opena20 - Dashboard Agent
Port: 12349
Kürzel: dashp

Central Dashboard für ELION/Portier System
- Aggregierter Status aller Agenten (opena3-opena19)
- SSE-Bus für Real-Time Updates
- Web-UI für Übersicht
- REST-API für Agent-Status, E2E-Tests
- Integration mit opena15 (htmlp) für Dashboard-Seiten
"""

import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import aiohttp
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

# =============================================================================
# SAFEPOINT-WRITER 3.0 (Portier 3.0 Spezifikation)
# =============================================================================


class SafepointWriter30:
    """SAFEPOINT-WRITER 3.0 - Production Grade nach Portier 3.0 Norm"""

    CATEGORIES = {"CMD", "RESP", "ROUTE", "DISPATCH"}
    SECRET_KEYS = {"token", "auth", "password", "apikey", "key", "secret", "credentials"}

    def __init__(self, archivp_root: str = "/tmp/archivp_store"):
        self.archivp_root = Path(archivp_root)
        self.index_file = self.archivp_root / "index.jsonl"
        self._ensure_structure()

    def _ensure_structure(self) -> None:
        """Erstellt YYYY/MM/DD Struktur und index.jsonl"""
        self.archivp_root.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self.index_file.write_text("", encoding="utf-8")

    def _mask_secrets(self, data: Any) -> Any:
        """Maskiert Secrets rekursiv nach Portier 3.0 Spezifikation"""
        if isinstance(data, dict):
            data_dict = cast(dict[str, Any], data)
            return {
                k: "***" if any(secret in k.lower() for secret in self.SECRET_KEYS) else self._mask_secrets(v)
                for k, v in data_dict.items()
            }
        elif isinstance(data, list):
            data_list = cast(list[Any], data)
            return [self._mask_secrets(item) for item in data_list]
        return data

    def write_safepoint(
        self, source: str, destination: str, category: str, request_id: str, payload: dict[str, Any]
    ) -> str:
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Must be one of {self.CATEGORIES}")

        sp_timestamp = int(time.time())
        iso_timestamp = datetime.now(UTC).isoformat()

        now = datetime.now()
        date_path = self.archivp_root / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d")
        date_path.mkdir(parents=True, exist_ok=True)

        filename = f"SP{sp_timestamp}_{source}→{destination}_{category}.json"
        filepath = date_path / filename

        safepoint_obj: dict[str, Any] = {
            "timestamp": iso_timestamp,
            "sp_timestamp": sp_timestamp,
            "source": source,
            "destination": destination,
            "category": category,
            "request_id": request_id,
            "payload": self._mask_secrets(payload),
            "strict": True,
        }

        try:
            filepath.write_text(json.dumps(safepoint_obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        except Exception as e:
            for attempt in range(3):
                try:
                    time.sleep(0.1 * (attempt + 1))
                    filepath.write_text(
                        json.dumps(safepoint_obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
                    )
                    break
                except Exception:
                    if attempt == 2:
                        raise RuntimeError(f"Failed to write safepoint after retries: {e}")

        index_entry = {
            "file": str(filepath.relative_to(self.archivp_root)),
            "ts": iso_timestamp,
            "category": category,
            "source": source,
            "destination": destination,
            "request_id": request_id,
        }

        try:
            with open(self.index_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.warning(f"Failed to update index.jsonl: {e}")

        return filename

    def publish_sse_event(self, agent: str, category: str, filename: str) -> None:
        try:
            event_data = {
                "event_type": "safepoint",
                "agent": agent,
                "category": category,
                "timestamp": datetime.now(UTC).isoformat(),
                "file": filename,
            }
            logging.info(f"SSE Event: {event_data}")
        except Exception as e:
            logging.error(f"SSE Event failed: {e}")


safepoint_writer = SafepointWriter30()


# =============================================================================
# CONFIGURATION
# =============================================================================

PORT = 12349
AGENT_ID = "opena20"
KUERZEL = "dashp"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


# =============================================================================
# AGENT REGISTRY
# =============================================================================

AGENT_REGISTRY: list[dict[str, Any]] = [
    {"id": "opena3", "name": "OpenWebUI Terminal", "kuerzel": "owuip", "port": 12347},
    {"id": "opena4", "name": "Telegram Agent", "kuerzel": "telep", "port": 12348},
    {"id": "opena5", "name": "VS Code Agent", "kuerzel": "vscop", "port": 12351},
    {"id": "opena6", "name": "Browser Agent", "kuerzel": "browsep", "port": 12352},
    {"id": "opena7", "name": "Email Agent", "kuerzel": "emailp", "port": 12353},
    {"id": "opena8", "name": "WhatsApp Agent", "kuerzel": "whatsappp", "port": 12354},
    {"id": "opena9", "name": "Telefonie Agent", "kuerzel": "telphonep", "port": 12355},
    {"id": "opena10", "name": "Call Tracking Agent", "kuerzel": "calltrackp", "port": 12356},
    {"id": "opena11", "name": "Unlock Agent", "kuerzel": "unlockp", "port": 12357},
    {"id": "opena12", "name": "Social Media Agent", "kuerzel": "smp", "port": 12358},
    {"id": "opena13", "name": "Influencer Agent", "kuerzel": "influp", "port": 12359},
    {"id": "opena14", "name": "Calendar Agent", "kuerzel": "calp", "port": 12360},
    {"id": "opena15", "name": "HTML Creator", "kuerzel": "htmlp", "port": 12361},
    {"id": "opena16", "name": "Shop Agent", "kuerzel": "shopp", "port": 12362},
    {"id": "opena17", "name": "Homepage Creator", "kuerzel": "hpcreatep", "port": 12363},
    {"id": "opena18", "name": "CRM Agent", "kuerzel": "crmp", "port": 12363},
    {"id": "opena19", "name": "Stocks & Crypto", "kuerzel": "stockcryptop", "port": 12365},
    {"id": "opena21", "name": "Workflow Engine", "kuerzel": "workflowp", "port": 12367},
]


# =============================================================================
# FASTAPI APP
# =============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify Bearer token"""
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {AGENT_ID} on port {PORT}")
    yield
    logger.info(f"🛑 Shutting down {AGENT_ID}")


app = FastAPI(
    title="opena20 Dashboard Agent",
    description="Central Dashboard for ELION/Portier System",
    version="3.0",
    lifespan=lifespan,
)

# Optional tracing: initialize if environment and packages permit
try:
    from pkg.observability import init_tracing

    init_tracing(app, service_name=AGENT_ID)
except Exception as _e:
    logger.debug("Tracing not initialized or not available: %s", _e)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (UI)
static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
    # Create placeholder index if it doesn't exist
    (static_dir / "index.html").write_text(
        """
    <!doctype html>
    <html><head><title>ELION Dashboard</title></head>
    <body><h1>Dashboard Loading...</h1></body>
    </html>
    """
    )

try:
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ Static files mounted from {static_dir}")
except Exception as e:
    logger.warning(f"⚠️  Could not mount static files: {e}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": AGENT_ID,
        "kuerzel": KUERZEL,
        "port": PORT,
        "timestamp": datetime.now(UTC).isoformat(),
        "registered_agents": len(AGENT_REGISTRY),
    }


@app.get("/api/status/all")
async def status_all():
    """Get status of all registered agents"""
    results = []
    async with aiohttp.ClientSession() as session:
        for agent in AGENT_REGISTRY:
            try:
                url = f"http://127.0.0.1:{agent['port']}/health"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results.append(
                            {
                                "id": agent["id"],
                                "name": agent["name"],
                                "port": agent["port"],
                                "status": "online",
                                "health": data,
                            }
                        )
                    else:
                        results.append(
                            {
                                "id": agent["id"],
                                "name": agent["name"],
                                "port": agent["port"],
                                "status": "error",
                                "error": f"HTTP {resp.status}",
                            }
                        )
            except Exception as e:
                results.append(
                    {
                        "id": agent["id"],
                        "name": agent["name"],
                        "port": agent["port"],
                        "status": "offline",
                        "error": str(e),
                    }
                )
    return {"agents": results, "total": len(results), "timestamp": datetime.now(UTC).isoformat()}


@app.get("/api/agents")
async def list_agents():
    """List all registered agents"""
    return {"agents": AGENT_REGISTRY}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Dashboard Home"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>ELION Dashboard</title></head>
    <body>
        <h1>🚀 ELION Hyper-Dashboard 3.0</h1>
        <p>Agent: opena20 | Port: 12349</p>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/api/status/all">All Agents Status</a></li>
            <li><a href="/api/agents">Agent Registry</a></li>
        </ul>
    </body>
    </html>
    """


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    PORT = int(os.getenv("OPENA20_PORT", "12349"))
    print(f"🚀 opena20 Dashboard Agent startet auf Port {PORT}")
    uvicorn.run("main_dashboard:app", host="127.0.0.1", port=PORT, log_level="info")
