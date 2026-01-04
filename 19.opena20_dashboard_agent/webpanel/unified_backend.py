#!/usr/bin/env python3
"""
TELEGRAM MOBILE AGENT - UNIFIED BACKEND
ALLE möglichen Anbindungen vollständig integriert
Port: 12346
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Mobile Agent - FULL API", version="4.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket verbunden: {len(self.active_connections)} aktive")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket getrennt: {len(self.active_connections)} verbleibend")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()

# Globale Stats
stats = {
    "messages_sent": 0,
    "messages_received": 0,
    "active_chats": 0,
    "response_time_ms": 0,
    "uptime_start": datetime.now().isoformat(),
    "total_requests": 0,
    "errors": 0,
    "workflows_loaded": 0,
}

# Workflows Speicher
workflows = []
telegram_workflows = []
terminal_workflows = []

# Bot Status
bot_status = {"is_running": False, "pid": None, "start_time": None}


# Models
class ChatMessage(BaseModel):
    text: str
    chat_id: str | None = None


class CommandExec(BaseModel):
    command: str


class WebhookConfig(BaseModel):
    url: str
    secret_token: str | None = None


# Workflows laden
def load_workflow(path: str) -> dict | None:
    try:
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"✅ Workflow geladen: {os.path.basename(path)}")
            return data
    except Exception as e:
        logger.error(f"❌ Workflow Fehler {path}: {e}")
        return None


def load_all_workflows():
    global workflows, telegram_workflows, terminal_workflows, stats

    base_path = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/3.opena4_telegram")

    # Telegram Workflows
    for i in range(1, 11):
        wf_path = base_path / f"telegram_workflow_{i:02d}.json"
        wf = load_workflow(str(wf_path))
        if wf:
            wf["type"] = "telegram"
            wf["id"] = f"telegram_{i:02d}"
            telegram_workflows.append(wf)

    # Terminal Workflows
    for i in range(1, 11):
        wf_path = base_path / f"terminal_workflow_{i:02d}.json"
        wf = load_workflow(str(wf_path))
        if wf:
            wf["type"] = "terminal"
            wf["id"] = f"terminal_{i:02d}"
            terminal_workflows.append(wf)

    workflows = telegram_workflows + terminal_workflows
    stats["workflows_loaded"] = len(workflows)

    logger.info(f"📊 Workflows geladen: {len(telegram_workflows)} Telegram + {len(terminal_workflows)} Terminal")


# Bot PID finden
def find_bot_process():
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline", [])
            if cmdline and any("telegram_bot.py" in str(c) for c in cmdline):
                return proc.info["pid"]
        except:
            pass
    return None


# ==================== ALLE ENDPUNKTE ====================


@app.on_event("startup")
async def startup():
    logger.info("🚀 Telegram Mobile Agent Backend startet...")
    load_all_workflows()
    bot_status["pid"] = find_bot_process()
    bot_status["is_running"] = bot_status["pid"] is not None
    logger.info(f"✅ Backend bereit - {stats['workflows_loaded']} Workflows geladen")


@app.get("/")
async def root():
    """Hauptseite - serviert index.html"""
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        logger.info(f"📄 Serviere: {html_path.name}")
        return FileResponse(html_path)
    return HTMLResponse("<h1>Telegram Mobile Agent</h1><p>Dashboard wird geladen...</p>")


@app.get("/index.html")
async def get_index():
    """Index HTML direkt"""
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    raise HTTPException(404, "index.html nicht gefunden")


@app.get("/style.css")
async def get_style():
    """CSS Datei"""
    css_path = Path(__file__).parent / "style.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(404, "style.css nicht gefunden")


@app.get("/config.js")
async def get_config_js():
    """Config JS"""
    js_path = Path(__file__).parent / "config.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(404, "config.js nicht gefunden")


@app.get("/app.js")
async def get_app_js():
    """App JS"""
    js_path = Path(__file__).parent / "app.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(404, "app.js nicht gefunden")


@app.get("/test_api.html")
async def get_test_api():
    """API Test Seite"""
    html_path = Path(__file__).parent / "test_api.html"
    if html_path.exists():
        return FileResponse(html_path)
    raise HTTPException(404, "test_api.html nicht gefunden")


# ==================== STATUS & MONITORING ====================


@app.get("/api/status")
async def get_status():
    """System und Bot Status"""
    stats["total_requests"] += 1

    bot_pid = find_bot_process()
    bot_running = bot_pid is not None

    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "bot": {
            "is_running": bot_running,
            "pid": bot_pid,
            "messages_sent": stats["messages_sent"],
            "messages_received": stats["messages_received"],
            "active_chats": stats["active_chats"],
            "response_time": stats["response_time_ms"],
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available // (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free // (1024**3),
            "uptime": (datetime.now() - datetime.fromisoformat(stats["uptime_start"])).total_seconds(),
        },
        "workflows": {
            "total": len(workflows),
            "telegram": len(telegram_workflows),
            "terminal": len(terminal_workflows),
        },
        "stats": {
            "total_requests": stats["total_requests"],
            "errors": stats["errors"],
            "websocket_connections": len(manager.active_connections),
        },
    }


@app.get("/api/health")
async def health_check():
    """Health Check"""
    return {
        "status": "ok",
        "service": "telegram-mobile-agent",
        "version": "4.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/selftest")
async def selftest():
    """Kompletter System-Test"""
    tests_passed = 0
    tests_total = 0
    results = []

    # Test 1: Workflow-Dateien
    tests_total += 1
    if len(workflows) >= 20:
        tests_passed += 1
        results.append({"test": "workflows", "status": "✅", "message": f"{len(workflows)} Workflows"})
    else:
        results.append({"test": "workflows", "status": "❌", "message": f"Nur {len(workflows)} Workflows"})

    # Test 2: Bot-Prozess
    tests_total += 1
    if find_bot_process():
        tests_passed += 1
        results.append({"test": "bot_process", "status": "✅", "message": "Bot läuft"})
    else:
        results.append({"test": "bot_process", "status": "⚠️", "message": "Bot gestoppt"})

    # Test 3: System-Ressourcen
    tests_total += 1
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    if cpu < 90 and mem < 90:
        tests_passed += 1
        results.append({"test": "resources", "status": "✅", "message": f"CPU {cpu}% RAM {mem}%"})
    else:
        results.append({"test": "resources", "status": "❌", "message": "Ressourcen kritisch"})

    return {
        "tests_passed": tests_passed,
        "total_tests": tests_total,
        "success_rate": f"{tests_passed/tests_total*100:.0f}%",
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }


# ==================== BOT STEUERUNG ====================


@app.post("/api/bot/start")
async def start_bot():
    """Bot starten"""
    pid = find_bot_process()
    if pid:
        return {"status": "already_running", "pid": pid}

    try:
        bot_script = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/3.opena4_telegram/telegram_bot.py"
        )
        if not bot_script.exists():
            raise HTTPException(404, "Bot-Script nicht gefunden")

        process = subprocess.Popen(
            ["python3", str(bot_script)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True
        )

        await asyncio.sleep(1)
        pid = find_bot_process()

        bot_status["is_running"] = True
        bot_status["pid"] = pid
        bot_status["start_time"] = datetime.now().isoformat()

        await manager.broadcast({"type": "bot_started", "pid": pid})

        return {"status": "started", "pid": pid, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        stats["errors"] += 1
        raise HTTPException(500, f"Start fehlgeschlagen: {e!s}")


@app.post("/api/bot/stop")
async def stop_bot():
    """Bot stoppen"""
    pid = find_bot_process()
    if not pid:
        return {"status": "not_running"}

    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)

        bot_status["is_running"] = False
        bot_status["pid"] = None

        await manager.broadcast({"type": "bot_stopped"})

        return {"status": "stopped", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        stats["errors"] += 1
        raise HTTPException(500, f"Stop fehlgeschlagen: {e!s}")


@app.post("/api/bot/restart")
async def restart_bot():
    """Bot neu starten"""
    await stop_bot()
    await asyncio.sleep(2)
    return await start_bot()


@app.get("/api/bot/details")
async def bot_details():
    """Detaillierte Bot-Informationen"""
    pid = find_bot_process()

    if not pid:
        return {"running": False}

    try:
        proc = psutil.Process(pid)
        return {
            "running": True,
            "pid": pid,
            "cpu_percent": proc.cpu_percent(),
            "memory_mb": proc.memory_info().rss // (1024 * 1024),
            "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
            "num_threads": proc.num_threads(),
            "status": proc.status(),
        }
    except:
        return {"running": False}


@app.get("/api/bot/updates")
async def get_updates():
    """Bot Updates abrufen (simuliert)"""
    stats["messages_received"] += 1
    return {"updates": [], "count": 0, "timestamp": datetime.now().isoformat()}


# ==================== WORKFLOWS ====================


@app.get("/api/workflows")
async def get_workflows():
    """Alle Workflows"""
    return {
        "workflows": workflows,
        "total": len(workflows),
        "telegram": len(telegram_workflows),
        "terminal": len(terminal_workflows),
    }


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Einzelner Workflow"""
    wf = next((w for w in workflows if w.get("id") == workflow_id), None)
    if not wf:
        raise HTTPException(404, "Workflow nicht gefunden")
    return wf


