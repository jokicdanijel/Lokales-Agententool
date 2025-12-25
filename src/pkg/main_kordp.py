"""
Kordinatport (kordp) – FastAPI-Service auf Port 12346

Aufgaben:
- Befehle entgegennehmen und weiterreichen (Dispatch)
- Für jede Operation einen CMD-Safepoint via opena2 (/store/archivp) schreiben
- Port-Policy & gemeinsame Auth via .env

Fixe Labels/Endpoints (bindend):
- /dispatch/kordp   (nimmt Kommandos an, schreibt CMD-Safepoint bei opena2)
"""

import logging
from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from security import RateLimiter, _read_env_token, verify_token

OPENA2_URL = "http://127.0.0.1:12348"  # Archivator NEU: 12348

ALLOWED_PORT_MIN = 12344
ALLOWED_PORT_MAX = 12399
FORBIDDEN_PORTS = {8080}

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - kordp - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/kordp_runtime.log"), logging.StreamHandler()],
)
logger = logging.getLogger("kordp")

# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------
app = FastAPI(title="Kordinatport (kordp)", version="1.0", description="Dispatch-Port für Befehle")
security = HTTPBearer()
rate_limiter = RateLimiter(requests_per_minute=90)

_client = httpx.AsyncClient(timeout=10)


# -------------------------------------------------------------------
# Middleware: Port-Policy
# -------------------------------------------------------------------
@app.middleware("http")
async def validate_port_policy(request: Request, call_next):
    port = request.url.port
    if port in FORBIDDEN_PORTS:
        raise HTTPException(status_code=403, detail=f"Port {port} ist verboten")
    if not (ALLOWED_PORT_MIN <= port <= ALLOWED_PORT_MAX):
        raise HTTPException(status_code=403, detail=f"Port {port} außerhalb {ALLOWED_PORT_MIN}–{ALLOWED_PORT_MAX}")
    return await call_next(request)


# -------------------------------------------------------------------
# Lifecycle
# -------------------------------------------------------------------
@app.on_event("startup")
async def on_start():
    _ = _read_env_token()
    logger.info("kordp gestartet. Ziel-Archivator: %s", OPENA2_URL)


# -------------------------------------------------------------------
# Endpunkte
# -------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"service": "kordp", "status": "healthy", "strict": True, "timestamp": datetime.utcnow().isoformat()}


@app.post("/dispatch/kordp")
@rate_limiter.limit()
async def dispatch(payload: dict[str, Any], token: HTTPAuthorizationCredentials = Security(security)):
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    command = (payload or {}).get("command")
    params = (payload or {}).get("params", {})
    src = (payload or {}).get("src", "kordp")

    if not command:
        raise HTTPException(status_code=400, detail="command fehlt")

    token_val = _read_env_token()
    try:
        sp_body = {
            "src": src,
            "dst": "opena2",
            "kind": "CMD",
            "data": {"command": command, "params": params, "ts": datetime.utcnow().isoformat(), "strict": True},
        }
        r = await _client.post(
            f"{OPENA2_URL}/store/archivp", headers={"Authorization": f"Bearer {token_val}"}, json=sp_body
        )
        if r.status_code != 200:
            logger.error("Safepoint-Write fehlgeschlagen: %s %s", r.status_code, r.text)
            raise HTTPException(status_code=502, detail=f"Archivator-Fehler {r.status_code}")
        sp_info = r.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Archivator-Aufruf fehlgeschlagen: %s", e)
        raise HTTPException(status_code=502, detail="Archivator nicht erreichbar")

    return {"strict": True, "accepted": True, "safepoint": sp_info}


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main_kordp:app", host="127.0.0.1", port=12346, reload=False)
