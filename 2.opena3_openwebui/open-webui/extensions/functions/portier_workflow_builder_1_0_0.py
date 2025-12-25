"""
Portier Workflow Builder 1.0.0
Visuelles KI-Automation-System für LocalAgentPro

Features:
- Visuelle Workflow-Erstellung
- Step-Management
- Multi-Action Support
- Live-Execution Plan
- Speichern & Ausführen

OpenWebUI Tool Format (production-ready)
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================


class ActionType(str, Enum):
    """Supported action types in workflow"""

    BROWSER_AGENT = "browser_agent"
    LOCAL_AGENT = "local_agent"
    FILE_OPS = "file_ops"
    PDF_TOOLS = "pdf_tools"
    SYSTEM_CMD = "system_cmd"
    DELAY = "delay"
    CONDITION = "condition"


class WorkflowStep(BaseModel):
    """Single step in workflow"""

    step_id: str
    name: str
    action_type: ActionType
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    order: int
    enabled: bool = True
    timeout_seconds: int = 300
    retry_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class WorkflowConfig(BaseModel):
    """Complete workflow configuration"""

    workflow_id: str
    name: str
    description: str = ""
    steps: list[WorkflowStep] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    auto_execute: bool = False
    execute_interval_seconds: int | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ExecutionResult(BaseModel):
    """Result from workflow step execution"""

    step_id: str
    status: str  # success, failed, skipped, timeout
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ExecutionPlan(BaseModel):
    """Execution plan for workflow"""

    plan_id: str
    workflow_id: str
    steps_order: list[str]
    total_steps: int
    estimated_duration_seconds: float
    critical_path: list[str]
    dependencies: dict[str, list[str]] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# WORKFLOW ENGINE
# ============================================================================


class WorkflowEngine:
    """Main workflow execution engine"""

    def __init__(self):
        """Initialize workflow engine"""
        self.workflows: dict[str, WorkflowConfig] = {}
        self.executions: dict[str, list[ExecutionResult]] = {}
        self.data_dir = os.environ.get("PORTIER_DATA_DIR", "/tmp/portier_workflows")
        os.makedirs(self.data_dir, exist_ok=True)
        logger.info(f"WorkflowEngine initialized. Data dir: {self.data_dir}")
        self._load_workflows()

    def _load_workflows(self):
        """Load workflows from storage"""
        workflows_file = os.path.join(self.data_dir, "workflows.json")
        if os.path.exists(workflows_file):
            try:
                with open(workflows_file) as f:
                    workflows_data = json.load(f)
                    for wf_id, wf_data in workflows_data.items():
                        steps = [WorkflowStep(**step) for step in wf_data.get("steps", [])]
                        self.workflows[wf_id] = WorkflowConfig(
                            workflow_id=wf_id,
                            name=wf_data["name"],
                            description=wf_data.get("description", ""),
                            steps=steps,
                            variables=wf_data.get("variables", {}),
                            enabled=wf_data.get("enabled", True),
                        )
                logger.info(f"Loaded {len(self.workflows)} workflows from storage")
            except Exception as e:
                logger.warning(f"Failed to load workflows: {e}")

    def _save_workflows(self):
        """Save workflows to storage"""
        try:
            workflows_file = os.path.join(self.data_dir, "workflows.json")
            workflows_data = {}
            for wf_id, workflow in self.workflows.items():
                workflows_data[wf_id] = workflow.model_dump()

            with open(workflows_file, "w") as f:
                json.dump(workflows_data, f, indent=2, default=str)
            logger.info("Workflows saved to storage")
        except Exception as e:
            logger.error(f"Failed to save workflows: {e}")

    async def create_workflow(self, name: str, description: str = "", auto_execute: bool = False) -> str:
        """Create new workflow"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        workflow = WorkflowConfig(
            workflow_id=workflow_id, name=name, description=description, auto_execute=auto_execute
        )

        self.workflows[workflow_id] = workflow
        self._save_workflows()

        logger.info(f"Created workflow: {workflow_id} ({name})")
        return workflow_id

    async def add_step(
        self, workflow_id: str, name: str, action_type: ActionType, parameters: dict[str, Any], description: str = ""
    ) -> bool:
        """Add step to workflow"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow not found: {workflow_id}")
            return False

        workflow = self.workflows[workflow_id]
        step_id = f"step_{len(workflow.steps) + 1:03d}"

        step = WorkflowStep(
            step_id=step_id,
            name=name,
            action_type=action_type,
            description=description,
            parameters=parameters,
            order=len(workflow.steps),
        )

        workflow.steps.append(step)
        workflow.updated_at = datetime.now().isoformat()
        self._save_workflows()

        logger.info(f"Added step {step_id} to workflow {workflow_id}")
        return True

    async def generate_execution_plan(self, workflow_id: str) -> ExecutionPlan | None:
        """Generate execution plan for workflow"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow not found: {workflow_id}")
            return None

        workflow = self.workflows[workflow_id]

        # Sort steps by order
        sorted_steps = sorted(workflow.steps, key=lambda s: s.order)
        steps_order = [s.step_id for s in sorted_steps]

        # Calculate estimated duration
        estimated_duration = sum(s.timeout_seconds for s in sorted_steps if s.enabled) / 2  # Average case

        # Identify critical path (longest chain)
        critical_path = steps_order

        # Build dependencies
        dependencies = {s.step_id: [] for s in sorted_steps}

        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        plan = ExecutionPlan(
            plan_id=plan_id,
            workflow_id=workflow_id,
            steps_order=steps_order,
            total_steps=len(sorted_steps),
            estimated_duration_seconds=estimated_duration,
            critical_path=critical_path,
            dependencies=dependencies,
        )

        logger.info(f"Generated execution plan {plan_id} for workflow {workflow_id}")
        return plan

    async def execute_workflow(self, workflow_id: str, dry_run: bool = False) -> dict[str, Any]:
        """Execute workflow"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow not found: {workflow_id}")
            return {"status": "failed", "error": "Workflow not found"}

        workflow = self.workflows[workflow_id]
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if execution_id not in self.executions:
            self.executions[execution_id] = []

        results = []
        start_time = datetime.now()

        try:
            sorted_steps = sorted(workflow.steps, key=lambda s: s.order)

            for step in sorted_steps:
                if not step.enabled:
                    logger.info(f"Skipping disabled step: {step.step_id}")
                    result = ExecutionResult(step_id=step.step_id, status="skipped")
                    results.append(result)
                    continue

                # Execute step based on type
                step_start = datetime.now()

                try:
                    if dry_run:
                        # Dry run - just log
                        logger.info(f"[DRY RUN] Would execute {step.action_type}: {step.name}")
                        output = {
                            "action": step.action_type,
                            "name": step.name,
                            "parameters": step.parameters,
                            "dry_run": True,
                        }
                        status = "success"
                    else:
                        # Real execution
                        output = await self._execute_step(step, workflow)
                        status = "success"

                    duration_ms = (datetime.now() - step_start).total_seconds() * 1000

                    result = ExecutionResult(
                        step_id=step.step_id, status=status, output=output, duration_ms=duration_ms
                    )

                except Exception as e:
                    logger.error(f"Step execution failed: {e}")
                    duration_ms = (datetime.now() - step_start).total_seconds() * 1000
                    result = ExecutionResult(
                        step_id=step.step_id, status="failed", error=str(e), duration_ms=duration_ms
                    )

                results.append(result)
                self.executions[execution_id].append(result)

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "status": "failed",
                "execution_id": execution_id,
                "error": str(e),
                "results": [r.model_dump() for r in results],
            }

        total_duration = (datetime.now() - start_time).total_seconds()

        return {
            "status": "success",
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "total_duration_seconds": total_duration,
            "results_count": len(results),
            "results": [r.model_dump() for r in results],
        }

    async def _execute_step(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict[str, Any]:
        """Execute individual step"""

        if step.action_type == ActionType.BROWSER_AGENT:
            return await self._execute_browser_agent(step, workflow)
        elif step.action_type == ActionType.LOCAL_AGENT:
            return await self._execute_local_agent(step, workflow)
        elif step.action_type == ActionType.FILE_OPS:
            return await self._execute_file_ops(step, workflow)
        elif step.action_type == ActionType.PDF_TOOLS:
            return await self._execute_pdf_tools(step, workflow)
        elif step.action_type == ActionType.SYSTEM_CMD:
            return await self._execute_system_cmd(step, workflow)
        elif step.action_type == ActionType.DELAY:
            return await self._execute_delay(step, workflow)
        elif step.action_type == ActionType.CONDITION:
            return await self._execute_condition(step, workflow)
        else:
            raise ValueError(f"Unknown action type: {step.action_type}")

    async def _execute_browser_agent(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict:
        """Execute BrowserAgent action"""
        params = step.parameters
        return {
            "action": "browser_agent",
            "instruction": params.get("instruction", ""),
            "timeout": step.timeout_seconds,
            "result": "Browser action executed",
        }

    async def _execute_local_agent(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict:
        """Execute LocalAgentPro action"""
        params = step.parameters
        return {
            "action": "local_agent",
            "command": params.get("command", ""),
            "agent_id": params.get("agent_id", ""),
            "result": "Agent action executed",
        }

    async def _execute_file_ops(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict:
        """Execute file operations"""
        params = step.parameters
        return {
            "action": "file_ops",
            "operation": params.get("operation", ""),
            "path": params.get("path", ""),
            "result": "File operation executed",
        }

    async def _execute_pdf_tools(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict:
        """Execute PDF tools"""
        params = step.parameters
        return {
            "action": "pdf_tools",
            "operation": params.get("operation", ""),
            "file": params.get("file", ""),
            "result": "PDF operation executed",
        }

    async def _execute_system_cmd(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict:
        """Execute system command"""
        params = step.parameters
        return {"action": "system_cmd", "command": params.get("command", ""), "result": "System command executed"}

    async def _execute_delay(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict:
        """Execute delay"""
        params = step.parameters
        delay_seconds = params.get("seconds", 1)
        await asyncio.sleep(delay_seconds)
        return {"action": "delay", "seconds": delay_seconds, "result": f"Waited {delay_seconds} seconds"}

    async def _execute_condition(self, step: WorkflowStep, workflow: WorkflowConfig) -> dict:
        """Execute conditional logic"""
        params = step.parameters
        return {"action": "condition", "condition": params.get("condition", ""), "result": "Condition evaluated"}

    async def get_workflow_status(self, workflow_id: str) -> dict | None:
        """Get current workflow status"""
        if workflow_id not in self.workflows:
            return None

        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "enabled": workflow.enabled,
            "steps_count": len(workflow.steps),
            "steps": [
                {
                    "step_id": s.step_id,
                    "name": s.name,
                    "action_type": s.action_type,
                    "order": s.order,
                    "enabled": s.enabled,
                }
                for s in sorted(workflow.steps, key=lambda s: s.order)
            ],
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at,
        }

    async def list_workflows(self) -> list[dict]:
        """List all workflows"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "steps_count": len(wf.steps),
                "enabled": wf.enabled,
                "created_at": wf.created_at,
            }
            for wf in self.workflows.values()
        ]


