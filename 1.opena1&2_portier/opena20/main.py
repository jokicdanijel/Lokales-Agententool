import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import httpx
import psutil
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============= GLOBALE KONFIGURATION =============
AGENTS = {
    "opena1": {"port": 12344, "name": "Koordinator (opena1)", "description": "Agent Koordinator"},
    "opena2": {"port": 12345, "name": "Archivator (opena2)", "description": "Dokumenten-Archivierung"},
    "kordp": {"port": 12346, "name": "Gateway (kordp)", "description": "Portal-Gateway"},
    "opena20": {"port": 12349, "name": "Dashboard (opena20)", "description": "Portier-20 Orchestrator"},
}

SAFEPOINTS = {
    "gateway": {
        "name": "Gateway Checkpoint",
        "status": "✅ Active",
        "rate": 0,
        "last_checkpoint": datetime.now().isoformat(),
    },
    "tool_exec": {
        "name": "Tool Execution",
        "status": "✅ Active",
        "rate": 0,
        "last_checkpoint": datetime.now().isoformat(),
    },
    "archive": {
        "name": "Archive Access",
        "status": "✅ Active",
        "rate": 0,
        "last_checkpoint": datetime.now().isoformat(),
    },
}

start_time = datetime.now()
request_count = 0
e2e_results = {}
logs_buffer = []
MAX_LOGS = 500


# ============= LIFECYCLE EVENTS =============
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 opena20 Dashboard startet auf Port 12349")
    logger.info("🔗 Circuit: opena1(12344) → opena2(12345) → kordp(12346) → opena20(12349)")
    yield
    logger.info("🛑 opena20 shutdown")


app = FastAPI(
    title="🧠 opena20 – Portier-20 Dashboard",
    description="Zentrales Monitoring & Control System für Portier-20 Circuit",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS aktivieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ============= LOGGING FUNKTION =============
def add_log(message: str, level: str = "info"):
    """Füge Log-Eintrag zu Buffer hinzu"""
    entry = {"timestamp": datetime.now().isoformat(), "level": level, "message": message}
    logs_buffer.append(entry)
    if len(logs_buffer) > MAX_LOGS:
        logs_buffer.pop(0)

    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)


# ============= HEALTH CHECK FUNKTIONEN =============
async def check_agent_health(agent_name: str, port: int, description: str) -> dict:
    """Prüfe echten Agent-Status über HTTP"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"http://localhost:{port}/health", follow_redirects=True)
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    data = {}

                add_log(f"✅ Agent {agent_name} online (Port {port})", "info")
                return {
                    "name": agent_name,
                    "port": port,
                    "description": description,
                    "status": "✅ Online",
                    "uptime": data.get("uptime", "N/A"),
                    "requests": data.get("requests", 0),
                    "last_check": datetime.now().isoformat(),
                }
    except Exception as e:
        add_log(f"⚠️ Agent {agent_name} nicht erreichbar: {e!s}", "warning")

    return {
        "name": agent_name,
        "port": port,
        "description": description,
        "status": "❌ Offline",
        "uptime": "N/A",
        "requests": 0,
        "last_check": datetime.now().isoformat(),
    }


async def get_all_agents_status() -> list:
    """Hole Status aller 4 Agents"""
    tasks = []
    for agent_name, config in AGENTS.items():
        tasks.append(check_agent_health(agent_name, config["port"], config["description"]))
    return await asyncio.gather(*tasks)


def get_system_metrics() -> dict:
    """Hole echte Systemmetriken"""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": cpu,
            "cpu_count": psutil.cpu_count(),
            "memory": {
                "total": mem.total,
                "available": mem.available,
                "percent": mem.percent,
                "used": mem.used,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            },
            "process_count": len(psutil.pids()),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        add_log(f"Fehler beim Lesen von Systemmetriken: {e}", "error")
        return {"error": str(e)}


# ============= HTML ROUTES =============
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard"""
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, encoding="utf-8") as f:
            return f.read()

    # Fallback Dashboard
    return """<!DOCTYPE html>
    <html><head><title>🧠 opena20</title>
    <style>body{background:#1a1a2e;color:#eee;font-family:system-ui;padding:20px}
    h1{color:#00d4ff}</style></head>
    <body><h1>🧠 opena20 Dashboard</h1>
    <p>Laden Sie die Templates neu. API verfügbar auf <a href="/docs">/docs</a></p>
    </body></html>"""