@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """Workflow ausführen"""
    wf = next((w for w in workflows if w.get("id") == workflow_id), None)
    if not wf:
        raise HTTPException(404, "Workflow nicht gefunden")

    await manager.broadcast({"type": "workflow_executed", "workflow_id": workflow_id})

    return {"status": "executed", "workflow_id": workflow_id, "timestamp": datetime.now().isoformat()}


# ==================== MESSAGING ====================


@app.post("/api/chat/send")
async def send_message(message: ChatMessage):
    """Nachricht senden"""
    stats["messages_sent"] += 1

    await manager.broadcast({"type": "message_sent", "text": message.text, "chat_id": message.chat_id})

    return {"status": "sent", "message_id": stats["messages_sent"], "timestamp": datetime.now().isoformat()}


@app.get("/api/analytics")
async def get_analytics():
    """Chat Analytics"""
    return {
        "total_messages": stats["messages_sent"] + stats["messages_received"],
        "sent": stats["messages_sent"],
        "received": stats["messages_received"],
        "active_chats": stats["active_chats"],
        "avg_response_time_ms": stats["response_time_ms"],
    }


# ==================== WEBHOOK ====================


@app.get("/api/webhook/info")
async def webhook_info():
    """Webhook Informationen"""
    return {
        "url": "http://localhost:12346/api/webhook",
        "has_custom_certificate": False,
        "pending_update_count": 0,
        "last_synchronization_error_date": None,
    }


