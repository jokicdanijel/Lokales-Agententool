#!/bin/bash
# ELION PORTIER 3.0 - Agent Module Generator
# Erstellt config.py, security.py, models.py, sse_client.py für alle 15 Agents

BASE_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"

# Agent-Definitionen: DIR|AGENTS (comma-separated: id,name,kuerzel,port)
declare -a AGENT_DIRS=(
    "1.opena1&2_portier|opena1,Koordinator Portier,portp,12344;opena2,Archivator,archivp,12345"
    "2.opena3_openwebui|opena3,OpenWebUI Terminal,owuip,12347"
    "3.opena4_telegram|opena4,Telegram Agent,telep,12348"
    "4.opena5_vscode|opena5,VS Code Agent,vscop,12351"
    "5.opena6_browser|opena6,Browser Agent,browsep,12352"
    "6.opena7_email|opena7,Email Agent,emailp,12353"
    "7.opena8_whatsapp|opena8,WhatsApp Agent,whatsappp,12354"
    "8.opena9_telephone|opena9,Telefonie Agent,telephonep,12355"
    "9.opena10_call_tracking|opena10,Call Tracking Agent,calltrackp,12356"
    "10.opena11_unlock|opena11,Unlock Agent,unlockp,12357"
    "11.opena12_social_media|opena12,Social Media Agent,smp,12358"
    "12.opena13_influencer|opena13,Influencer Agent,influp,12359"
    "13.opena14_calendar|opena14,Calendar Agent,calp,12360"
    "14.opena15_html|opena15,HTML Creator,htmlp,12361"
    "15.opena16_shop|opena16,Shop Agent,shopp,12362"
)

create_config_py() {
    local dir="$1"
    local agent_id="$2"
    local agent_name="$3"
    local kuerzel="$4"
    local port="$5"

    cat > "${BASE_DIR}/${dir}/config.py" << CONFIGEOF
#!/usr/bin/env python3
"""
${agent_id} - ${agent_name}
Konfigurationsmodul

Port: ${port}
Kürzel: ${kuerzel}

PORTIER 3.0 konform
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PortPolicy:
    """PORTIER 3.0 Port Policy Enforcement"""

    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]

    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS

    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        origins = ["http://127.0.0.1:8080"]
        for port in cls.ALLOWED_RANGE:
            if port not in cls.FORBIDDEN_PORTS:
                origins.append(f"http://127.0.0.1:{port}")
        return origins


class ServiceConfig(BaseSettings):
    """Hauptkonfiguration für ${agent_id}"""

    service_name: str = "${agent_id}"
    kuerzel: str = "${kuerzel}"
    port: int = ${port}
    version: str = "3.0"

    bearer_token: str = Field(
        default="c899b90d-faf8-485b-afa4-078357cf5313",
        alias="BEARER_TOKEN"
    )

    base_dir: Path = Path(__file__).parent

    opena1_url: str = Field(default="http://127.0.0.1:12344", alias="OPENA1_URL")
    opena2_url: str = Field(default="http://127.0.0.1:12345", alias="OPENA2_URL")
    opena20_url: str = Field(default="http://127.0.0.1:12349", alias="OPENA20_URL")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"


class AgentInfo(BaseModel):
    """Agent-Informationen"""

    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Service Port")
    enabled: bool = Field(default=True)

    class Config:
        extra = "forbid"


_config: Optional[ServiceConfig] = None


def load_config() -> ServiceConfig:
    global _config
    if _config is None:
        _config = ServiceConfig()
        _config.data_dir.mkdir(exist_ok=True)
        _config.logs_dir.mkdir(exist_ok=True)
    return _config


__all__ = ["PortPolicy", "ServiceConfig", "AgentInfo", "load_config"]
CONFIGEOF
}

create_security_py() {
    local dir="$1"
    local agent_id="$2"
    local port="$3"
    local kuerzel="$4"

    cat > "${BASE_DIR}/${dir}/security.py" << SECEOF
#!/usr/bin/env python3
"""
${agent_id} - Security Module

Port: ${port}
Kürzel: ${kuerzel}

PORTIER 3.0 Security Layer
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Set
from functools import wraps
from collections import defaultdict

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

logger = logging.getLogger(__name__)

SECRET_KEYS: Set[str] = {
    "token", "auth", "password", "apikey", "api_key", "key",
    "secret", "credentials", "bearer", "authorization",
    "access_token", "refresh_token", "private_key", "session"
}


def mask_secrets(data: Any, mask_value: str = "***MASKED***") -> Any:
    if isinstance(data, dict):
        return {
            k: mask_value if any(secret in k.lower() for secret in SECRET_KEYS)
            else mask_secrets(v, mask_value)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item, mask_value) for item in data]
    return data


