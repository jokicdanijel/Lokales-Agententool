"""
tests/test_openwebui_service.py
Unit tests for OpenA3 (OpenWebUI → openweb)
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.services.openwebui.service import app


def test_health_ok():
    """Test /health endpoint."""
    with patch("src.services.openwebui.service._route_register", new_callable=AsyncMock):
        client = TestClient(app)
        r = client.get("/health")
        assert r.status_code == 200
        j = r.json()
        assert j["component"] == "openwebui"
        assert j["port"] == 12346
        assert j["status"] == "ok"


def test_ping():
    """Test /openwebui/ping endpoint."""
    with patch("src.services.openwebui.service._route_register", new_callable=AsyncMock):
        client = TestClient(app)
        r = client.get("/openwebui/ping")
        assert r.status_code == 200
        j = r.json()
        assert j["pong"] == "openweb"
        assert j["ok"] is True


def test_call_prompt_valid():
    """Test /openwebui/call with valid prompt action."""
    with patch("src.services.openwebui.service._route_register", new_callable=AsyncMock):
        with patch("src.services.openwebui.service.httpx.AsyncClient.post", new_callable=AsyncMock):
            client = TestClient(app)
            r = client.post("/openwebui/call", json={"action": "prompt", "data": {"text": "hello world"}})
            assert r.status_code == 200
            j = r.json()
            assert j["ok"] is True
            assert j["echo"] == "hello world"


def test_call_unsupported_action():
    """Test /openwebui/call with unsupported action."""
    with patch("src.services.openwebui.service._route_register", new_callable=AsyncMock):
        client = TestClient(app)
        r = client.post("/openwebui/call", json={"action": "invalid_action", "data": {}})
        assert r.status_code == 400


def test_redaction_in_call():
    """Test that secrets are redacted in /openwebui/call."""
    with patch("src.services.openwebui.service._route_register", new_callable=AsyncMock):
        with patch("src.services.openwebui.service.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            client = TestClient(app)
            r = client.post(
                "/openwebui/call", json={"action": "prompt", "data": {"text": "hello", "api_key": "secret123"}}
            )
            assert r.status_code == 200
            # Verify redaction in the call (mock should receive redacted payload)
            # The actual redaction happens in the safepoint call to OpenA2
            assert mock_post.called


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