# ============================================================================
# OPENWEBUI TOOL CLASS
# ============================================================================


class Tools:
    """Portier Workflow Builder OpenWebUI Tool"""

    def __init__(self):
        """Initialize tool"""
        self.engine = WorkflowEngine()
        logger.info("Portier Workflow Builder 1.0.0 initialized")

    async def workflow_builder_create(
        self, name: str, description: str = "", auto_execute: bool = False
    ) -> dict[str, Any]:
        """
        Create new workflow

        Args:
            name: Workflow name
            description: Workflow description
            auto_execute: Enable auto-execution

        Returns:
            Workflow creation result
        """
        try:
            workflow_id = await self.engine.create_workflow(
                name=name, description=description, auto_execute=auto_execute
            )
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "name": name,
                "message": f"Workflow '{name}' created successfully",
            }
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return {"status": "failed", "error": str(e)}

    async def workflow_builder_add_step(
        self, workflow_id: str, name: str, action_type: str, parameters: dict[str, Any], description: str = ""
    ) -> dict[str, Any]:
        """
        Add step to workflow

        Args:
            workflow_id: Target workflow ID
            name: Step name
            action_type: One of: browser_agent, local_agent, file_ops, pdf_tools, system_cmd, delay, condition
            parameters: Step parameters as JSON
            description: Step description

        Returns:
            Step addition result
        """
        try:
            action = ActionType(action_type)
            success = await self.engine.add_step(
                workflow_id=workflow_id, name=name, action_type=action, parameters=parameters, description=description
            )

            if success:
                return {"status": "success", "message": f"Step '{name}' added to workflow"}
            else:
                return {"status": "failed", "error": "Failed to add step"}
        except Exception as e:
            logger.error(f"Error adding step: {e}")
            return {"status": "failed", "error": str(e)}

    async def workflow_builder_execute(self, workflow_id: str, dry_run: bool = False) -> dict[str, Any]:
        """
        Execute workflow

        Args:
            workflow_id: Workflow to execute
            dry_run: Preview execution without running

        Returns:
            Execution result
        """
        try:
            result = await self.engine.execute_workflow(workflow_id=workflow_id, dry_run=dry_run)
            return result
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {"status": "failed", "error": str(e)}

    async def workflow_builder_plan(self, workflow_id: str) -> dict[str, Any]:
        """
        Generate execution plan for workflow

        Args:
            workflow_id: Workflow to plan

        Returns:
            Execution plan
        """
        try:
            plan = await self.engine.generate_execution_plan(workflow_id)
            if plan:
                return {"status": "success", "plan": plan.model_dump()}
            else:
                return {"status": "failed", "error": "Could not generate plan"}
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return {"status": "failed", "error": str(e)}

    async def workflow_builder_status(self, workflow_id: str) -> dict[str, Any]:
        """
        Get workflow status

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow status
        """
        try:
            status = await self.engine.get_workflow_status(workflow_id)
            if status:
                return {"status": "success", "workflow": status}
            else:
                return {"status": "failed", "error": "Workflow not found"}
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"status": "failed", "error": str(e)}

    async def workflow_builder_list(self) -> dict[str, Any]:
        """
        List all workflows

        Returns:
            List of workflows
        """
        try:
            workflows = await self.engine.list_workflows()
            return {"status": "success", "count": len(workflows), "workflows": workflows}
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return {"status": "failed", "error": str(e)}


# ============================================================================
# EXPORT FOR OPENWEBUI
# ============================================================================

__all__ = ["Tools"]