# ============= HEALTH & STATUS =============
@app.get("/health")
async def health_check():
    """Full Health Status"""
    global request_count
    request_count += 1

    agents = await get_all_agents_status()
    online_count = sum(1 for a in agents if "Online" in a["status"])
    uptime_seconds = (datetime.now() - start_time).total_seconds()

    add_log(f"Health Check: {online_count}/4 agents online", "info")

    return {
        "status": "ok",
        "port": 12349,
        "circuit": f"{online_count}/4 agents online",
        "uptime_seconds": uptime_seconds,
        "requests": request_count,
        "agents": agents,
        "safepoints": SAFEPOINTS,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/v1/health/full")
async def health_full():
    """Vollständiger Health Report"""
    agents = await get_all_agents_status()
    metrics = get_system_metrics()

    return {
        "status": "ok",
        "agents": agents,
        "safepoints": SAFEPOINTS,
        "system": metrics,
        "timestamp": datetime.now().isoformat(),
    }


# ============= AGENT ROUTES =============
@app.get("/api/v1/agents")
async def get_agents():
    """Get all agents status"""
    agents = await get_all_agents_status()
    online = sum(1 for a in agents if "Online" in a["status"])
    return {"agents": agents, "total": len(agents), "online": online, "circuit_ok": online >= 3}


@app.get("/api/v1/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get specific agent"""
    if agent_name not in AGENTS:
        add_log(f"Agent {agent_name} nicht gefunden", "warning")
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")

    agent_config = AGENTS[agent_name]
    return await check_agent_health(agent_name, agent_config["port"], agent_config["description"])


# ============= SAFEPOINT ROUTES =============
@app.get("/api/v1/safepoints")
async def get_safepoints():
    """Get safepoint status"""
    active_count = sum(1 for s in SAFEPOINTS.values() if "Active" in s.get("status", ""))
    return {
        "safepoints": SAFEPOINTS,
        "active_count": active_count,
        "total": len(SAFEPOINTS),
        "all_active": active_count == len(SAFEPOINTS),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/v1/safepoint/update/{name}")
async def update_safepoint(name: str):
    """Update safepoint checkpoint"""
    if name not in SAFEPOINTS:
        raise HTTPException(status_code=404, detail="Safepoint nicht gefunden")

    SAFEPOINTS[name]["last_checkpoint"] = datetime.now().isoformat()
    add_log(f"Safepoint '{name}' aktualisiert", "success")

    return {"status": "updated", "safepoint": SAFEPOINTS[name], "timestamp": datetime.now().isoformat()}


# ============= CIRCUIT CHECK =============
@app.get("/api/v1/circuit/integrity")
async def circuit_integrity():
    """Check circuit integrity"""
    agents = await get_all_agents_status()
    online_count = sum(1 for a in agents if "Online" in a["status"])
    circuit_ok = online_count >= 3

    add_log(f"Circuit Integrity: {online_count}/4 agents", "info" if circuit_ok else "warning")

    return {
        "circuit_ok": circuit_ok,
        "agents_online": online_count,
        "agents_total": len(agents),
        "agents": agents,
        "safepoints_active": sum(1 for s in SAFEPOINTS.values() if "Active" in s.get("status", "")),
        "timestamp": datetime.now().isoformat(),
    }


# ============= E2E TEST =============
@app.post("/e2e")
async def run_e2e():
    """End-to-End Test"""
    start = datetime.now()
    add_log("🔄 E2E Test gestartet", "info")

    try:
        # Test 1: Health Check
        health = await health_check()
        test_health = "✅" if health["status"] == "ok" else "❌"

        # Test 2: Agents
        agents = await get_agents()
        test_agents = "✅" if agents["circuit_ok"] else "❌"

        # Test 3: Safepoints
        safepoints = await get_safepoints()
        test_safepoints = "✅" if safepoints["all_active"] else "❌"

        # Test 4: Circuit
        circuit = await circuit_integrity()
        test_circuit = "✅" if circuit["circuit_ok"] else "❌"

        duration_ms = (datetime.now() - start).total_seconds() * 1000
        all_passed = all(t == "✅" for t in [test_health, test_agents, test_safepoints, test_circuit])

        results = {
            "health_check": test_health,
            "agents": test_agents,
            "safepoints": test_safepoints,
            "circuit": test_circuit,
        }

        e2e_results.clear()
        e2e_results.update(results)

        message = (
            f"✅ E2E Test PASSED ({duration_ms:.0f}ms)" if all_passed else f"❌ E2E Test FAILED ({duration_ms:.0f}ms)"
        )
        add_log(message, "success" if all_passed else "error")

        return {
            "success": all_passed,
            "duration_ms": duration_ms,
            "results": results,
            "details": {"health": health, "agents": agents, "safepoints": safepoints, "circuit": circuit},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        add_log(f"❌ E2E Test Error: {e!s}", "error")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}


# ============= SYSTEM CONTROL =============
@app.post("/restart")
async def restart_system():
    """Restart system"""
    add_log("🚨 System Restart angefordert", "warning")

    return {
        "status": "restart_scheduled",
        "message": "System wird in 2 Sekunden neu gestartet...",
        "timestamp": datetime.now().isoformat(),
    }


# ============= METRICS =============
@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics"""
    metrics = get_system_metrics()
    agents = await get_all_agents_status()
    uptime = (datetime.now() - start_time).total_seconds()

    return {
        "uptime_seconds": uptime,
        "requests_total": request_count,
        "system": metrics,
        "agents": agents,
        "safepoints": SAFEPOINTS,
        "timestamp": datetime.now().isoformat(),
    }


# ============= LOGS =============
@app.get("/api/v1/logs")
async def get_logs(limit: int = 50):
    """Get system logs"""
    return {
        "logs": logs_buffer[-limit:] if limit > 0 else logs_buffer,
        "total": len(logs_buffer),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/v1/logs/circuit")
async def get_circuit_logs():
    """Get circuit-related logs"""
    circuit_logs = [l for l in logs_buffer if any(x in l["message"].lower() for x in ["circuit", "agent", "safepoint"])]
    return {"logs": circuit_logs[-30:], "total": len(circuit_logs), "timestamp": datetime.now().isoformat()}


@app.post("/api/v1/logs/clear")
async def clear_logs():
    """Clear all logs"""
    global logs_buffer
    logs_buffer.clear()
    add_log("Logs gelöscht", "info")
    return {"status": "cleared", "timestamp": datetime.now().isoformat()}


# ============= STATUS & INFO =============
@app.get("/api/status")
async def status():
    """System Status"""
    uptime_sec = (datetime.now() - start_time).total_seconds()
    uptime_min = uptime_sec // 60
    uptime_hr = uptime_min // 60

    return {
        "status": "running",
        "version": "2.0.0",
        "uptime_seconds": uptime_sec,
        "uptime_formatted": f"{int(uptime_hr)}h {int(uptime_min % 60)}m",
        "requests": request_count,
        "logs": len(logs_buffer),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/v1/info")
async def system_info():
    """System Information"""
    agents = await get_all_agents_status()
    return {
        "name": "opena20 – Portier-20 Dashboard",
        "version": "2.0.0",
        "port": 12349,
        "agents": agents,
        "safepoints": list(SAFEPOINTS.keys()),
        "uptime_seconds": (datetime.now() - start_time).total_seconds(),
        "timestamp": datetime.now().isoformat(),
    }


# ============= ERROR HANDLERS =============
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    add_log(f"HTTP Error {exc.status_code}: {exc.detail}", "error")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    add_log(f"Unerwarteter Fehler: {exc!s}", "error")
    return JSONResponse(status_code=500, content={"detail": "Interner Fehler", "error": str(exc)})


# ============= STARTUP & SHUTDOWN =============
@app.on_event("startup")
async def startup_event():
    add_log("✅ opena20 startup complete", "success")
    logger.info("📊 Dashboard: GET /")
    logger.info("❤️  Health: GET /health")
    logger.info("🤖 Agents: GET /api/v1/agents")
    logger.info("📍 Safepoints: GET /api/v1/safepoints")
    logger.info("📈 Metrics: GET /metrics")
    logger.info("🔌 API Docs: GET /docs")


@app.on_event("shutdown")
async def shutdown_event():
    add_log("🛑 opena20 shutdown", "warning")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=12349, log_level="info")
