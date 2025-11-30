#!/usr/bin/env python3
"""
opena21 - Workflow Engine Agent
Port: 12364  
Kürzel: workflowp
Version: 2.0
Status: ✅ Production

Multi-Agent Workflow Orchestrierung für PORTIER 3.0.
Ermöglicht Definition, Ausführung und Monitoring von Multi-Step-Workflows.

Integration Points:
- Option-2-Flow: OpenAI → opena1 → opena2 → kordp → workflowp
- Safepoints: Automatische Archivierung über opena2
- Agent Coordination: HTTP-Calls via kordp Gateway
- Tool Registry: Registrierung als 'workflowp' Tool
"""

import os
import sys
import time
import json
import asyncio
import httpx
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
import uvicorn
from dotenv import load_dotenv

# Environment laden
load_dotenv()

# Konfiguration
PORT = int(os.getenv("OPENA21_PORT", "12364"))
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
SERVICE_NAME = "opena21"
PROGRAM_TARGET = "workflowp"
VERSION = "2.0"

# Portier Integration URLs
PORTIER_URL = os.getenv("PORTIER_URL", "http://127.0.0.1:12344")
OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
KORDP_URL = os.getenv("KORDP_URL", "http://127.0.0.1:12346")

# FastAPI App mit PORTIER 3.0 Standards
app = FastAPI(
    title=f"{SERVICE_NAME} - Workflow Engine",
    description="Multi-Agent Workflow Orchestration für PORTIER 3.0 - Option-2-Flow kompatibel",
    version=VERSION,
    docs_url="/docs" if not BEARER_TOKEN else None,  # Docs nur in DEV-Mode
    redoc_url="/redoc" if not BEARER_TOKEN else None
)

# CORS für Port-Policy Compliance (12344-12399 erlaubt)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:12349", "http://127.0.0.1:12344"],  # Dashboard + Portier
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security & Monitoring
security = HTTPBearer()
start_time = time.time()
http_client = httpx.AsyncClient(timeout=30.0)


# ==================== Schemas ====================

class WorkflowState(str, Enum):
    """Workflow-Zustandstypen"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepDefinition(BaseModel):
    """Definition eines Workflow-Steps mit PORTIER 3.0 Integration"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Name des Steps")
    action: str = Field(..., description="Aktion (z.B. 'call_agent', 'transform_data', 'condition')")
    agent: Optional[str] = Field(None, description="Ziel-Agent (opena3-opena20, kordp)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Step-Parameter")
    timeout: int = Field(30, ge=5, le=300, description="Timeout in Sekunden (5-300)")
    retry_count: int = Field(0, ge=0, le=5, description="Anzahl Retry-Versuche (0-5)")
    condition: Optional[str] = Field(None, description="Bedingung für Step-Ausführung (JSON-Path)")
    on_failure: Optional[str] = Field("stop", description="Verhalten bei Fehler (stop|continue|retry)")
    depends_on: Optional[List[str]] = Field(None, description="Step-Abhängigkeiten")


