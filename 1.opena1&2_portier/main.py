"""
3.opena1_coordinator/main.py – Portier Coordinator Service (opena1)
============================================================================
FastAPI service for coordinating Portier agent communication.

Port: 12344
Endpoints:
  GET /health
  POST /log/opena1
  
Usage:
  cd 3.opena1_coordinator
  python main.py
  # → Listening on http://127.0.0.1:12344
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from src.portier_service_base import (
    PortierServiceBase,
    PortierServiceConfig,
    PortPolicyMiddleware
)

# ─────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────

config = PortierServiceConfig(
    service_name="opena1",
    service_port=int(os.getenv("OPENA1_PORT", "12344")),
    allowed_port_min=12344,
    allowed_port_max=12399,
    bind_addr=os.getenv("BIND_ADDR", "127.0.0.1"),
    archiv_base=os.getenv("ARCHIV_BASE", "./archiv")
)

# ─────────────────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="opena1 – Portier Coordinator",
    description="Coordinator service for Portier agent orchestration",
    version="1.0.0"
)

# Middleware for port-policy enforcement
PortPolicyMiddleware(app, config)

# Initialize base service
service_base = PortierServiceBase(config)

# Setup endpoints
service_base.setup_health_endpoint(app)
service_base.setup_safepoints(app, config.archiv_base)

# ─────────────────────────────────────────────────────────────────────────
# ROOT ENDPOINT
# ─────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "opena1",
        "status": "online",
        "port": config.service_port,
        "docs": "/docs"
    }

# ─────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = config.service_port
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║           opena1 – Portier Coordinator                    ║
    ╚════════════════════════════════════════════════════════════╝
    
    Port:      {port}
    Bind:      {config.bind_addr}
    Docs:      http://{config.bind_addr}:{port}/docs
    Health:    http://{config.bind_addr}:{port}/health
    
    Starting server...
    """)
    
    uvicorn.run(
        "main:app",
        host=config.bind_addr,
        port=port,
        reload=False,
        log_level="info"
    )
