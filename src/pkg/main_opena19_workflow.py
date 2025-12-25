"""
opena19_Workflow: Advanced Workflow Agent
Workflow orchestration, task scheduling, conditional logic, agent chaining
GitHub Pattern: agent_lightning (workflow_engine_service.py) + AI-Powered-Tool-Discovery-Agent
"""

import json
import logging
import os
import secrets
import sys
import urllib.request
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(title="opena19_Workflow", version="1.0.0", description="Workflow Agent - Orchestration & Scheduling")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12367
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_workflows: dict[str, dict] = {}
_executions: dict[str, dict] = {}
_triggers: dict[str, dict] = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class WorkflowStep(BaseModel):
    """Single workflow step"""

    step_id: str
    action: str  # "call_agent", "send_email", "create_record", "condition"
    target: str | None = None  # agent name or service
    payload: dict[str, Any] = {}
    condition: str | None = None  # For conditional steps


class WorkflowRequest(BaseModel):
    """Create workflow"""

    name: str
    description: str
    steps: list[WorkflowStep]
    enabled: bool = True


class WorkflowExecuteRequest(BaseModel):
    """Execute workflow with context"""

    context: dict[str, Any] = {}  # Input data


class TriggerRequest(BaseModel):
    """Set trigger for workflow"""

    event_type: str  # "schedule", "webhook", "agent_action"
    condition: str  # cron expression or condition
    workflow_id: str


class WorkflowUpdateRequest(BaseModel):
    """Update workflow execution status"""

    status: str  # "running", "paused", "completed", "failed"
    notes: str | None = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: str | None):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict):
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena19_workflow",
            "dst": "opena2",
            "kind": "WORKFLOW_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"},
        }

        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_workflow_id() -> str:
    """Generate unique workflow ID"""
    return f"WFW_{secrets.token_hex(6).upper()}"


def _generate_execution_id() -> str:
    """Generate unique execution ID"""
    return f"EXE_{secrets.token_hex(6).upper()}"


def _generate_trigger_id() -> str:
    """Generate unique trigger ID"""
    return f"TRG_{secrets.token_hex(6).upper()}"


async def _execute_step(step: WorkflowStep, context: dict[str, Any]) -> dict[str, Any]:
    """Execute a single workflow step"""
    result = {"step_id": step.step_id, "action": step.action, "status": "completed", "output": {}}

    try:
        if step.action == "call_agent":
            # Simulate agent call
            if step.target == "crm":
                result["output"] = {"agent": "opena16_crm", "data": "customer_created"}
            elif step.target == "analytics":
                result["output"] = {"agent": "opena17_analytics", "data": "report_generated"}
            elif step.target == "dashboard":
                result["output"] = {"agent": "opena18_dashboard", "data": "widget_updated"}
            else:
                result["output"] = {"message": f"Called agent: {step.target}"}

        elif step.action == "send_email":
            result["output"] = {"email_sent": True, "recipient": step.payload.get("to")}

        elif step.action == "create_record":
            result["output"] = {"record_id": secrets.token_hex(6), "type": step.payload.get("type")}

        elif step.action == "condition":
            # Evaluate condition (simplified)
            result["output"] = {"condition_met": True}

        logger.info(f"✅ Step executed: {step.step_id} ({step.action})")

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        logger.error(f"❌ Step failed: {step.step_id} - {e}")

    return result


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena19_Workflow",
        "port": PORT,
        "workflows": len(_workflows),
        "executions": len(_executions),
        "triggers": len(_triggers),
        "ts": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/workflow/create")