class WorkflowDefinition(BaseModel):
    """Vollständige Workflow-Definition"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Workflow-Name")
    description: Optional[str] = Field(None, description="Workflow-Beschreibung")
    steps: List[StepDefinition] = Field(..., description="Liste der Steps")
    timeout: int = Field(300, description="Gesamtzeit Timeout in Sekunden")


class ExecuteRequest(BaseModel):
    """Request zum Starten eines Workflows"""
    model_config = ConfigDict(extra="forbid")
    
    workflow_name: str = Field(..., description="Name des auszuführenden Workflows")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input-Parameter")
    mode: str = Field("sync", description="Ausführungsmodus (sync/async)")


class WorkflowStatus(BaseModel):
    """Status eines laufenden/abgeschlossenen Workflows"""
    model_config = ConfigDict(extra="forbid")
    
    workflow_id: str = Field(..., description="Eindeutige Workflow-ID")
    workflow_name: str = Field(..., description="Workflow-Name")
    state: WorkflowState = Field(..., description="Aktueller Zustand")
    current_step: Optional[str] = Field(None, description="Aktueller Step (wenn running)")
    started_at: str = Field(..., description="Start-Zeitstempel (ISO 8601)")
    completed_at: Optional[str] = Field(None, description="Completion-Zeitstempel")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Workflow-Outputs")
    error: Optional[str] = Field(None, description="Fehlermeldung (wenn failed)")


class InvokeRequest(BaseModel):
    """Generic Invoke Request für Option-2-Flow Kompatibilität"""
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(..., description="Aktion (z.B. 'execute_workflow', 'get_status')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action-Parameter")


class HealthResponse(BaseModel):
    """Health-Check Response - PORTIER 3.0 Standard"""
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="Status (ok/error)")
    service: str = Field(..., description="Service-Name")
    port: int = Field(..., description="Port-Nummer")
    program_target: str = Field(..., description="Programm-Ziel (kordp-Kürzel)")
    uptime_seconds: float = Field(..., description="Uptime in Sekunden")
    version: str = Field(..., description="Version")
    workflows_count: int = Field(0, description="Anzahl definierter Workflows")
    executions_count: int = Field(0, description="Anzahl laufender Executions")
    portier_connected: bool = Field(False, description="Portier-Verbindung aktiv")
    opena2_connected: bool = Field(False, description="OpenA2-Verbindung aktiv")
    
    
class SafepointRequest(BaseModel):
    """Safepoint für Option-2-Flow Archivierung"""
    model_config = ConfigDict(extra="forbid")
    
    sp_id: str = Field(..., description="Safepoint-ID")
    timestamp: str = Field(..., description="ISO 8601 Timestamp")
    source: str = Field(..., description="Quell-Agent")
    destination: str = Field(..., description="Ziel-Agent") 
    kind: str = Field(..., description="Art (CMD/RESP)")
    payload: Dict[str, Any] = Field(..., description="Nutzdaten")
    workflow_id: Optional[str] = Field(None, description="Zugehörige Workflow-ID")
    step_name: Optional[str] = Field(None, description="Zugehöriger Step-Name")


# ==================== Storage & State Management ====================

# In-Memory Storage (Produktiv: Redis/PostgreSQL)
workflows_registry: Dict[str, WorkflowDefinition] = {}
executions_registry: Dict[str, WorkflowStatus] = {}

# Agent-Mapping für PORTIER 3.0 Integration
AGENT_PORT_MAPPING = {
    "opena1": 12344, "opena2": 12345, "kordp": 12346, "opena3": 12347,
    "opena4": 12348, "opena5": 12351, "opena6": 12352, "opena7": 12353,
    "opena8": 12354, "opena9": 12355, "opena10": 12356, "opena11": 12357,
    "opena12": 12358, "opena13": 12359, "opena14": 12360, "opena15": 12361,
    "opena16": 12362, "opena17": 12363, "opena18": 12364, "opena19": 12365,
    "opena20": 12349
}

# Workflow-Statistiken
workflow_stats = {
    "total_executions": 0,
    "successful_executions": 0,
    "failed_executions": 0,
    "total_steps": 0,
    "last_execution": None
}


# ==================== Security ====================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verifiziert Bearer Token"""
    if not BEARER_TOKEN:
        # DEV-Mode ohne Token
        return "dev-mode"
    
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token"
        )
    return credentials.credentials


# ==================== Workflow Engine (Simplified) ====================

# ==================== Portier Integration Functions ====================

async def check_portier_connection() -> bool:
    """Prüft Verbindung zu Portier (opena1)"""
    try:
        response = await http_client.get(f"{PORTIER_URL}/health")
        return response.status_code == 200
    except Exception:
        return False


async def check_opena2_connection() -> bool:
    """Prüft Verbindung zu OpenA2 (Archivator)"""
    try:
        response = await http_client.get(f"{OPENA2_URL}/health")
        return response.status_code == 200
    except Exception:
        return False


async def send_safepoint(safepoint: SafepointRequest) -> bool:
    """Sendet Safepoint an OpenA2 für Archivierung"""
    try:
        response = await http_client.post(
            f"{OPENA2_URL}/store/archivp",
            json=safepoint.model_dump(),
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"} if BEARER_TOKEN else {}
        )
        return response.status_code in [200, 201]
    except Exception:
        return False


