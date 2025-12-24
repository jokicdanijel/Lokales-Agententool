#!/usr/bin/env python3
"""
FastAPI Dashboard für Telegram Bot
"""

from datetime import datetime
from pathlib import Path

import psutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI(title="Telegram Bot Dashboard", version="1.0")

BASE_DIR = Path(__file__).parent


# Status endpoint
@app.get("/api/status")
async def get_status():
    """Gibt den Bot-Status zurück"""
    try:
        # Bot PID lesen
        pid_file = BASE_DIR / "telegram_bot.pid"
        bot_running = False
        bot_pid = None

        if pid_file.exists():
            with open(pid_file) as f:
                bot_pid = int(f.read().strip())
                bot_running = psutil.pid_exists(bot_pid)

        # System-Status
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "bot": {"running": bot_running, "pid": bot_pid},
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Logs endpoint
@app.get("/api/logs")
async def get_logs(lines: int = 50):
    """Gibt die letzten Log-Einträge zurück"""
    try:
        log_file = BASE_DIR / "telegram_bot.log"

        if not log_file.exists():
            return {"logs": []}

        with open(log_file) as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]

        return {"logs": [line.strip() for line in last_lines], "total_lines": len(all_lines)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Bot-Kontrolle
@app.post("/api/bot/{action}")
async def control_bot(action: str):
    """Steuert den Bot (start/stop/restart)"""
    try:
        script = BASE_DIR / "start_telegram_bot.sh"

        if not script.exists():
            raise HTTPException(status_code=404, detail="Start-Script nicht gefunden")

        if action not in ["start", "stop", "restart", "status"]:
            raise HTTPException(status_code=400, detail="Ungültige Aktion")

        import subprocess

        result = subprocess.run([str(script), action], capture_output=True, text=True, cwd=str(BASE_DIR))

        return {"action": action, "success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Root - Dashboard HTML
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serviert das Dashboard"""
    index_file = BASE_DIR / "index.html"

    if index_file.exists():
        return FileResponse(index_file)
    else:
        return HTMLResponse(
            """
            <html>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>🤖 Telegram Bot Dashboard</h1>
                    <p>API läuft auf Port 8000</p>
                    <ul style="list-style: none;">
                        <li><a href="/docs">📚 API Dokumentation</a></li>
                        <li><a href="/api/status">📊 Status</a></li>
                        <li><a href="/api/logs">📋 Logs</a></li>
                    </ul>
                </body>
            </html>
        """
        )


# Health Check
@app.get("/health")
async def health():
    """Health Check Endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
