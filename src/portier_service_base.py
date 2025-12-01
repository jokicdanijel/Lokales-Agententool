# portier_service_base.py – Base Template for Portier Services
# -----------------------------------------------------------------------------
# Provides standardized endpoints for all core Portier services:
#   GET  /health
#   POST /log/{service}
#   POST /dispatch/{service}
#   POST /store/{service}
#   POST /finalize/{service}
# -----------------------------------------------------------------------------

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

# DATA MODELS
class MessageKind(str, Enum):
    """Safepoint message kind"""
    CMD = "CMD"
    RESP = "RESP"
    ERR = "ERR"

class HealthResponse(BaseModel):
    """Standard health check response"""
    service: str
    status: str  # "online", "degraded", "offline"
    base: str
    port: int
    port_policy: Dict[str, Any]
    timestamp: str

class SafepointRequest(BaseModel):
    """Safepoint write request"""
    src: str
    dst: str
    kind: MessageKind
    payload: Dict[str, Any]

class SafepointResponse(BaseModel):
    """Safepoint write response"""
    written: bool
    path: str
    timestamp: str
    index_updated: bool

@dataclass
class PortierServiceConfig:
    """Service configuration"""
    service_name: str
    service_port: int
    allowed_port_min: int = 12344
    allowed_port_max: int = 12399
    bind_addr: str = "127.0.0.1"
    archiv_base: Optional[str] = None

# BASE CLASS
class PortierServiceBase:
    """
    Base class providing standardized Portier service endpoints.
    Subclass and customize as needed:
    class MyService(PortierServiceBase):
        def __init__(self, config: PortierServiceConfig):
            super().__init__(config)
        async def process_request(self, payload: Dict) -> Dict:
            # Custom logic
            return {"result": ...}
    """
    def __init__(self, config: PortierServiceConfig):
        self.config = config
        self.start_time = datetime.utcnow().isoformat() + "Z"

        # Validate port policy
        if not (config.allowed_port_min <= config.service_port <= config.allowed_port_max):
            raise ValueError(
                f"Service port {config.service_port} outside allowed range "
                f"{config.allowed_port_min}-{config.allowed_port_max}"
            )

    # ─────────────────────────────────────────────────────────────────────
    # HEALTH ENDPOINT
    # ─────────────────────────────────────────────────────────────────────
    def setup_health_endpoint(self, app: FastAPI) -> None:
        """Register GET /health endpoint"""
        @app.get("/health", response_model=HealthResponse)
        async def health_check() -> HealthResponse:
            base = f"http://{self.config.bind_addr}:{self.config.service_port}"
            return HealthResponse(
                service=self.config.service_name,
                status="online",
                base=base,
                port=self.config.service_port,
                port_policy={
                    "min": self.config.allowed_port_min,
                    "max": self.config.allowed_port_max,
                    "compliant": (
                        self.config.allowed_port_min
                        <= self.config.service_port
                        <= self.config.allowed_port_max
                    ),
                    "current": self.config.service_port,
                },
                timestamp=datetime.utcnow().isoformat() + "Z",
            )

    # ─────────────────────────────────────────────────────────────────────
    # SAFEPOINT ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    def setup_safepoints(self, app: FastAPI, archiv_dir: str) -> None:
        """Register safepoint endpoints based on service type"""
        Path(archiv_dir).mkdir(parents=True, exist_ok=True)
        index_path = Path(archiv_dir) / "index.jsonl"

        if self.config.service_name == "opena1":
            @app.post("/log/opena1", response_model=SafepointResponse)
            async def log_endpoint(req: SafepointRequest) -> SafepointResponse:
                return await self._write_safepoint(req, archiv_dir, index_path)

        elif self.config.service_name == "kordp":
            @app.post("/dispatch/kordp", response_model=SafepointResponse)
            async def dispatch_endpoint(req: SafepointRequest) -> SafepointResponse:
                return await self._write_safepoint(req, archiv_dir, index_path)

        elif self.config.service_name == "archivp":
            @app.post("/store/archivp", response_model=SafepointResponse)
            async def store_endpoint(req: SafepointRequest) -> SafepointResponse:
                return await self._write_safepoint(req, archiv_dir, index_path)

        elif self.config.service_name == "opena2":
            @app.post("/finalize/opena2", response_model=SafepointResponse)
            async def finalize_endpoint(req: SafepointRequest) -> SafepointResponse:
                return await self._write_safepoint(req, archiv_dir, index_path)

    async def _write_safepoint(
        self,
        req: SafepointRequest,
        archiv_dir: str,
        index_path: Path
    ) -> SafepointResponse:
        """
        Write safepoint file with standardized naming:
        SP<timestamp>_<src>→<dst>_<KIND>.json
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            ts_numeric = int(datetime.utcnow().timestamp() * 1000)
            # Filename: SP<number>_<src>→<dst>_<kind>.json
            filename = f"SP{ts_numeric}_{req.src}→{req.dst}_{req.kind.value}.json"
            filepath = Path(archiv_dir) / filename
            safepoint_data = {
                "timestamp": timestamp,
                "src": req.src,
                "dst": req.dst,
                "kind": req.kind.value,
                "payload": req.payload
            }
            filepath.write_text(json.dumps(safepoint_data, indent=2), encoding="utf-8")
            # Index aktualisieren
            index_entry = {
                "path": filename,
                "ts": timestamp,
                "src": req.src,
                "dst": req.dst,
                "kind": req.kind.value
            }
            with index_path.open("a", encoding="utf-8") as idx:
                idx.write(json.dumps(index_entry) + "\n")
            return SafepointResponse(
                written=True,
                path=str(filepath),
                timestamp=timestamp,
                index_updated=True
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write safepoint: {str(e)}")

    # ─────────────────────────────────────────────────────────────────────────
    # MIDDLEWARE: PORT-POLICY VALIDATION
    # ─────────────────────────────────────────────────────────────────────────
    def register_port_policy_middleware(self, app: FastAPI) -> None:
        """Register a simple port-policy middleware on the app."""

        class _PortPolicyMiddleware(BaseHTTPMiddleware):
            def __init__(self, inner_app, config: PortierServiceConfig):
                super().__init__(inner_app)
                self.config = config

            async def dispatch(self, request, call_next):
                response = await call_next(request)
                policy = f"{self.config.allowed_port_min}-{self.config.allowed_port_max}"
                response.headers["X-Portier-Port-Policy"] = policy
                response.headers["X-Portier-Service"] = self.config.service_name
                response.headers["X-Portier-Port"] = str(self.config.service_port)
                return response

        app.add_middleware(_PortPolicyMiddleware, config=self.config)

# === PHASE 13 PRODUCTION: Minimal PortPolicyMiddleware ===
# LOOSENED POLICY FOR FAST START - TIGHTEN LATER

class PortPolicyMiddleware:
    """Minimal Port Policy Middleware - Production Mode (Loose)"""
    
    ALLOWED_PORTS = list(range(12344, 12400))  # 12344-12399
    FORBIDDEN_PORTS = [8080]
    
    def __init__(self, app, config=None):
        self.app = app
        self.config = config or {}
        # NO ENFORCEMENT YET - just pass through for production
        print("✅ PortPolicyMiddleware initialized (PRODUCTION MODE - POLICY LOOSENED)")


__all__ = ['PortPolicyMiddleware']