async def call_agent_via_kordp(agent: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ruft Agent via kordp Gateway auf (Option-2-Flow konform).
    """
    if agent not in AGENT_PORT_MAPPING:
        raise ValueError(f"Unknown agent: {agent}")
    
    try:
        # kordp Dispatch Request
        dispatch_payload = {
            "service_target": agent,
            "action": action,
            "params": params
        }
        
        response = await http_client.post(
            f"{KORDP_URL}/dispatch/{agent}",
            json=dispatch_payload,
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"} if BEARER_TOKEN else {},
            timeout=30.0
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "details": response.text}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


async def execute_step(step: StepDefinition, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Führt einzelnen Workflow-Step aus mit PORTIER 3.0 Integration.
    """
    step_start = datetime.now(timezone.utc)
    
    # CMD Safepoint erstellen
    cmd_safepoint = SafepointRequest(
        sp_id=f"SP{int(time.time() * 1000)}_workflowp→{step.agent or 'internal'}_CMD",
        timestamp=step_start.isoformat(),
        source="workflowp",
        destination=step.agent or "internal",
        kind="CMD",
        payload={
            "workflow_id": workflow_id,
            "step_name": step.name,
            "action": step.action,
            "params": step.params
        },
        workflow_id=workflow_id,
        step_name=step.name
    )
    
    # Safepoint archivieren
    await send_safepoint(cmd_safepoint)
    
    try:
        if step.action == "call_agent" and step.agent:
            # Agent via kordp aufrufen
            result = await call_agent_via_kordp(step.agent, "invoke", step.params)
        elif step.action == "transform_data":
            # Daten-Transformation
            result = {"success": True, "data": {"transformed": step.params}}
        elif step.action == "condition":
            # Conditional Logic
            condition_result = step.params.get("value", True)
            result = {"success": True, "data": {"condition_met": condition_result}}
        else:
            # Fallback
            result = {"success": True, "data": {"message": f"Step {step.name} executed"}}
        
        step_end = datetime.now(timezone.utc)
        
        # RESP Safepoint erstellen
        resp_safepoint = SafepointRequest(
            sp_id=f"SP{int(time.time() * 1000)}_{step.agent or 'internal'}→workflowp_RESP",
            timestamp=step_end.isoformat(),
            source=step.agent or "internal",
            destination="workflowp",
            kind="RESP",
            payload={
                "workflow_id": workflow_id,
                "step_name": step.name,
                "success": result.get("success", False),
                "result": result,
                "duration_ms": int((step_end - step_start).total_seconds() * 1000)
            },
            workflow_id=workflow_id,
            step_name=step.name
        )
        
        # Safepoint archivieren
        await send_safepoint(resp_safepoint)
        
        return result
        
    except Exception as e:
        # Error Safepoint
        error_safepoint = SafepointRequest(
            sp_id=f"SP{int(time.time() * 1000)}_workflowp→error_RESP",
            timestamp=datetime.now(timezone.utc).isoformat(),
            source="workflowp",
            destination="error",
            kind="RESP",
            payload={
                "workflow_id": workflow_id,
                "step_name": step.name,
                "success": False,
                "error": str(e)
            },
            workflow_id=workflow_id,
            step_name=step.name
        )
        
        await send_safepoint(error_safepoint)
        return {"success": False, "error": str(e)}


async def execute_workflow_async(workflow: WorkflowDefinition, inputs: Dict[str, Any]) -> WorkflowStatus:
    """
    Führt Workflow asynchron mit PORTIER 3.0 Integration aus.
    """
    workflow_id = f"wf_{int(time.time() * 1000)}"
    started_at = datetime.now(timezone.utc).isoformat()
    
    status_obj = WorkflowStatus(
        workflow_id=workflow_id,
        workflow_name=workflow.name,
        state=WorkflowState.RUNNING,
        started_at=started_at,
        outputs={}
    )
    
    executions_registry[workflow_id] = status_obj
    workflow_stats["total_executions"] += 1
    workflow_stats["last_execution"] = started_at
    
    try:
        # Steps ausführen
        step_outputs = {}
        context = inputs.copy()
        
        for step in workflow.steps:
            status_obj.current_step = step.name
            workflow_stats["total_steps"] += 1
            
            # Step ausführen
            step_result = await execute_step(step, workflow_id, context)
            step_outputs[step.name] = step_result
            
            # Fehlerbehandlung
            if not step_result.get("success", False):
                if step.on_failure == "stop":
                    raise Exception(f"Step {step.name} failed: {step_result.get('error')}")
                elif step.on_failure == "continue":
                    continue
                elif step.on_failure == "retry" and step.retry_count > 0:
                    # Retry-Logic (vereinfacht)
                    for retry in range(step.retry_count):
                        await asyncio.sleep(1)
                        retry_result = await execute_step(step, workflow_id, context)
                        if retry_result.get("success", False):
                            step_outputs[step.name] = retry_result
                            break
            
            # Context für nächste Steps aktualisieren
            if step_result.get("success", False):
                context[f"step_{step.name}_output"] = step_result.get("data", {})
        
        # Workflow erfolgreich
        status_obj.state = WorkflowState.COMPLETED
        status_obj.completed_at = datetime.now(timezone.utc).isoformat()
        status_obj.outputs = step_outputs
        status_obj.current_step = None
        workflow_stats["successful_executions"] += 1
        
    except Exception as e:
        # Workflow fehlgeschlagen
        status_obj.state = WorkflowState.FAILED
        status_obj.completed_at = datetime.now(timezone.utc).isoformat()
        status_obj.error = str(e)
        status_obj.current_step = None
        workflow_stats["failed_executions"] += 1
    
    executions_registry[workflow_id] = status_obj
    return status_obj


# ==================== API Endpoints ====================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health-Check Endpoint (öffentlich) - PORTIER 3.0 Standard"""
    portier_connected = await check_portier_connection()
    opena2_connected = await check_opena2_connection()
    
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        port=PORT,
        program_target=PROGRAM_TARGET,
        uptime_seconds=time.time() - start_time,
        version=VERSION,
        workflows_count=len(workflows_registry),
        executions_count=len([e for e in executions_registry.values() if e.state == WorkflowState.RUNNING]),
        portier_connected=portier_connected,
        opena2_connected=opena2_connected
    )


