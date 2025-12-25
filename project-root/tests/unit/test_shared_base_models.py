"""
Unit tests for shared base models.
"""

import time

import pytest
from pydantic import ValidationError

from src.pkg.shared.base_models import (
    CommandRequest,
    ErrorResponse,
    HealthResponse,
    ServiceInfo,
    SuccessResponse,
    create_health_response,
    create_service_info,
    get_current_timestamp_iso,
)


class TestCommandRequest:
    """Tests for CommandRequest model."""

    def test_valid_request(self):
        """Should accept valid command request."""
        req = CommandRequest(command="test_command", params={"key": "value"})
        assert req.command == "test_command"
        assert req.params == {"key": "value"}

    def test_empty_params(self):
        """Should accept empty params."""
        req = CommandRequest(command="test")
        assert req.params == {}

    def test_reject_extra_fields(self):
        """Should reject extra fields (strict mode)."""
        with pytest.raises(ValidationError):
            CommandRequest(command="test", params={}, extra_field="not_allowed")

    def test_command_length_validation(self):
        """Should validate command length."""
        # Too short
        with pytest.raises(ValidationError):
            CommandRequest(command="")

        # Too long
        with pytest.raises(ValidationError):
            CommandRequest(command="x" * 201)


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_valid_health_response(self):
        """Should accept valid health response."""
        resp = HealthResponse(
            status="ok",
            service="opena11",
            kuerzel="unlockp",
            port=12356,
            uptime_seconds=123.45,
            timestamp="2025-12-18T01:00:00Z",
        )
        assert resp.status == "ok"
        assert resp.port == 12356

    def test_with_extra_info(self):
        """Should accept extra_info field."""
        resp = HealthResponse(
            status="ok",
            service="opena11",
            kuerzel="unlockp",
            port=12356,
            uptime_seconds=100.0,
            timestamp="2025-12-18T01:00:00Z",
            extra_info={"custom": "data"},
        )
        assert resp.extra_info == {"custom": "data"}

    def test_allows_custom_fields(self):
        """Should allow custom fields (extra='allow')."""
        # This should not raise an error
        resp = HealthResponse(
            status="ok",
            service="test",
            kuerzel="tst",
            port=12345,
            uptime_seconds=1.0,
            timestamp="2025-12-18T01:00:00Z",
            custom_field="allowed",
        )
        assert resp.status == "ok"


class TestServiceInfo:
    """Tests for ServiceInfo model."""

    def test_valid_service_info(self):
        """Should accept valid service info."""
        info = ServiceInfo(
            service="opena11",
            kuerzel="unlockp",
            description="Unlock Master Agent",
            port=12356,
            version="2.0",
            endpoints=["/health", "/command"],
        )
        assert info.service == "opena11"
        assert len(info.endpoints) == 2


class TestSuccessResponse:
    """Tests for SuccessResponse model."""

    def test_basic_success(self):
        """Should create basic success response."""
        resp = SuccessResponse(message="Operation completed")
        assert resp.status == "success"
        assert resp.message == "Operation completed"
        assert resp.data is None

    def test_with_data(self):
        """Should accept data field."""
        resp = SuccessResponse(message="Created", data={"id": "123", "name": "Test"})
        assert resp.data["id"] == "123"


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_basic_error(self):
        """Should create basic error response."""
        resp = ErrorResponse(message="Something went wrong")
        assert resp.status == "error"
        assert resp.message == "Something went wrong"

    def test_with_error_code(self):
        """Should accept error_code."""
        resp = ErrorResponse(message="Not found", error_code="NOT_FOUND")
        assert resp.error_code == "NOT_FOUND"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_current_timestamp_iso(self):
        """Should return valid ISO timestamp."""
        timestamp = get_current_timestamp_iso()
        assert isinstance(timestamp, str)
        assert timestamp.endswith("Z")
        assert "T" in timestamp

    def test_create_health_response(self):
        """Should create health response with factory."""
        start_time = time.time()
        time.sleep(0.1)  # Small delay

        resp = create_health_response(
            service="opena11", kuerzel="unlockp", port=12356, start_time=start_time, custom_metric=42
        )

        assert resp.status == "ok"
        assert resp.service == "opena11"
        assert resp.uptime_seconds > 0
        assert resp.extra_info is not None
        assert resp.extra_info["custom_metric"] == 42

    def test_create_service_info(self):
        """Should create service info with factory."""
        info = create_service_info(
            service="opena11",
            kuerzel="unlockp",
            description="Test service",
            port=12356,
            version="1.0",
            endpoints=["/health", "/command"],
        )

        assert info.service == "opena11"
        assert info.version == "1.0"
        assert len(info.endpoints) == 2