security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    if DEV_MODE and not credentials:
        logger.warning("DEV_MODE: Authentifizierung übersprungen")
        return "dev-mode"

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer Token erforderlich",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Bearer Token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return credentials.credentials


async def optional_verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    if not credentials:
        return None
    if credentials.credentials == BEARER_TOKEN:
        return credentials.credentials
    return None


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, client_id: str) -> None:
        cutoff = time.time() - self.window_seconds
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]

    def is_allowed(self, request: Request) -> bool:
        client_id = self._get_client_id(request)
        self._clean_old_requests(client_id)
        if len(self._requests[client_id]) >= self.max_requests:
            return False
        self._requests[client_id].append(time.time())
        return True

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


default_limiter = RateLimiter(max_requests=100, window_seconds=60)
api_limiter = RateLimiter(max_requests=60, window_seconds=60)


class PortPolicyEnforcer:
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]

    @classmethod
    def validate_origin(cls, origin: str) -> bool:
        if not origin:
            return True
        try:
            if ":" in origin:
                port_str = origin.split(":")[-1]
                if port_str.isdigit():
                    port = int(port_str)
                    return port in cls.ALLOWED_RANGE or port == 8080
        except (ValueError, IndexError):
            pass
        return True


__all__ = [
    "BEARER_TOKEN", "DEV_MODE", "SECRET_KEYS", "mask_secrets",
    "security", "verify_token", "optional_verify_token",
    "RateLimiter", "default_limiter", "api_limiter", "PortPolicyEnforcer"
]
SECEOF
}