@app.post("/invoke", tags=["Option-2-Flow"])
async def invoke(
    request: InvokeRequest,
    token: str = Depends(verify_token)
):
    """
    Generic Invoke Endpoint für Option-2-Flow Kompatibilität.
    Dispatcht Actions an interne Handler.
    """
    if request.action == "execute_workflow":
        # Workflow ausführen
        workflow_name = request.params.get("workflow_name")
        inputs = request.params.get("inputs", {})
        
        if not workflow_name or workflow_name not in workflows_registry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{workflow_name}' nicht gefunden"
            )
        
        workflow = workflows_registry[workflow_name]
        status_obj = execute_workflow_sync(workflow, inputs)
        
        return {
            "status": "success",
            "action": request.action,
            "result": status_obj.model_dump()
        }
    
    elif request.action == "get_status":
        # Status abfragen
        workflow_id = request.params.get("workflow_id")
        
        if not workflow_id or workflow_id not in executions_registry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow-ID '{workflow_id}' nicht gefunden"
            )
        
        status_obj = executions_registry[workflow_id]
        
        return {
            "status": "success",
            "action": request.action,
            "result": status_obj.model_dump()
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unbekannte Action: {request.action}"
        )


@app.post("/workflows/create", tags=["Workflows"])
async def create_workflow(
    workflow: WorkflowDefinition,
    token: str = Depends(verify_token)
):
    """Erstellt eine neue Workflow-Definition"""
    if workflow.name in workflows_registry:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workflow '{workflow.name}' existiert bereits"
        )
    
    workflows_registry[workflow.name] = workflow
    
    return {
        "status": "success",
        "message": f"Workflow '{workflow.name}' erstellt",
        "workflow": workflow.model_dump()
    }


@app.get("/workflows/list", tags=["Workflows"])
async def list_workflows(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """Listet alle definierten Workflows auf"""
    return {
        "status": "success",
        "count": len(workflows_registry),
        "workflows": [
            {
                "name": workflow.name,
                "description": workflow.description,
                "steps_count": len(workflow.steps),
                "timeout": workflow.timeout
            }
            for workflow in workflows_registry.values()
        ]
    }


@app.post("/workflows/execute", tags=["Workflows"])
async def execute_workflow_endpoint(
    request: ExecuteRequest,
    token: str = Depends(verify_token)
):
    """Führt einen Workflow aus mit PORTIER 3.0 Integration"""
    if request.workflow_name not in workflows_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{request.workflow_name}' nicht gefunden"
        )
    
    workflow = workflows_registry[request.workflow_name]
    
    # Workflow-Start Safepoint
    start_safepoint = SafepointRequest(
        sp_id=f"SP{int(time.time() * 1000)}_workflowp→execution_CMD",
        timestamp=datetime.now(timezone.utc).isoformat(),
        source="workflowp",
        destination="execution",
        kind="CMD",
        payload={
            "workflow_name": request.workflow_name,
            "inputs": request.inputs,
            "mode": request.mode
        }
    )
    await send_safepoint(start_safepoint)
    
    if request.mode == "sync":
        status_obj = await execute_workflow_async(workflow, request.inputs)
        return {
            "status": "success",
            "execution": status_obj.model_dump()
        }
    else:
        # Async-Mode mit Background Task
        workflow_id = f"wf_{int(time.time() * 1000)}"
        
        # Status-Objekt für Async erstellen
        status_obj = WorkflowStatus(
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            state=WorkflowState.PENDING,
            started_at=datetime.now(timezone.utc).isoformat(),
            outputs={}
        )
        executions_registry[workflow_id] = status_obj
        
        # Background Task starten
        asyncio.create_task(execute_workflow_async(workflow, request.inputs))
        
        return {
            "status": "success",
            "message": "Workflow gestartet (asynchron)",
            "workflow_id": workflow_id,
            "execution": status_obj.model_dump()
        }


@app.get("/workflows/status/{workflow_id}", tags=["Workflows"])
async def get_workflow_status(
    workflow_id: str,
    token: str = Depends(verify_token)
):
    """Fragt Status eines Workflows ab"""
    if workflow_id not in executions_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow-ID '{workflow_id}' nicht gefunden"
        )
    
    status_obj = executions_registry[workflow_id]
    return {
        "status": "success",
        "execution": status_obj.model_dump()
    }


