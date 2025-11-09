"""
portier_service_base.py – Base Template for Portier Services
============================================================================
Provides standardized endpoints for all core Portier services:
  • GET /health – Standard health check
  • POST /log/{service} – Log endpoint (opena1)
  • POST /dispatch/{service} – Dispatch endpoint (kordp)
  • POST /store/{service} – Store endpoint (archivp)
  • POST /finalize/{service} – Finalize endpoint (opena2)

Usage:
  from portier_service_base import PortierServiceBase
  
  app = FastAPI()
  base = PortierServiceBase(
      service_name="opena1",
      service_port=12344,
      allowed_port_min=12344,
      allowed_port_max=12399
  )
  base.setup_health_endpoint(app)
  base.setup_safepoints(app, archiv_dir="/path/to/archiv")
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel


# ─────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────
# SERVICE BASE CLASS
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class PortierServiceConfig:
    """Service configuration"""
    service_name: str
    service_port: int
    allowed_port_min: int = 12344
    allowed_port_max: int = 12399
    bind_addr: str = "127.0.0.1"
    archiv_base: Optional[str] = None


class PortierServiceBase:
    """
    Base class providing standardized Portier service endpoints.
    
    Subclass and customize as needed:
    
    class MyService(PortierServiceBase):
        def __init__(self):
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
        async def health_check():
            """Standard health check endpoint"""
            return HealthResponse(
                service=self.config.service_name,
                status="online",
                base=f"http://{self.config.bind_addr}:{self.config.service_port}",
                port=self.config.service_port,
                port_policy={
                    "allowed_min": self.config.allowed_port_min,
                    "allowed_max": self.config.allowed_port_max,
                    "current_port": self.config.service_port,
                    "compliant": (
                        self.config.allowed_port_min 
                        <= self.config.service_port 
                        <= self.config.allowed_port_max
                    )
                },
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
    
    # ─────────────────────────────────────────────────────────────────────
    # SAFEPOINT ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    
    def setup_safepoints(self, app: FastAPI, archiv_dir: str) -> None:
        """Register safepoint endpoints based on service type"""
        
        # Ensure archiv directory exists
        Path(archiv_dir).mkdir(parents=True, exist_ok=True)
        index_path = Path(archiv_dir) / "index.jsonl"
        
        # opena1: /log/opena1
        if self.config.service_name == "opena1":
            @app.post("/log/opena1", response_model=SafepointResponse)
            async def log_endpoint(req: SafepointRequest):
                return await self._write_safepoint(
                    req, archiv_dir, index_path
                )
        
        # kordp: /dispatch/kordp
        elif self.config.service_name == "kordp":
            @app.post("/dispatch/kordp", response_model=SafepointResponse)
            async def dispatch_endpoint(req: SafepointRequest):
                return await self._write_safepoint(
                    req, archiv_dir, index_path
                )
        
        # archivp: /store/archivp
        elif self.config.service_name == "archivp":
            @app.post("/store/archivp", response_model=SafepointResponse)
            async def store_endpoint(req: SafepointRequest):
                return await self._write_safepoint(
                    req, archiv_dir, index_path
                )
        
        # opena2: /finalize/opena2
        elif self.config.service_name == "opena2":
            @app.post("/finalize/opena2", response_model=SafepointResponse)
            async def finalize_endpoint(req: SafepointRequest):
                return await self._write_safepoint(
                    req, archiv_dir, index_path
                )
    
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
            
            # Filename: SP<number>_src→dst_KIND.json
            filename = f"SP{ts_numeric}_{req.src}→{req.dst}_{req.kind.value}.json"
            filepath = Path(archiv_dir) / filename
            
            # Write safepoint JSON
            safepoint_data = {
                "timestamp": timestamp,
                "src": req.src,
                "dst": req.dst,
                "kind": req.kind.value,
                "payload": req.payload
            }
            
            with open(filepath, "w") as f:
                json.dump(safepoint_data, f, indent=2)
            
            # Append to index
            index_entry = {
                "path": filename,
                "ts": timestamp,
                "src": req.src,
                "dst": req.dst,
                "kind": req.kind.value
            }
            
            with open(index_path, "a") as f:
                f.write(json.dumps(index_entry) + "\n")
            
            return SafepointResponse(
                written=True,
                path=str(filepath),
                timestamp=timestamp,
                index_updated=True
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to write safepoint: {str(e)}"
            )


# ─────────────────────────────────────────────────────────────────────────
# MIDDLEWARE: PORT-POLICY VALIDATION
# ─────────────────────────────────────────────────────────────────────────

class PortPolicyMiddleware:
    """Middleware to enforce port-policy compliance"""
    
    def __init__(self, app: FastAPI, config: PortierServiceConfig):
        self.app = app
        self.config = config
        
        @app.middleware("http")
        async def enforce_port_policy(request: Request, call_next):
            # Add port-policy header to response
            response = await call_next(request)
            response.headers["X-Portier-Port-Policy"] = (
                f"{config.allowed_port_min}-{config.allowed_port_max}"
            )
            response.headers["X-Portier-Service"] = config.service_name
            response.headers["X-Portier-Port"] = str(config.service_port)
            return response