create_models_py() {
    local dir="$1"
    local agent_id="$2"
    local port="$3"
    local kuerzel="$4"

    cat > "${BASE_DIR}/${dir}/models.py" << MODELSEOF
#!/usr/bin/env python3
"""
${agent_id} - Pydantic Models

Port: ${port}
Kürzel: ${kuerzel}

PORTIER 3.0 Strict JSON Schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class SafepointCategory(str, Enum):
    CMD = "CMD"
    RESP = "RESP"
    ROUTE = "ROUTE"
    DISPATCH = "DISPATCH"


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status (ok/error)")
    service: str = Field(..., description="Service-Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Port-Nummer")
    uptime_seconds: float = Field(..., description="Uptime in Sekunden")
    version: str = Field(..., description="Version")
    strict: bool = Field(True, description="Strict JSON Mode")


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., description="Aktion")
    target: Optional[str] = Field(None, description="Ziel-Agent")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameter")


class CommandResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status (success/error)")
    action: str = Field(..., description="Ausgeführte Aktion")
    result: Optional[Dict[str, Any]] = Field(None, description="Ergebnis")
    error: Optional[str] = Field(None, description="Fehlermeldung")
    timestamp: str = Field(..., description="Timestamp")


class InvokeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., description="Aktion")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameter")


class SafepointRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sp_timestamp: int = Field(..., description="Unix Timestamp")
    timestamp: str = Field(..., description="ISO 8601 Timestamp")
    source: str = Field(..., description="Quell-Agent")
    destination: str = Field(..., description="Ziel-Agent")
    category: SafepointCategory = Field(..., description="Kategorie")
    request_id: str = Field(..., description="Request ID")
    payload: Dict[str, Any] = Field(..., description="Payload")
    strict: bool = Field(True, description="Strict Mode")


class APIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = Field(..., description="Erfolg")
    data: Optional[Any] = Field(None, description="Daten")
    error: Optional[str] = Field(None, description="Fehlermeldung")
    timestamp: str = Field(..., description="Response Timestamp")


__all__ = [
    "AgentStatus", "SafepointCategory", "HealthResponse",
    "CommandRequest", "CommandResponse", "InvokeRequest",
    "SafepointRecord", "APIResponse"
]
MODELSEOF
}

create_sse_client_py() {
    local dir="$1"
    local agent_id="$2"
    local port="$3"
    local kuerzel="$4"

    cat > "${BASE_DIR}/${dir}/sse_client.py" << SSEEOF
#!/usr/bin/env python3
"""
${agent_id} - SSE Client Module

Port: ${port}
Kürzel: ${kuerzel}

SSE Client für opena20 Dashboard Events
Safepoint Client für opena2 Archivierung
"""

import asyncio
import json
import logging
import os
import time
import uuid
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, Optional, AsyncGenerator, Callable, Awaitable
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)

OPENA20_URL = os.getenv("OPENA20_URL", "http://127.0.0.1:12349")
OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")


@dataclass
class SSEEvent:
    event_type: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: Optional[str] = None


class SSEClient:
    """SSE Client für Verbindung zu opena20 Dashboard"""

    def __init__(
        self,
        base_url: str = OPENA20_URL,
        bearer_token: str = BEARER_TOKEN,
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._running = False

    async def connect(self) -> None:
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout
        )
        self._running = True

    async def disconnect(self) -> None:
        self._running = False
        if self._client:
            await self._client.aclose()
            self._client = None

    async def subscribe(
        self,
        endpoint: str = "/api/events/live",
        on_event: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not self._client:
            await self.connect()

        try:
            async with self._client.stream("GET", endpoint) as response:
                response.raise_for_status()
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    while "\n\n" in buffer:
                        event_str, buffer = buffer.split("\n\n", 1)
                        event = self._parse_event(event_str)
                        if event:
                            if on_event:
                                await on_event(event)
                            yield event
                    if not self._running:
                        break
        except Exception as e:
            logger.error(f"SSE Error: {e}")
            raise

    def _parse_event(self, event_str: str) -> Optional[Dict[str, Any]]:
        event_data: Dict[str, Any] = {}
        for line in event_str.strip().split("\n"):
            if line.startswith("event:"):
                event_data["event_type"] = line[6:].strip()
            elif line.startswith("data:"):
                try:
                    event_data["data"] = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    event_data["data"] = line[5:].strip()
            elif line.startswith("id:"):
                event_data["event_id"] = line[3:].strip()
        return event_data if event_data else None


class SafepointClient:
    """Client für Safepoint-Archivierung via opena2"""

    def __init__(
        self,
        base_url: str = OPENA2_URL,
        bearer_token: str = BEARER_TOKEN,
        source_agent: str = "${agent_id}"
    ):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.source_agent = source_agent
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> None:
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=10.0
        )

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def write_safepoint(
        self,
        category: str,
        destination: str,
        payload: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Optional[str]:
        if not self._client:
            await self.connect()

        safepoint = {
            "sp_timestamp": int(time.time() * 1000),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": self.source_agent,
            "destination": destination,
            "category": category,
            "request_id": request_id or str(uuid.uuid4())[:8],
            "payload": payload,
            "strict": True
        }

        try:
            response = await self._client.post("/api/safepoint", json=safepoint)
            response.raise_for_status()
            return safepoint["request_id"]
        except Exception as e:
            logger.error(f"Safepoint write failed: {e}")
            return None


_sse_client: Optional[SSEClient] = None
_safepoint_client: Optional[SafepointClient] = None


def get_sse_client() -> SSEClient:
    global _sse_client
    if _sse_client is None:
        _sse_client = SSEClient()
    return _sse_client


def get_safepoint_client() -> SafepointClient:
    global _safepoint_client
    if _safepoint_client is None:
        _safepoint_client = SafepointClient()
    return _safepoint_client


__all__ = [
    "SSEEvent", "SSEClient", "SafepointClient",
    "get_sse_client", "get_safepoint_client"
]
SSEEOF
}

# Hauptschleife
echo "🚀 ELION PORTIER 3.0 - Agent Module Generator"
echo "============================================="
echo ""

for entry in "${AGENT_DIRS[@]}"; do
    dir="${entry%%|*}"
    agents="${entry#*|}"

    echo "📁 Verarbeite: ${dir}"

    # Mehrere Agents pro Verzeichnis (z.B. opena1&2)
    IFS=';' read -ra AGENT_LIST <<< "$agents"
    for agent_entry in "${AGENT_LIST[@]}"; do
        IFS=',' read -r agent_id agent_name kuerzel port <<< "$agent_entry"

        echo "   ✓ ${agent_id} (${kuerzel}, Port ${port})"

        # Verzeichnis erstellen falls nicht vorhanden
        mkdir -p "${BASE_DIR}/${dir}"

        # Module erstellen
        create_config_py "$dir" "$agent_id" "$agent_name" "$kuerzel" "$port"
        create_security_py "$dir" "$agent_id" "$port" "$kuerzel"
        create_models_py "$dir" "$agent_id" "$port" "$kuerzel"
        create_sse_client_py "$dir" "$agent_id" "$port" "$kuerzel"
    done
    echo ""
done

echo "============================================="
echo "✅ Alle Module erstellt!"
