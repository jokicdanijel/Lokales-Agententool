# Dashboard Konfiguration
# Strict Mode ist immer aktiv

import os
from pathlib import Path

# Basis-Konfiguration
BASE_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt")

# Port-Konfiguration
DASHBOARD_PORT = 12344  # Hauptport für Dashboard
PORT_RANGE = range(12344, 12400)  # Erlaubte Ports
FORBIDDEN_PORTS = [8080]  # Verbotene Ports

# Pfad-Konfiguration
ARCHIVE_PATH = PROJECT_ROOT / "1.opena1&2_portier" / "archivp"
TEMPLATES_PATH = BASE_DIR / "templates"

# Sicherheit
TOKEN_REQUIRED = True
RATE_LIMIT = 60  # Requests pro Minute
RATE_LIMIT_WINDOW = 60  # Sekunden

# Safepoint-Konfiguration
SAFEPOINT_FORMAT = "SP{timestamp}_{src}→{dst}_{kind}.json"
INDEX_FILE = ARCHIVE_PATH / "index.jsonl"

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Health-Check
HEALTH_CHECK_INTERVAL = 60  # Sekunden
HEALTH_CHECK_TIMEOUT = 5  # Sekunden

# Event-Stream
SSE_RETRY_TIMEOUT = 3000  # Millisekunden
MAX_EVENTS_BUFFER = 1000


# OpenWebUI-Konfiguration
class OpenWebUIConfig:
    """Konfiguration für OpenWebUI-Integration"""

    url: str = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
    agent_port: int = int(os.getenv("OPENWEBUI_AGENT_PORT", "12347"))
    adapter_port: int = int(os.getenv("OPENWEBUI_ADAPTER_PORT", "12350"))
    timeout: int = int(os.getenv("OPENWEBUI_TIMEOUT", "30"))

    @classmethod
    def to_dict(cls):
        return {"url": cls.url, "agent_port": cls.agent_port, "adapter_port": cls.adapter_port, "timeout": cls.timeout}


# Agenten-Konfiguration
AGENTS = {
    "opena1": {
        "role": "Koordinator",
        "base_path": PROJECT_ROOT / "1.opena1&2_portier" / "opena1",
        "endpoints": {"log": "/log/opena1"},
    },
    "opena2": {
        "role": "Archivator",
        "base_path": PROJECT_ROOT / "1.opena1&2_portier" / "opena2",
        "endpoints": {"finalize": "/finalize/opena2", "store": "/store/archivp"},
    },
    "opena3": {
        "role": "OpenWebUI Agent",
        "port": OpenWebUIConfig.agent_port,
        "endpoints": {"health": "/health", "command": "/command"},
    },
    "opena19": {
        "role": "Dashboard Backend",
        "base_path": PROJECT_ROOT / "19.dashboard_agent",
        "endpoints": {"status": "/api/status", "command": "/api/command", "events": "/api/events/live"},
    },
}

# Frontend-Konfiguration
UI_TEMPLATES = {"base": "base.html", "dashboard": "dashboard.html", "agent": "agent.html", "error": "error.html"}

# Strict Mode Validation
assert all(12344 <= port <= 12399 for port in PORT_RANGE), "Ungültiger Port-Bereich"
assert all(path.exists() for path in [ARCHIVE_PATH, TEMPLATES_PATH]), "Pfade nicht gefunden"
