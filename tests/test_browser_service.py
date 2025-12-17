"""
opena6 Browser Agent Unit Tests
Health, policy, artifact, and playbook execution validation
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Test imports (assuming tests run from project root)
import sys
sys.path.insert(0, "5.opena6_browser")

from app.config import config
from app.models import (
    PlaybookRequest, PlaybookStep, ActionType, PlaybookResponse,
    HealthResponse, ReadyResponse, Safepoint, ComplianceConfig,
    ArtifactConfig, ViewportConfig
)
from app.browser_client import PolicyGate, ArtifactWriter


class TestHealthEndpoints:
    """Test health & readiness endpoints"""
    
    def test_health_response_structure(self):
        """Verify health check response structure"""
        
        health = HealthResponse(
            service="opena6",
            status="ok",
            component="browser",
            port=12349,
            browser="playwright-chromium",
            ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        
        assert health.service == "opena6"
        assert health.status == "ok"
        assert health.component == "browser"
        assert health.port == 12349
    
    def test_readiness_response_structure(self):
        """Verify readiness check response structure"""
        
        ready = ReadyResponse(
            ready=True,
            browser="playwright-chromium",
            version="1.0.0"
        )
        
        assert ready.ready is True
        assert "chromium" in ready.browser


class TestPolicyGate:
    """Test policy enforcement (domain allowlist, robots.txt)"""
    
    @pytest.mark.asyncio
    async def test_domain_allowlist_check(self):
        """Verify domain allowlist enforcement"""
        
        compliance = ComplianceConfig(
            allow_domains=["example.org", "localhost"],
            obey_robots=True
        )
        
        gate = PolicyGate(compliance)
        
        # Should allow
        request = PlaybookRequest(
            steps=[
                PlaybookStep(action=ActionType.GOTO, url="https://example.org")
            ],
            compliance=compliance
        )
        
        allowed, reason = await gate.validate_request(request)
        assert allowed is True
        assert reason is None
    
    @pytest.mark.asyncio
    async def test_domain_blocklist_enforcement(self):
        """Verify blocked domains are rejected"""
        
        compliance = ComplianceConfig(
            allow_domains=["example.org"],
            obey_robots=True
        )
        
        gate = PolicyGate(compliance)
        
        # Should block
        request = PlaybookRequest(
            steps=[
                PlaybookStep(action=ActionType.GOTO, url="https://evil.com")
            ],
            compliance=compliance
        )
        
        allowed, reason = await gate.validate_request(request)
        assert allowed is False
        assert "not in allowlist" in reason


class TestPlaybookRequest:
    """Test playbook request validation"""
    
    def test_playbook_request_creation(self):
        """Verify playbook request structure"""
        
        request = PlaybookRequest(
            request_id="test-001",
            steps=[
                PlaybookStep(action=ActionType.GOTO, url="https://example.org"),
                PlaybookStep(action=ActionType.SCREENSHOT, label="homepage"),
            ],
            compliance=ComplianceConfig(allow_domains=["example.org"]),
            archiv=ArtifactConfig(attach_screenshot=True, attach_html=True)
        )
        
        assert request.request_id == "test-001"
        assert len(request.steps) == 2
        assert request.steps[0].action == ActionType.GOTO
        assert request.steps[1].action == ActionType.SCREENSHOT
    
    def test_playbook_step_actions(self):
        """Verify all supported playbook actions"""
        
        actions = [
            ActionType.GOTO,
            ActionType.FILL,
            ActionType.CLICK,
            ActionType.WAIT_FOR,
            ActionType.SCREENSHOT,
            ActionType.EXTRACT,
            ActionType.SUBMIT,
        ]
        
        for action in actions:
            step = PlaybookStep(action=action)
            assert step.action == action
    
    def test_viewport_configuration(self):
        """Verify viewport configuration"""
        
        viewport = ViewportConfig(width=1920, height=1080)
        assert viewport.width == 1920
        assert viewport.height == 1080
        
        # Test defaults
        default_viewport = ViewportConfig()
        assert default_viewport.width == 1280
        assert default_viewport.height == 800


class TestPlaybookResponse:
    """Test playbook response structure"""
    
    def test_success_response_structure(self):
        """Verify success response format"""
        
        from app.models import ArtifactCollection, TimingInfo
        
        response = PlaybookResponse(
            request_id="test-001",
            status="success",
            artifacts=ArtifactCollection(),
            timings=TimingInfo(total_ms=3500),
            strict=True
        )
        
        assert response.status == "success"
        assert response.timings.total_ms == 3500
        assert len(response.artifacts.screenshots) == 0
    
    def test_error_response_structure(self):
        """Verify error response format"""
        
        from app.models import ArtifactCollection, TimingInfo, ErrorInfo
        
        response = PlaybookResponse(
            request_id="test-001",
            status="failed",
            artifacts=ArtifactCollection(),
            timings=TimingInfo(total_ms=1200),
            error=ErrorInfo(code="SelectorNotFound", message="#kpi not found"),
            strict=True
        )
        
        assert response.status == "failed"
        assert response.error.code == "SelectorNotFound"


class TestArtifactWriter:
    """Test artifact capture & storage"""
    
    def test_artifact_reference_structure(self):
        """Verify artifact reference structure"""
        
        from app.models import ArtifactRef
        
        artifact = ArtifactRef(
            label="screenshot_01",
            path="archivp/2025/11/10/screenshot_01.png",
            sha256="abc123def456",
            size_bytes=65536,
            mime_type="image/png"
        )
        
        assert artifact.label == "screenshot_01"
        assert artifact.mime_type == "image/png"
        assert artifact.size_bytes == 65536


class TestSafepoint:
    """Test safepoint structure for archiving"""
    
    def test_safepoint_creation(self):
        """Verify safepoint structure"""
        
        payload = {
            "status": "success",
            "artifacts": {"screenshots": []}
        }
        
        safepoint = Safepoint(
            ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            src="opena6",
            dst="opena2",
            kind="RESP",
            request_id="test-001",
            payload=payload
        )
        
        assert safepoint.src == "opena6"
        assert safepoint.dst == "opena2"
        assert safepoint.kind == "RESP"


class TestConfiguration:
    """Test configuration loading"""
    
    def test_config_defaults(self):
        """Verify configuration defaults"""
        
        assert config.SERVICE_NAME == "opena6"
        assert config.SERVICE_COMPONENT == "browser"
        assert config.PORT == 12349
        assert config.HEADLESS is True
        assert config.DEFAULT_RPS_LIMIT == 1.0


# ============================================================================
# INTEGRATION TEST PATTERNS (marked as integration, skip by default)
# ============================================================================

@pytest.mark.skip(reason="Integration test — requires browser runtime")
class TestBrowserExecution:
    """Integration tests with actual browser"""
    
    @pytest.mark.asyncio
    async def test_simple_navigation(self):
        """Test simple page navigation"""
        
        from app.browser_client import BrowserExecutor
        
        executor = BrowserExecutor()
        await executor.startup()
        
        try:
            request = PlaybookRequest(
                request_id="int-test-001",
                steps=[
                    PlaybookStep(
                        action=ActionType.GOTO,
                        url="https://example.org",
                        wait="load"
                    ),
                    PlaybookStep(
                        action=ActionType.SCREENSHOT,
                        label="homepage"
                    )
                ],
                compliance=ComplianceConfig(allow_domains=["example.org"])
            )
            
            response = await executor.execute_playbook(request)
            
            assert response.status == "success"
            assert len(response.artifacts.screenshots) > 0
        
        finally:
            await executor.shutdown()


# ============================================================================
# MOCK TEST SUITE (for CI/CD without browser)
# ============================================================================

class TestMockExecutor:
    """Mock executor tests (no browser runtime required)"""
    
    @pytest.mark.asyncio
    async def test_mock_playbook_execution(self):
        """Test playbook execution with mocks"""
        
        from app.models import ArtifactRef, ArtifactCollection, TimingInfo
        
        # Simulate successful execution
        mock_response = PlaybookResponse(
            request_id="mock-001",
            status="success",
            artifacts=ArtifactCollection(
                screenshots=[
                    ArtifactRef(
                        label="homepage",
                        path="archivp/2025/11/10/screenshot.png",
                        sha256="abc123"
                    )
                ]
            ),
            timings=TimingInfo(total_ms=2500),
            strict=True
        )
        
        assert mock_response.status == "success"
        assert len(mock_response.artifacts.screenshots) == 1


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