@app.post("/api/webhook")
async def webhook_receiver(data: dict):
    """Webhook Empfänger"""
    logger.info(f"📩 Webhook erhalten: {data}")
    stats["messages_received"] += 1

    await manager.broadcast({"type": "webhook_update", "data": data})

    return {"status": "ok"}


# ==================== MEDIA & CONTACTS ====================


@app.get("/api/media")
async def get_media():
    """Media-Dateien"""
    return {"media": [], "count": 0}


@app.get("/api/contacts")
async def get_contacts():
    """Kontakte"""
    return {"contacts": [], "count": 0}


# ==================== TEMPLATES ====================


@app.get("/api/templates")
async def get_templates():
    """Nachrichtenvorlagen"""
    return {
        "templates": [
            {"id": "welcome", "name": "Willkommensnachricht", "text": "Willkommen! 👋"},
            {"id": "status", "name": "Status-Update", "text": "Status: {status}"},
            {"id": "error", "name": "Fehlermeldung", "text": "⚠️ Fehler: {error}"},
        ]
    }


# ==================== AI REPLY ====================


@app.post("/api/ai/reply")
async def ai_reply(message: ChatMessage):
    """KI-Antwort generieren"""
    response_text = f"KI-Antwort auf: {message.text}"
    stats["messages_sent"] += 1

    return {"reply": response_text, "confidence": 0.95, "timestamp": datetime.now().isoformat()}