@app.get("/workflows/executions", tags=["Workflows"])
async def list_executions(token: str = Depends(verify_token)):
    """Listet alle Workflow-Ausführungen auf"""
    return {
        "status": "success",
        "count": len(executions_registry),
        "statistics": workflow_stats,
        "executions": [exec_obj.model_dump() for exec_obj in executions_registry.values()]
    }


@app.post("/workflows/cancel/{workflow_id}", tags=["Workflows"])
async def cancel_workflow(
    workflow_id: str,
    token: str = Depends(verify_token)
):
    """Bricht laufenden Workflow ab"""
    if workflow_id not in executions_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow-ID '{workflow_id}' nicht gefunden"
        )
    
    status_obj = executions_registry[workflow_id]
    
    if status_obj.state not in [WorkflowState.RUNNING, WorkflowState.PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow kann nicht abgebrochen werden (Status: {status_obj.state})"
        )
    
    # Status auf cancelled setzen
    status_obj.state = WorkflowState.CANCELLED
    status_obj.completed_at = datetime.now(timezone.utc).isoformat()
    status_obj.current_step = None
    
    # Cancel Safepoint
    cancel_safepoint = SafepointRequest(
        sp_id=f"SP{int(time.time() * 1000)}_workflowp→cancel_CMD",
        timestamp=datetime.now(timezone.utc).isoformat(),
        source="workflowp",
        destination="cancel",
        kind="CMD",
        payload={
            "workflow_id": workflow_id,
            "action": "cancel",
            "reason": "User requested cancellation"
        },
        workflow_id=workflow_id
    )
    await send_safepoint(cancel_safepoint)
    
    return {
        "status": "success",
        "message": f"Workflow {workflow_id} abgebrochen",
        "execution": status_obj.model_dump()
    }


@app.get("/statistics", tags=["Monitoring"])
async def get_statistics(token: str = Depends(verify_token)):
    """Workflow-Engine Statistiken"""
    return {
        "status": "success",
        "statistics": workflow_stats,
        "workflows": {
            "total_defined": len(workflows_registry),
            "workflow_names": list(workflows_registry.keys())
        },
        "executions": {
            "total": len(executions_registry),
            "running": len([e for e in executions_registry.values() if e.state == WorkflowState.RUNNING]),
            "completed": len([e for e in executions_registry.values() if e.state == WorkflowState.COMPLETED]),
            "failed": len([e for e in executions_registry.values() if e.state == WorkflowState.FAILED]),
            "cancelled": len([e for e in executions_registry.values() if e.state == WorkflowState.CANCELLED])
        }
    }


# ==================== Startup/Shutdown ====================

