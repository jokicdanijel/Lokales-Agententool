#!/usr/bin/env python3
"""
opena21 - Workflow Engine Agent
Test Suite - 20 Unit Tests

PORTIER 3.0 Compliant Testing
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


# ================== BASIC TESTS ==================

class TestBasicStructure:
    """Basic Structure Tests"""
    
    def test_directory_exists(self):
        """Test: Agent Directory existiert"""
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/20.opena21_workflow")
        assert agent_dir.exists()
    
    def test_html_exists(self):
        """Test: HTML-Verzeichnis existiert"""
        html_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/20.opena21_workflow/html")
        assert html_dir.exists()
    
    def test_readme_exists(self):
        """Test: README existiert"""
        readme_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/20.opena21_workflow/README.md")
        assert readme_file.exists()
    
    def test_main_agent_exists(self):
        """Test: Main Agent File existiert"""
        main_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/20.opena21_workflow/main.py")
        assert main_file.exists()


# ================== MODEL TESTS ==================

class TestModels:
    """Tests für Pydantic Models"""
    
    def test_workflow_state_enum(self):
        """Test: WorkflowState Enum"""
        try:
            from models import WorkflowState
            assert WorkflowState.PENDING.value == "pending"
            assert WorkflowState.RUNNING.value == "running"
            assert WorkflowState.COMPLETED.value == "completed"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_step_definition_valid(self):
        """Test: Gültige StepDefinition"""
        try:
            from models import StepDefinition, ActionType
            step = StepDefinition(
                name="test_step",
                action=ActionType.CALL_AGENT,
                agent="opena3",
                timeout=30
            )
            assert step.name == "test_step"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_workflow_definition_valid(self):
        """Test: Gültige WorkflowDefinition"""
        try:
            from models import WorkflowDefinition, StepDefinition, ActionType
            workflow = WorkflowDefinition(
                name="test_workflow",
                description="Test Workflow",
                steps=[
                    StepDefinition(
                        name="step1",
                        action=ActionType.CALL_AGENT,
                        agent="opena3"
                    )
                ]
            )
            assert workflow.name == "test_workflow"
            assert len(workflow.steps) == 1
        except ImportError:
            pytest.skip("models.py not available")


# ================== SECURITY TESTS ==================

class TestSecurity:
    """Tests für Security-Module"""
    
    def test_mask_secrets(self):
        """Test: Secret Masking"""
        try:
            from security import mask_secrets
            data = {"api_key": "secret123", "workflow": "test"}
            masked = mask_secrets(data)
            assert masked["api_key"] == "***MASKED***"
            assert masked["workflow"] == "test"
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_workflow_security_validate_action(self):
        """Test: Action Validation"""
        try:
            from security import WorkflowSecurityManager
            assert WorkflowSecurityManager.validate_action("call_agent") is True
            assert WorkflowSecurityManager.validate_action("invalid") is False
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_workflow_security_validate_agent(self):
        """Test: Agent Validation"""
        try:
            from security import WorkflowSecurityManager
            assert WorkflowSecurityManager.validate_agent("opena3") is True
            assert WorkflowSecurityManager.validate_agent("invalid") is False
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_rate_limiter_allows(self):
        """Test: Rate Limiter erlaubt Requests"""
        try:
            from security import RateLimiter
            limiter = RateLimiter(max_requests=5, window_seconds=60)
            mock_request = MagicMock()
            mock_request.client.host = "127.0.0.1"
            mock_request.headers.get.return_value = None
            assert limiter.is_allowed(mock_request) is True
        except ImportError:
            pytest.skip("security.py not available")


# ================== CONFIG TESTS ==================

class TestConfig:
    """Tests für Konfiguration"""
    
    def test_load_config(self):
        """Test: Konfiguration laden"""
        try:
            from config import load_config
            config = load_config()
            assert config.service_name == "opena21"
            assert config.program_target == "workflowp"
            assert config.port == 12364
        except ImportError:
            pytest.skip("config.py not available")
    
    def test_port_policy(self):
        """Test: Port Policy"""
        try:
            from config import load_config
            config = load_config()
            assert config.allowed_ports_start == 12344
            assert config.allowed_ports_end == 12399
            assert 8080 in config.forbidden_ports
        except ImportError:
            pytest.skip("config.py not available")
    
    def test_config_defaults(self):
        """Test: Config Defaults"""
        try:
            from config import load_config
            config = load_config()
            assert config.default_timeout == 300
            assert config.max_retry_count == 3
        except ImportError:
            pytest.skip("config.py not available")


# ================== ENUM TESTS ==================

class TestEnums:
    """Tests für Enums"""
    
    def test_action_type_values(self):
        """Test: ActionType Werte"""
        try:
            from models import ActionType
            assert ActionType.CALL_AGENT.value == "call_agent"
            assert ActionType.TRANSFORM_DATA.value == "transform_data"
            assert ActionType.CONDITION.value == "condition"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_on_failure_action_values(self):
        """Test: OnFailureAction Werte"""
        try:
            from models import OnFailureAction
            assert OnFailureAction.STOP.value == "stop"
            assert OnFailureAction.CONTINUE.value == "continue"
            assert OnFailureAction.RETRY.value == "retry"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_safepoint_category_values(self):
        """Test: SafepointCategory Werte"""
        try:
            from models import SafepointCategory
            assert SafepointCategory.CMD.value == "CMD"
            assert SafepointCategory.RESP.value == "RESP"
        except ImportError:
            pytest.skip("models.py not available")


# ================== RESPONSE MODEL TESTS ==================

class TestResponseModels:
    """Tests für Response Models"""
    
    def test_health_response_model(self):
        """Test: HealthResponse Model"""
        try:
            from models import HealthResponse
            health = HealthResponse(
                status="ok",
                service="opena21",
                port=12364,
                program_target="workflowp",
                uptime_seconds=100.5,
                version="2.0",
                workflows_count=5,
                executions_running=2,
                strict=True
            )
            assert health.status == "ok"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_execute_request_model(self):
        """Test: ExecuteRequest Model"""
        try:
            from models import ExecuteRequest
            req = ExecuteRequest(
                workflow_name="test_workflow",
                inputs={"key": "value"},
                mode="sync"
            )
            assert req.workflow_name == "test_workflow"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_workflow_status_model(self):
        """Test: WorkflowStatus Model"""
        try:
            from models import WorkflowStatus, WorkflowState
            status = WorkflowStatus(
                workflow_id="wf_123",
                workflow_name="test",
                state=WorkflowState.RUNNING,
                started_at="2025-01-01T00:00:00Z",
                steps_total=5
            )
            assert status.state == WorkflowState.RUNNING
        except ImportError:
            pytest.skip("models.py not available")


# ================== MAIN ==================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