async def create_workflow(req: WorkflowRequest, authorization: str = Header(None)):
    """Create new workflow"""
    _validate_token(authorization)

    try:
        workflow_id = _generate_workflow_id()

        # Convert steps to dict format
        steps_data = []
        for step in req.steps:
            steps_data.append(
                {
                    "step_id": step.step_id,
                    "action": step.action,
                    "target": step.target,
                    "payload": step.payload,
                    "condition": step.condition,
                }
            )

        workflow_entry = {
            "id": workflow_id,
            "name": req.name,
            "description": req.description,
            "steps": steps_data,
            "enabled": req.enabled,
            "created_at": datetime.utcnow().isoformat(),
            "execution_count": 0,
            "status": "active",
        }

        _workflows[workflow_id] = workflow_entry

        logger.info(f"⚙️ Workflow created: {workflow_id} ({req.name}) with {len(steps_data)} steps")

        await _archive(
            {
                "op": "WORKFLOW_CREATED",
                "workflow_id": workflow_id,
                "workflow_name": req.name,
                "step_count": len(steps_data),
            }
        )

        return {
            "strict": True,
            "workflow_id": workflow_id,
            "name": req.name,
            "steps": len(steps_data),
            "created": True,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Workflow creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str, authorization: str = Header(None)):
    """Get workflow details"""
    _validate_token(authorization)

    try:
        if workflow_id not in _workflows:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        workflow = _workflows[workflow_id]
        logger.info(f"⚙️ Workflow retrieved: {workflow_id}")

        return {"strict": True, "workflow": workflow, "ts": datetime.utcnow().isoformat() + "Z"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Workflow retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, req: WorkflowExecuteRequest, authorization: str = Header(None)):
    """Execute workflow"""
    _validate_token(authorization)

    try:
        if workflow_id not in _workflows:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        workflow = _workflows[workflow_id]

        if not workflow["enabled"]:
            raise HTTPException(status_code=400, detail="Workflow is disabled")

        execution_id = _generate_execution_id()

        # Execute all steps
        step_results = []
        for step_data in workflow["steps"]:
            step = WorkflowStep(**step_data)
            result = await _execute_step(step, req.context)
            step_results.append(result)

        # Determine execution status
        failed_steps = [s for s in step_results if s["status"] == "failed"]
        execution_status = "failed" if failed_steps else "completed"

        execution_entry = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "status": execution_status,
            "steps_executed": len(step_results),
            "steps_failed": len(failed_steps),
            "step_results": step_results,
            "context": req.context,
        }

        _executions[execution_id] = execution_entry
        workflow["execution_count"] += 1

        logger.info(f"🚀 Workflow executed: {workflow_id} → {execution_id} ({execution_status})")

        await _archive(
            {
                "op": "WORKFLOW_EXECUTED",
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "status": execution_status,
                "steps_count": len(step_results),
                "steps_failed": len(failed_steps),
            }
        )

        return {
            "strict": True,
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": execution_status,
            "steps_executed": len(step_results),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/{workflow_id}/status")
async def workflow_status(workflow_id: str, authorization: str = Header(None)):
    """Get workflow status and execution history"""
    _validate_token(authorization)

    try:
        if workflow_id not in _workflows:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        workflow = _workflows[workflow_id]

        # Get related executions
        related_executions = [e for e in _executions.values() if e["workflow_id"] == workflow_id]

        logger.info(f"📊 Workflow status: {workflow_id}")

        return {
            "strict": True,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "enabled": workflow["enabled"],
            "steps": len(workflow["steps"]),
            "total_executions": len(related_executions),
            "recent_executions": related_executions[-5:],  # Last 5 executions
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Workflow status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trigger/set")
async def set_trigger(req: TriggerRequest, authorization: str = Header(None)):
    """Set trigger for workflow (schedule, webhook, etc.)"""
    _validate_token(authorization)

    try:
        trigger_id = _generate_trigger_id()

        trigger_entry = {
            "id": trigger_id,
            "workflow_id": req.workflow_id,
            "event_type": req.event_type,
            "condition": req.condition,
            "created_at": datetime.utcnow().isoformat(),
            "active": True,
            "executions": 0,
        }

        _triggers[trigger_id] = trigger_entry

        logger.info(f"🔔 Trigger set: {trigger_id} for workflow {req.workflow_id}")

        await _archive(
            {
                "op": "TRIGGER_SET",
                "trigger_id": trigger_id,
                "workflow_id": req.workflow_id,
                "event_type": req.event_type,
            }
        )

        return {
            "strict": True,
            "trigger_id": trigger_id,
            "workflow_id": req.workflow_id,
            "event_type": req.event_type,
            "created": True,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Trigger set failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trigger/list")
async def list_triggers(authorization: str = Header(None)):
    """List all triggers"""
    _validate_token(authorization)

    try:
        logger.info(f"📋 Triggers listed: {len(_triggers)} triggers")

        return {
            "strict": True,
            "triggers": list(_triggers.values()),
            "count": len(_triggers),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Trigger listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow/{workflow_id}/pause")
async def pause_workflow(workflow_id: str, req: WorkflowUpdateRequest, authorization: str = Header(None)):
    """Pause or update workflow status"""
    _validate_token(authorization)

    try:
        if workflow_id not in _workflows:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        workflow = _workflows[workflow_id]
        old_status = workflow["status"]
        workflow["status"] = req.status
        workflow["last_updated"] = datetime.utcnow().isoformat()

        if req.notes:
            workflow["notes"] = req.notes

        logger.info(f"⏸️ Workflow status changed: {workflow_id} from {old_status} to {req.status}")

        await _archive(
            {
                "op": "WORKFLOW_STATUS_CHANGED",
                "workflow_id": workflow_id,
                "old_status": old_status,
                "new_status": req.status,
                "notes": req.notes,
            }
        )

        return {
            "strict": True,
            "workflow_id": workflow_id,
            "status": req.status,
            "updated": True,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Workflow update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)

    return {
        "service": "opena19_Workflow",
        "version": "1.0.0",
        "port": PORT,
        "workflows": len(_workflows),
        "executions": len(_executions),
        "triggers": len(_triggers),
        "endpoints": 7,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting opena19_Workflow on port {PORT}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
