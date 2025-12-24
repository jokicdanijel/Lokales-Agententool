#!/usr/bin/env python3
"""
🔀 OpenA4 Reverse Proxy - Optimierte Version
Port: 12349 → 12348
Route: /agent/opena4 → http://127.0.0.1:12348/
"""

import logging
import os
from datetime import datetime

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("reverse_proxy")

# Konfiguration
TARGET_URL = os.getenv("TARGET_URL", "http://127.0.0.1:12348")
PROXY_PORT = int(os.getenv("PROXY_PORT", "12349"))
BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0")
REQUEST_TIMEOUT = 30.0

# FastAPI App
app = FastAPI(title="OpenA4 Reverse Proxy", description="Leitet /agent/opena4 zu Port 12348 weiter", version="1.0.0")

# HTTP Client mit Connection Pooling
http_client = httpx.AsyncClient(
    timeout=REQUEST_TIMEOUT, limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
)

# Statistiken
stats = {"requests": 0, "errors": 0, "start_time": datetime.now().isoformat()}


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "proxy": "running",
        "target": TARGET_URL,
        "uptime": stats["start_time"],
        "stats": stats,
    }


@app.get("/")
async def root():
    """Info Endpoint"""
    return {
        "service": "OpenA4 Reverse Proxy",
        "version": "1.0.0",
        "route": f"/agent/opena4 → {TARGET_URL}/",
        "health": "/health",
        "stats": stats,
    }


@app.api_route("/agent/opena4/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
@app.api_route("/agent/opena4", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_opena4(request: Request, path: str = ""):
    """
    🔀 Leitet /agent/opena4 zu Port 12348 weiter
    """
    stats["requests"] += 1

    # Baue Ziel-URL
    target_url = f"{TARGET_URL}/{path}" if path else TARGET_URL
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    logger.info(f"{request.method} /agent/opena4/{path} → {target_url}")

    # Headers ohne Host und Connection
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "connection", "content-length"]}

    # Body lesen
    body = await request.body()

    try:
        # Request weiterleiten
        response = await http_client.request(
            method=request.method, url=target_url, headers=headers, content=body, follow_redirects=True
        )

        # Response-Headers filtern
        response_headers = {
            k: v
            for k, v in response.headers.items()
            if k.lower() not in ["content-encoding", "content-length", "transfer-encoding"]
        }
        response_headers.pop("transfer-encoding", None)  # Transfer wird automatisch gehandhabt

        return Response(content=response.content, status_code=response.status_code, headers=response_headers)

    except httpx.TimeoutException:
        stats["errors"] += 1
        logger.error(f"Timeout bei {target_url}")
        return JSONResponse(status_code=504, content={"error": "Gateway Timeout", "target": TARGET_URL})
    except httpx.ConnectError:
        stats["errors"] += 1
        logger.error(f"Connection Error zu {target_url}")
        return JSONResponse(status_code=502, content={"error": "Backend nicht erreichbar", "target": TARGET_URL})
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Proxy Error: {e!s}")
        return JSONResponse(status_code=502, content={"error": "Proxy Error", "detail": str(e)})


@app.on_event("startup")
async def startup_event():
    """Initialisierung beim Start"""
    logger.info(f"🚀 Reverse Proxy startet auf {BIND_HOST}:{PROXY_PORT}")
    logger.info(f"🎯 Ziel: {TARGET_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup beim Beenden"""
    await http_client.aclose()
    logger.info("👋 Reverse Proxy gestoppt")


if __name__ == "__main__":
    print(
        f"""
╔═══════════════════════════════════════════════════════════════╗
║  🔀 OpenA4 Reverse Proxy - Optimierte Version                ║
╠═══════════════════════════════════════════════════════════════╣
║  Port:         {PROXY_PORT:<50}║
║  Host:         {BIND_HOST:<50}║
║  Ziel:         {TARGET_URL:<50}║
║  Timeout:      {REQUEST_TIMEOUT}s{' ' * 47}║
╠═══════════════════════════════════════════════════════════════╣
║  Routen:                                                      ║
║  • /agent/opena4 → {TARGET_URL}/{'':>24}║
║  • /health       → Health Check{'':>33}║
║  • /             → Info{'':>42}║
╠═══════════════════════════════════════════════════════════════╣
║  Features:                                                    ║
║  ✅ Connection Pooling                                        ║
║  ✅ Error Handling                                            ║
║  ✅ Request Logging                                           ║
║  ✅ Health Checks                                             ║
║  ✅ Statistiken                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    )

    uvicorn.run(app, host=BIND_HOST, port=PROXY_PORT, log_level="info", access_log=True)