async def register_with_portier():
    """Registriert Service bei Portier (opena1) als Tool"""
    try:
        registration_payload = {
            "service_name": SERVICE_NAME,
            "endpoint": f"http://127.0.0.1:{PORT}",
            "program_target": PROGRAM_TARGET,
            "capabilities": ["workflow_execution", "multi_agent_orchestration"],
            "health_endpoint": f"http://127.0.0.1:{PORT}/health"
        }
        
        response = await http_client.post(
            f"{PORTIER_URL}/route/update",
            json=registration_payload,
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"} if BEARER_TOKEN else {},
            timeout=10.0
        )
        
        if response.status_code == 200:
            print(f"✅ Service bei Portier registriert: {PROGRAM_TARGET}")
            return True
        else:
            print(f"⚠️ Portier-Registrierung fehlgeschlagen: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Portier-Registrierung Fehler: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Initialisierung beim Start mit PORTIER 3.0 Integration"""
    print(f"🚀 {SERVICE_NAME} (Workflow Engine) startet auf Port {PORT}")
    print(f"📊 Program Target: {PROGRAM_TARGET}")
    print(f"🔐 Bearer Token: {'✅ Aktiviert' if BEARER_TOKEN else '⚠️ Nicht gesetzt (DEV-Mode)'}")
    print(f"🔗 Portier URL: {PORTIER_URL}")
    print(f"📦 OpenA2 URL: {OPENA2_URL}")
    print(f"🚪 kordp URL: {KORDP_URL}")
    
    # Verbindungen prüfen
    portier_ok = await check_portier_connection()
    opena2_ok = await check_opena2_connection()
    
    print(f"📡 Portier Connection: {'✅' if portier_ok else '❌'}")
    print(f"📦 OpenA2 Connection: {'✅' if opena2_ok else '❌'}")
    
    # Bei Portier registrieren
    if portier_ok:
        await register_with_portier()
    
    # Demo-Workflows erstellen
    demo_workflows = [
        WorkflowDefinition(
            name="demo_multi_agent_chain",
            description="Demo: OpenWebUI → Browser → Email Chain (Multi-Agent)",
            steps=[
                StepDefinition(
                    name="query_openwebui",
                    action="call_agent",
                    agent="opena3",
                    params={"action": "invoke", "query": "Aktuelle Tech-Nachrichten"},
                    timeout=30
                ),
                StepDefinition(
                    name="analyze_browser",
                    action="call_agent", 
                    agent="opena6",
                    params={"action": "browse", "url": "https://techcrunch.com"},
                    timeout=45,
                    depends_on=["query_openwebui"]
                ),
                StepDefinition(
                    name="send_summary_email",
                    action="call_agent",
                    agent="opena7", 
                    params={"action": "send", "to": "admin@example.com", "subject": "Daily Tech Summary"},
                    timeout=20,
                    depends_on=["analyze_browser"]
                )
            ],
            timeout=120
        ),
        
        WorkflowDefinition(
            name="social_media_automation",
            description="Demo: Content Creation → Social Media Publishing",
            steps=[
                StepDefinition(
                    name="generate_content",
                    action="call_agent",
                    agent="opena3",
                    params={"action": "invoke", "prompt": "Generiere Social Media Post über KI"},
                    timeout=30
                ),
                StepDefinition(
                    name="post_to_social",
                    action="call_agent",
                    agent="opena12",
                    params={"action": "post", "platform": "twitter"},
                    timeout=20,
                    depends_on=["generate_content"]
                )
            ],
            timeout=60
        ),
        
        WorkflowDefinition(
            name="crm_data_sync",
            description="Demo: CRM Data Synchronization Workflow",
            steps=[
                StepDefinition(
                    name="fetch_crm_data",
                    action="call_agent",
                    agent="opena18",
                    params={"action": "export", "format": "json"},
                    timeout=30
                ),
                StepDefinition(
                    name="transform_data",
                    action="transform_data",
                    params={"format": "normalized", "filters": ["active_customers"]},
                    timeout=15
                ),
                StepDefinition(
                    name="update_calendar",
                    action="call_agent",
                    agent="opena14",
                    params={"action": "sync", "source": "crm_export"},
                    timeout=25,
                    depends_on=["transform_data"]
                )
            ],
            timeout=90
        ),
        
        # ==================== HTML SYSTEMS MANAGEMENT WORKFLOWS ====================
        
        WorkflowDefinition(
            name="html_systems_discovery",
            description="🔍 HTML Systems Discovery - Entdeckung aller online HTML-Systeme",
            steps=[
                StepDefinition(
                    name="scan_network_domains",
                    action="call_agent",
                    agent="opena6",
                    params={
                        "action": "domain_scan",
                        "target_domains": ["localhost", "127.0.0.1", "*.local", "*.dev"],
                        "ports": [80, 443, 3000, 8080, 8000, 8001, 5000],
                        "scan_type": "html_detection"
                    },
                    timeout=45
                ),
                StepDefinition(
                    name="identify_html_frameworks",
                    action="call_agent",
                    agent="opena15",
                    params={
                        "action": "analyze_html_structure",
                        "detection_methods": ["framework_fingerprinting", "meta_analysis", "asset_detection"]
                    },
                    timeout=30,
                    depends_on=["scan_network_domains"]
                ),
                StepDefinition(
                    name="catalog_discovered_systems",
                    action="call_agent",
                    agent="opena18",
                    params={
                        "action": "store_html_inventory",
                        "storage_format": "structured_json",
                        "include_metadata": True
                    },
                    timeout=20,
                    depends_on=["identify_html_frameworks"]
                )
            ],
            timeout=120
        ),
        
        WorkflowDefinition(
            name="html_quality_assessment",
            description="📊 HTML Quality Assessment - Bewertung aller HTML-Systeme",
            steps=[
                StepDefinition(
                    name="performance_audit",
                    action="call_agent",
                    agent="opena6",
                    params={
                        "action": "lighthouse_audit",
                        "metrics": ["performance", "accessibility", "best_practices", "seo"],
                        "devices": ["mobile", "desktop"],
                        "generate_reports": True
                    },
                    timeout=60
                ),
                StepDefinition(
                    name="html_validation",
                    action="call_agent",
                    agent="opena15",
                    params={
                        "action": "w3c_validation",
                        "validation_types": ["html5", "css3", "wcag"],
                        "error_reporting": True
                    },
                    timeout=30,
                    depends_on=["performance_audit"]
                ),
                StepDefinition(
                    name="security_scan",
                    action="call_agent",
                    agent="opena6",
                    params={
                        "action": "security_audit",
                        "scan_types": ["xss", "csrf", "sql_injection", "headers"],
                        "vulnerability_assessment": True
                    },
                    timeout=45,
                    depends_on=["html_validation"]
                ),
                StepDefinition(
                    name="generate_quality_report",
                    action="call_agent",
                    agent="opena17",
                    params={
                        "action": "create_assessment_report",
                        "template": "html_quality_dashboard",
                        "include_charts": True,
                        "output_format": "interactive_html"
                    },
                    timeout=25,
                    depends_on=["security_scan"]
                )
            ],
            timeout=180
        ),
        
        WorkflowDefinition(
            name="html_system_optimization",
            description="⚡ HTML System Optimization - Automatische Verbesserung",
            steps=[
                StepDefinition(
                    name="analyze_optimization_opportunities",
                    action="call_agent",
                    agent="opena15",
                    params={
                        "action": "optimization_analysis",
                        "focus_areas": ["load_time", "bundle_size", "image_optimization", "css_minification"],
                        "priority_scoring": True
                    },
                    timeout=30
                ),
                StepDefinition(
                    name="implement_performance_improvements",
                    action="call_agent",
                    agent="opena17",
                    params={
                        "action": "apply_optimizations",
                        "optimization_types": ["css_minify", "js_minify", "image_compress", "lazy_loading"],
                        "backup_originals": True,
                        "rollback_enabled": True
                    },
                    timeout=45,
                    depends_on=["analyze_optimization_opportunities"]
                ),
                StepDefinition(
                    name="update_html_structure",
                    action="call_agent",
                    agent="opena15",
                    params={
                        "action": "modernize_html",
                        "improvements": ["semantic_html5", "aria_labels", "meta_optimization", "structured_data"],
                        "validate_changes": True
                    },
                    timeout=40,
                    depends_on=["implement_performance_improvements"]
                ),
                StepDefinition(
                    name="verify_improvements",
                    action="call_agent",
                    agent="opena6",
                    params={
                        "action": "post_optimization_test",
                        "test_types": ["performance_comparison", "functionality_test", "cross_browser_test"],
                        "baseline_comparison": True
                    },
                    timeout=35,
                    depends_on=["update_html_structure"]
                )
            ],
            timeout=180
        ),
        
        WorkflowDefinition(
            name="html_deployment_pipeline",
            description="🚀 HTML Deployment Pipeline - Erstellung und Deployment neuer HTML-Systeme",
            steps=[
                StepDefinition(
                    name="generate_html_templates",
                    action="call_agent",
                    agent="opena15",
                    params={
                        "action": "create_html_templates",
                        "template_types": ["landing_page", "dashboard", "documentation", "portfolio"],
                        "frameworks": ["vanilla", "bootstrap", "tailwind", "material"],
                        "responsive_design": True
                    },
                    timeout=40
                ),
                StepDefinition(
                    name="create_homepage_structure",
                    action="call_agent",
                    agent="opena17",
                    params={
                        "action": "build_homepage",
                        "structure_type": "modern_spa",
                        "include_components": ["header", "hero", "features", "contact", "footer"],
                        "seo_optimization": True
                    },
                    timeout=35,
                    depends_on=["generate_html_templates"]
                ),
                StepDefinition(
                    name="integrate_dynamic_content",
                    action="call_agent",
                    agent="opena18",
                    params={
                        "action": "connect_data_sources",
                        "data_types": ["cms_content", "user_data", "analytics"],
                        "api_integration": True
                    },
                    timeout=30,
                    depends_on=["create_homepage_structure"]
                ),
                StepDefinition(
                    name="automated_testing",
                    action="call_agent",
                    agent="opena6",
                    params={
                        "action": "comprehensive_testing",
                        "test_suites": ["unit", "integration", "e2e", "accessibility"],
                        "browsers": ["chrome", "firefox", "safari", "edge"],
                        "generate_reports": True
                    },
                    timeout=50,
                    depends_on=["integrate_dynamic_content"]
                ),
                StepDefinition(
                    name="deploy_to_production",
                    action="call_agent",
                    agent="opena17",
                    params={
                        "action": "production_deployment",
                        "deployment_type": "blue_green",
                        "monitoring_enabled": True,
                        "rollback_strategy": "automated"
                    },
                    timeout=25,
                    depends_on=["automated_testing"]
                )
            ],
            timeout=210
        ),
        
        WorkflowDefinition(
            name="html_monitoring_maintenance",
            description="🔧 HTML Monitoring & Maintenance - Kontinuierliche Überwachung",
            steps=[
                StepDefinition(
                    name="setup_monitoring",
                    action="call_agent",
                    agent="opena20",
                    params={
                        "action": "configure_html_monitoring",
                        "monitoring_types": ["uptime", "performance", "errors", "user_experience"],
                        "alert_thresholds": {
                            "response_time": 3000,
                            "error_rate": 0.01,
                            "uptime": 0.995
                        }
                    },
                    timeout=30
                ),
                StepDefinition(
                    name="health_check_automation",
                    action="call_agent",
                    agent="opena6",
                    params={
                        "action": "automated_health_checks",
                        "check_frequency": "every_5_minutes",
                        "check_types": ["availability", "response_time", "content_integrity"],
                        "alerting_enabled": True
                    },
                    timeout=25,
                    depends_on=["setup_monitoring"]
                ),
                StepDefinition(
                    name="periodic_maintenance",
                    action="call_agent",
                    agent="opena15",
                    params={
                        "action": "maintenance_tasks",
                        "tasks": ["cache_cleanup", "dependency_updates", "security_patches", "content_refresh"],
                        "schedule": "weekly",
                        "maintenance_window": "03:00-05:00"
                    },
                    timeout=35,
                    depends_on=["health_check_automation"]
                ),
                StepDefinition(
                    name="generate_maintenance_reports",
                    action="call_agent",
                    agent="opena20",
                    params={
                        "action": "create_maintenance_dashboard",
                        "report_types": ["system_health", "performance_trends", "maintenance_history"],
                        "delivery_schedule": "weekly",
                        "stakeholder_notifications": True
                    },
                    timeout=20,
                    depends_on=["periodic_maintenance"]
                )
            ],
            timeout=130
        ),
        
        WorkflowDefinition(
            name="html_integration_orchestration",
            description="🔗 HTML Integration Orchestration - Vollständige System-Integration",
            steps=[
                StepDefinition(
                    name="discover_integration_points",
                    action="call_agent",
                    agent="opena18",
                    params={
                        "action": "map_integration_architecture",
                        "integration_types": ["api_endpoints", "data_flows", "user_journeys", "cross_system_deps"],
                        "documentation_level": "comprehensive"
                    },
                    timeout=40
                ),
                StepDefinition(
                    name="implement_api_connections",
                    action="call_agent",
                    agent="opena15",
                    params={
                        "action": "create_api_integrations",
                        "integration_patterns": ["rest_apis", "graphql", "websockets", "sse"],
                        "authentication": "bearer_token",
                        "error_handling": "comprehensive"
                    },
                    timeout=50,
                    depends_on=["discover_integration_points"]
                ),
                StepDefinition(
                    name="setup_data_synchronization",
                    action="call_agent",
                    agent="opena18",
                    params={
                        "action": "configure_data_sync",
                        "sync_patterns": ["real_time", "batch", "event_driven"],
                        "conflict_resolution": "last_write_wins",
                        "backup_strategy": "incremental"
                    },
                    timeout=35,
                    depends_on=["implement_api_connections"]
                ),
                StepDefinition(
                    name="create_unified_dashboard",
                    action="call_agent",
                    agent="opena20",
                    params={
                        "action": "build_integration_dashboard",
                        "dashboard_features": ["system_overview", "data_flows", "performance_metrics", "alerts"],
                        "real_time_updates": True,
                        "user_personalization": True
                    },
                    timeout=45,
                    depends_on=["setup_data_synchronization"]
                ),
                StepDefinition(
                    name="validate_end_to_end_flows",
                    action="call_agent",
                    agent="opena6",
                    params={
                        "action": "e2e_integration_testing",
                        "test_scenarios": ["user_workflows", "data_consistency", "error_propagation", "performance_under_load"],
                        "automation_level": "full",
                        "reporting": "detailed"
                    },
                    timeout=60,
                    depends_on=["create_unified_dashboard"]
                )
            ],
            timeout=260
        )
    ]
    
    # Workflows registrieren
    for workflow in demo_workflows:
        workflows_registry[workflow.name] = workflow
        print(f"✅ Demo-Workflow '{workflow.name}' registriert ({len(workflow.steps)} Steps)")
    
    print(f"🎯 Workflow Engine bereit - {len(workflows_registry)} Workflows verfügbar")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup beim Shutdown"""
    print(f"🛑 {SERVICE_NAME} wird gestoppt")
    
    # Laufende Workflows abbrechen
    running_count = len([e for e in executions_registry.values() if e.state == WorkflowState.RUNNING])
    if running_count > 0:
        print(f"⚠️ {running_count} laufende Workflows werden abgebrochen")
        
        for execution in executions_registry.values():
            if execution.state == WorkflowState.RUNNING:
                execution.state = WorkflowState.CANCELLED
                execution.completed_at = datetime.now(timezone.utc).isoformat()
    
    # HTTP Client schließen
    await http_client.aclose()
    print(f"✅ Cleanup abgeschlossen")


# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