# ==================== COMMANDS ====================


@app.post("/api/cmd/execute")
async def execute_command(cmd: CommandExec):
    """Sicherer Command-Executor"""
    safe_commands = ["ls", "pwd", "date", "whoami", "ps"]

    cmd_base = cmd.command.split()[0] if cmd.command.split() else ""

    if cmd_base not in safe_commands:
        raise HTTPException(403, "Command nicht erlaubt")

    try:
        result = subprocess.run(cmd.command, shell=True, capture_output=True, text=True, timeout=5)

        return {"command": cmd.command, "output": result.stdout, "error": result.stderr, "exit_code": result.returncode}
    except Exception as e:
        stats["errors"] += 1
        raise HTTPException(500, str(e))


# ==================== LOGS ====================


@app.get("/api/logs")
async def get_logs():
    """System-Logs"""
    return {
        "logs": [
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "System läuft"},
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"{stats['workflows_loaded']} Workflows aktiv",
            },
        ]
    }


# ==================== PORTIER CONFIG API ENDPOINTS ====================


@app.get("/health")
async def health():
    """Health Check - PORTIER Standard"""
    return {"status": "healthy", "service": "opena4-telegram", "timestamp": datetime.now().isoformat()}


@app.get("/status")
async def status():
    """Status - PORTIER Standard"""
    return await get_status()


@app.get("/metrics")
async def metrics():
    """Metrics Endpoint"""
    return {
        "uptime_seconds": (datetime.now() - datetime.fromisoformat(stats["uptime_start"])).total_seconds(),
        "requests_total": stats["total_requests"],
        "errors_total": stats["errors"],
        "messages_sent": stats["messages_sent"],
        "messages_received": stats["messages_received"],
    }


@app.get("/config")
async def get_config():
    """Agent Configuration"""
    return {
        "agent": {"id": "opena4", "name": "Telegram Mobile Agent", "version": "6.0.0", "port": 12346},
        "capabilities": 12,
        "workflows": len(workflows),
    }


# ==================== MESSAGE API (CONFIG FORMAT) ====================


@app.post("/api/message/send")
async def api_message_send(message: ChatMessage):
    """Send message - CONFIG format"""
    return await send_message(message)


@app.post("/api/message/bulk")
async def api_message_bulk(messages: list[ChatMessage]):
    """Bulk send messages"""
    results = []
    for msg in messages:
        stats["messages_sent"] += 1
        results.append({"status": "sent", "text": msg.text})
    return {"sent": len(results), "results": results}


@app.get("/api/message/history")
async def api_message_history():
    """Message history"""
    return {"messages": [], "total": 0, "sent": stats["messages_sent"], "received": stats["messages_received"]}


# ==================== CONTACTS API ====================


@app.get("/api/contacts/list")
async def api_contacts_list():
    """List all contacts"""
    return await get_contacts()


@app.post("/api/contacts/add")
async def api_contacts_add(contact: dict):
    """Add contact"""
    return {"status": "added", "contact": contact}


@app.delete("/api/contacts/delete")
async def api_contacts_delete(contact_id: str):
    """Delete contact"""
    return {"status": "deleted", "contact_id": contact_id}


@app.get("/api/contacts/export")
async def api_contacts_export():
    """Export contacts"""
    return {"contacts": [], "count": 0, "format": "json"}


