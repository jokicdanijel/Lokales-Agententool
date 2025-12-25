"""
Unit tests for shared configuration utilities.
"""

import pytest

from src.pkg.shared.config import ALLOWED_PORT_RANGE, FORBIDDEN_PORTS, get_port_from_env, validate_port


class TestValidatePort:
    """Tests for validate_port function."""

    def test_valid_port(self):
        """Should accept valid port in range."""
        port = validate_port(12356, "test_service")
        assert port == 12356

    def test_forbidden_port(self):
        """Should reject forbidden ports."""
        with pytest.raises(RuntimeError) as exc_info:
            validate_port(8080, "test_service")
        assert "forbidden" in str(exc_info.value).lower()
        assert "8080" in str(exc_info.value)

    def test_port_below_range(self):
        """Should reject port below allowed range."""
        with pytest.raises(RuntimeError) as exc_info:
            validate_port(12000, "test_service")
        assert "outside allowed range" in str(exc_info.value).lower()

    def test_port_above_range(self):
        """Should reject port above allowed range."""
        with pytest.raises(RuntimeError) as exc_info:
            validate_port(13000, "test_service")
        assert "outside allowed range" in str(exc_info.value).lower()

    def test_edge_case_min_port(self):
        """Should accept minimum allowed port."""
        port = validate_port(12344, "test_service")
        assert port == 12344

    def test_edge_case_max_port(self):
        """Should accept maximum allowed port."""
        port = validate_port(12399, "test_service")
        assert port == 12399


class TestGetPortFromEnv:
    """Tests for get_port_from_env function."""

    def test_default_port(self, monkeypatch):
        """Should use default when env var not set."""
        monkeypatch.delenv("TEST_PORT", raising=False)
        port = get_port_from_env("TEST_PORT", 12356, "test_service")
        assert port == 12356

    def test_env_port(self, monkeypatch):
        """Should use port from environment."""
        monkeypatch.setenv("TEST_PORT", "12357")
        port = get_port_from_env("TEST_PORT", 12356, "test_service")
        assert port == 12357

    def test_invalid_env_port(self, monkeypatch):
        """Should reject invalid port from environment."""
        monkeypatch.setenv("TEST_PORT", "8080")
        with pytest.raises(RuntimeError):
            get_port_from_env("TEST_PORT", 12356, "test_service")

    def test_validates_default_port(self):
        """Should validate default port as well."""
        with pytest.raises(RuntimeError):
            get_port_from_env("NONEXISTENT_VAR", 8080, "test_service")


class TestPortConstants:
    """Tests for port configuration constants."""

    def test_allowed_range(self):
        """Should have correct allowed port range."""
        assert ALLOWED_PORT_RANGE.start == 12344
        assert ALLOWED_PORT_RANGE.stop == 12400

    def test_forbidden_ports(self):
        """Should include forbidden ports."""
        assert 8080 in FORBIDDEN_PORTS
