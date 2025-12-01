#!/usr/bin/env python3
"""
OpenWebUI Bridge für HYPER-DASHBOARD 3.0 - PORT 12346
opena3 → opena20 Integration Bridge mit PORTIER 3.0 Compliance

Features:
- OpenWebUI Integration (Port 12346)
- opena3 Terminal Agent Communication (Port 12347)
- HYPER-DASHBOARD 3.0 Status Integration (Port 12349)
- Real-time Agent Monitoring
- Workflow Execution Bridge
- PORTIER 3.0 Option-2-Flow Compliance
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import aiohttp
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

# Configuration - UPDATED FOR PORT 12346
OPENWEBUI_PORT = 12346  # OpenWebUI integration port
OPENA3_PORT = 12347     # opena3 terminal agent port  
DASHBOARD_PORT = 12349  # HYPER-DASHBOARD 3.0 port
OPENWEBUI_URL = "http://127.0.0.1:8080"  # OpenWebUI UI (forbidden for backend)
OPENA3_URL = f"http://127.0.0.1:{OPENA3_PORT}"  # opena3 terminal agent
DASHBOARD_URL = f"http://127.0.0.1:{DASHBOARD_PORT}"

class OpenWebUIBridge:
    """Bridge between OpenWebUI and HYPER-DASHBOARD 3.0"""
    
    def __init__(self):
        self.logger = logging.getLogger("openwebui_bridge")
        self.session = None
    
    async def start(self):
        """Start the bridge"""
        self.session = aiohttp.ClientSession()
        self.logger.info("🌉 OpenWebUI Bridge started")
    
    async def stop(self):
        """Stop the bridge"""
        if self.session:
            await self.session.close()
        self.logger.info("🛑 OpenWebUI Bridge stopped")
    
    async def get_dashboard_status(self) -> Dict:
        """Get HYPER-DASHBOARD 3.0 status"""
        try:
            async with self.session.get(f"{DASHBOARD_URL}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Dashboard unreachable: HTTP {response.status}"}
        except Exception as e:
            return {"error": f"Dashboard connection failed: {str(e)}"}
    
    async def get_all_agents_status(self, bearer_token: str) -> Dict:
        """Get all agents status from dashboard"""
        try:
            headers = {"Authorization": f"Bearer {bearer_token}"}
            async with self.session.get(f"{DASHBOARD_URL}/api/status/all", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Dashboard API error: HTTP {response.status}"}
        except Exception as e:
            return {"error": f"Dashboard API failed: {str(e)}"}
    
    async def execute_workflow(self, workflow_id: str, workflow_data: Dict, bearer_token: str) -> Dict:
        """Execute workflow via dashboard"""
        try:
            headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json"
            }
            async with self.session.post(
                f"{DASHBOARD_URL}/api/workflows/{workflow_id}",
                headers=headers,
                json=workflow_data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Workflow execution failed: HTTP {response.status}"}
        except Exception as e:
            return {"error": f"Workflow execution error: {str(e)}"}

# FastAPI App
app = FastAPI(
    title="OpenWebUI Bridge - HYPER-DASHBOARD 3.0",
    description="Bridge between OpenWebUI and HYPER-DASHBOARD 3.0",
    version="3.0.0"
)

bridge = OpenWebUIBridge()

@app.on_event("startup")
async def startup_event():
    await bridge.start()

@app.on_event("shutdown")
async def shutdown_event():
    await bridge.stop()

@app.get("/health")
async def health_check():
    """Bridge health check"""
    dashboard_status = await bridge.get_dashboard_status()
    
    return {
        "status": "ok",
        "service": "openwebui-bridge-3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dashboard_status": dashboard_status,
        "openwebui_port": OPENWEBUI_PORT,
        "dashboard_port": DASHBOARD_PORT
    }

@app.get("/api/dashboard/status")
async def get_dashboard_status():
    """Get HYPER-DASHBOARD 3.0 status"""
    return await bridge.get_dashboard_status()

@app.post("/api/dashboard/agents")
async def get_agents_status(request: Request):
    """Get all agents status (requires bearer token in body)"""
    try:
        body = await request.json()
        bearer_token = body.get("bearer_token")
        
        if not bearer_token:
            raise HTTPException(status_code=400, detail="bearer_token required")
        
        result = await bridge.get_all_agents_status(bearer_token)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dashboard/workflow/{workflow_id}")
async def execute_workflow(workflow_id: str, request: Request):
    """Execute workflow via dashboard"""
    try:
        body = await request.json()
        bearer_token = body.get("bearer_token")
        workflow_data = body.get("workflow_data", {})
        
        if not bearer_token:
            raise HTTPException(status_code=400, detail="bearer_token required")
        
        result = await bridge.execute_workflow(workflow_id, workflow_data, bearer_token)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/openwebui/commands")
async def get_available_commands():
    """Get available OpenWebUI commands"""
    return {
        "commands": [
            {
                "command": "/dashboard",
                "description": "Get HYPER-DASHBOARD 3.0 status",
                "usage": "/dashboard"
            },
            {
                "command": "/agents",
                "description": "List all agents status",
                "usage": "/agents [bearer_token]"
            },
            {
                "command": "/workflow",
                "description": "Execute workflow",
                "usage": "/workflow <workflow_id> [data] [bearer_token]"
            },
            {
                "command": "/health",
                "description": "Check system health",
                "usage": "/health"
            }
        ]
    }

def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    logger = logging.getLogger("main")
    logger.info("🌉 Starting OpenWebUI Bridge for HYPER-DASHBOARD 3.0")
    
    uvicorn.run(
        "openwebui_bridge:app",
        host="127.0.0.1",
        port=OPENWEBUI_PORT,
        reload=False,
        access_log=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()