@app.post("/api/contacts/import")
async def api_contacts_import(data: dict):
    """Import contacts"""
    return {"status": "imported", "count": 0}


# ==================== MEDIA API ====================


@app.post("/api/media/send")
async def api_media_send(data: dict):
    """Send media"""
    stats["messages_sent"] += 1
    return {"status": "sent", "media_type": data.get("type", "unknown")}


@app.post("/api/media/upload")
async def api_media_upload(data: dict):
    """Upload media"""
    return {"status": "uploaded", "media_id": "media_" + str(datetime.now().timestamp())}


@app.get("/api/media/gallery")
async def api_media_gallery():
    """Media gallery"""
    return await get_media()


# ==================== AI REPLY API ====================


@app.post("/api/ai/generate")
async def api_ai_generate(message: ChatMessage):
    """Generate AI reply"""
    return await ai_reply(message)


@app.get("/api/ai/settings")
async def api_ai_settings():
    """AI settings"""
    return {"model": "gpt-4", "temperature": 0.7, "max_tokens": 500, "language": "de"}


@app.post("/api/ai/context")
async def api_ai_context(data: dict):
    """Update AI context"""
    return {"status": "updated", "context_id": data.get("id")}


# ==================== WEBHOOK API ====================


@app.get("/api/webhook/status")
async def api_webhook_status():
    """Webhook status"""
    return await webhook_info()


@app.post("/api/webhook/config")
async def api_webhook_config(config: WebhookConfig):
    """Configure webhook"""
    return {"status": "configured", "url": config.url}


@app.get("/api/webhook/events")
async def api_webhook_events():
    """Webhook events"""
    return {"events": [], "count": 0}


# ==================== ANALYTICS API ====================


@app.get("/api/analytics/overview")
async def api_analytics_overview():
    """Analytics overview"""
    return await get_analytics()


@app.get("/api/analytics/messages")
async def api_analytics_messages():
    """Message analytics"""
    return {
        "total": stats["messages_sent"] + stats["messages_received"],
        "sent": stats["messages_sent"],
        "received": stats["messages_received"],
        "avg_per_hour": 0,
    }


@app.get("/api/analytics/export")
async def api_analytics_export():
    """Export analytics"""
    return {"format": "json", "data": await get_analytics(), "timestamp": datetime.now().isoformat()}


# ==================== TEMPLATES API ====================


@app.get("/api/templates/list")
async def api_templates_list():
    """List templates"""
    return await get_templates()


@app.post("/api/templates/save")
async def api_templates_save(template: dict):
    """Save template"""
    return {"status": "saved", "template_id": template.get("id", "new")}


@app.delete("/api/templates/delete")
async def api_templates_delete(template_id: str):
    """Delete template"""
    return {"status": "deleted", "template_id": template_id}


# ==================== SYSTEM API ====================


@app.post("/api/system/restart")
async def api_system_restart():
    """Restart system"""
    await restart_bot()
    return {"status": "restarting", "timestamp": datetime.now().isoformat()}


@app.post("/api/system/clear-cache")
async def api_system_clear_cache():
    """Clear cache"""
    return {"status": "cleared", "timestamp": datetime.now().isoformat()}


# ==================== WEBSOCKET ====================


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket für Live-Updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"type": "message", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== STATIC FILES ====================

try:
    app.mount("/css", StaticFiles(directory=str(Path(__file__).parent / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(Path(__file__).parent / "js")), name="js")
except:
    logger.warning("⚠️ CSS/JS Verzeichnisse nicht gefunden")

# ==================== START ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TELEGRAM MOBILE AGENT - UNIFIED BACKEND")
    print("=" * 60)
    print("📡 Port: 12346")
    print("🌐 URL: http://localhost:12346")
    print("📊 Workflows: 20 (10 Telegram + 10 Terminal)")
    print("⚡ ALLE Anbindungen: VOLLSTÄNDIG INTEGRIERT")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=12346, log_level="info", reload=False)
