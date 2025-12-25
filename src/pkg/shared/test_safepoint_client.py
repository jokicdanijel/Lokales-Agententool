#!/usr/bin/env python3
"""
Tests for shared safepoint_client module.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.pkg.shared.safepoint_client import SafepointClient


class TestSafepointClient:
    """Test SafepointClient functionality."""

    def test_initialization_default(self):
        """Test client initialization with defaults."""
        with patch.dict("os.environ", {"OPENA2_URL": "http://test:12345", "BEARER_TOKEN": "test-token"}):
            client = SafepointClient()
            assert client.opena2_url == "http://test:12345"
            assert client.bearer_token == "test-token"

    def test_initialization_custom(self):
        """Test client initialization with custom values."""
        client = SafepointClient(opena2_url="http://custom:9999", bearer_token="custom-token")
        assert client.opena2_url == "http://custom:9999"
        assert client.bearer_token == "custom-token"

    def test_mask_dict(self):
        """Test masking sensitive data in dictionaries."""
        data = {"username": "john", "password": "secret123", "api_key": "key123", "normal_field": "visible"}
        masked = SafepointClient._mask(data)

        assert masked["username"] == "john"
        assert masked["password"] == "***"
        assert masked["api_key"] == "***"
        assert masked["normal_field"] == "visible"

    def test_mask_nested_dict(self):
        """Test masking nested dictionaries."""
        data = {"user": {"name": "john", "credentials": {"password": "secret"}}}
        masked = SafepointClient._mask(data)

        assert masked["user"]["name"] == "john"
        assert masked["user"]["credentials"]["password"] == "***"

    def test_mask_list(self):
        """Test masking lists."""
        data = [{"token": "secret1"}, {"token": "secret2"}]
        masked = SafepointClient._mask(data)

        assert masked[0]["token"] == "***"
        assert masked[1]["token"] == "***"

    def test_categories(self):
        """Test valid categories."""
        assert "CMD" in SafepointClient.CATEGORIES
        assert "RESP" in SafepointClient.CATEGORIES
        assert "ROUTE" in SafepointClient.CATEGORIES
        assert "DISPATCH" in SafepointClient.CATEGORIES

    @pytest.mark.asyncio
    async def test_write_invalid_category(self):
        """Test write with invalid category raises error."""
        client = SafepointClient()

        with pytest.raises(ValueError, match="Invalid category"):
            await client.write(category="INVALID", source="test", destination="test", request_id="123", payload={})

    @pytest.mark.asyncio
    async def test_write_success(self):
        """Test successful write operation."""
        client = SafepointClient(opena2_url="http://test:12345", bearer_token="test-token")

        mock_response = AsyncMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            result = await client.write(
                category="CMD", source="opena4", destination="opena5", request_id="test123", payload={"action": "test"}
            )

            assert result["source"] == "opena4"
            assert result["destination"] == "opena5"
            assert result["category"] == "CMD"
            assert result["request_id"] == "test123"
            assert result["strict"] is True
            assert "timestamp" in result
            assert "sp_timestamp" in result

            # Verify API call
            mock_instance.post.assert_called_once()
            call_args = mock_instance.post.call_args
            assert call_args[0][0] == "http://test:12345/store/CMD"
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_write_masks_payload(self):
        """Test that write masks sensitive payload data."""
        client = SafepointClient()

        payload = {"username": "john", "password": "secret123"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.post = AsyncMock()
            mock_client.return_value = mock_instance

            result = await client.write(
                category="CMD", source="test", destination="test", request_id="123", payload=payload
            )

            # Check that password was masked in result
            assert result["payload"]["username"] == "john"
            assert result["payload"]["password"] == "***"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
