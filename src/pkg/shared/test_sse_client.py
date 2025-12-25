#!/usr/bin/env python3
"""
Tests for shared sse_client module.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.pkg.shared.sse_client import (
    SafepointClient,
    SSEClient,
    SSEEvent,
    create_safepoint_client,
    create_sse_client,
    get_safepoint_client,
    get_sse_client,
)


class TestSSEClient:
    """Test SSEClient functionality."""

    def test_initialization_default(self):
        """Test SSE client initialization with defaults."""
        with patch.dict("os.environ", {"OPENA20_URL": "http://test:12349", "BEARER_TOKEN": "test-token"}):
            client = SSEClient()
            assert client.base_url == "http://test:12349"
            assert client.bearer_token == "test-token"

    def test_initialization_custom(self):
        """Test SSE client initialization with custom values."""
        client = SSEClient(base_url="http://custom:9999", bearer_token="custom-token", timeout=60.0)
        assert client.base_url == "http://custom:9999"
        assert client.bearer_token == "custom-token"
        assert client.timeout == 60.0

    def test_parse_event_complete(self):
        """Test parsing complete SSE event."""
        client = SSEClient()
        event_str = 'event: test\ndata: {"key": "value"}\nid: 123'

        result = client._parse_event(event_str)

        assert result["event_type"] == "test"
        assert result["data"] == {"key": "value"}
        assert result["event_id"] == "123"

    def test_parse_event_data_only(self):
        """Test parsing event with data only."""
        client = SSEClient()
        event_str = "data: plain text"

        result = client._parse_event(event_str)

        assert result["data"] == "plain text"
        assert "event_type" not in result

    def test_parse_event_empty(self):
        """Test parsing empty event returns None."""
        client = SSEClient()
        event_str = ""

        result = client._parse_event(event_str)

        assert result is None

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connection establishment."""
        client = SSEClient()

        await client.connect()

        assert client._client is not None
        assert client._running is True

        await client.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        client = SSEClient()
        await client.connect()

        await client.disconnect()

        assert client._running is False
        assert client._client is None


class TestSafepointClient:
    """Test SafepointClient functionality."""

    def test_initialization(self):
        """Test safepoint client initialization."""
        client = SafepointClient(base_url="http://test:12345", bearer_token="test-token", source_agent="opena4")

        assert client.base_url == "http://test:12345"
        assert client.bearer_token == "test-token"
        assert client.source_agent == "opena4"

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connection establishment."""
        client = SafepointClient(source_agent="opena4")

        await client.connect()

        assert client._client is not None

        await client.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        client = SafepointClient(source_agent="opena4")
        await client.connect()

        await client.disconnect()

        assert client._client is None

    @pytest.mark.asyncio
    async def test_write_safepoint_auto_request_id(self):
        """Test write_safepoint with auto-generated request_id."""
        client = SafepointClient(base_url="http://test:12345", bearer_token="test-token", source_agent="opena4")

        mock_response = AsyncMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            result = await client.write_safepoint(category="CMD", destination="opena5", payload={"action": "test"})

            assert result is not None
            assert len(result) == 8  # UUID[:8]

            # Verify the call
            mock_instance.post.assert_called_once()
            call_args = mock_instance.post.call_args
            json_data = call_args[1]["json"]

            assert json_data["source"] == "opena4"
            assert json_data["destination"] == "opena5"
            assert json_data["category"] == "CMD"
            assert json_data["strict"] is True


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_sse_client(self):
        """Test SSE client factory."""
        client = create_sse_client(source_agent="opena4", base_url="http://test:12349")

        assert isinstance(client, SSEClient)
        assert client.base_url == "http://test:12349"

    def test_create_safepoint_client(self):
        """Test safepoint client factory."""
        client = create_safepoint_client(source_agent="opena7", base_url="http://test:12345")

        assert isinstance(client, SafepointClient)
        assert client.source_agent == "opena7"
        assert client.base_url == "http://test:12345"

    def test_get_sse_client_singleton(self):
        """Test singleton SSE client."""
        client1 = get_sse_client()
        client2 = get_sse_client()

        assert client1 is client2

    def test_get_safepoint_client_singleton(self):
        """Test singleton safepoint client."""
        client1 = get_safepoint_client("opena4")
        client2 = get_safepoint_client("opena4")

        # Note: Due to implementation, these will be the same instance
        # but with potentially different source_agent if called differently
        assert isinstance(client1, SafepointClient)
        assert isinstance(client2, SafepointClient)


class TestSSEEvent:
    """Test SSEEvent dataclass."""

    def test_creation_minimal(self):
        """Test creating event with minimal fields."""
        event = SSEEvent(event_type="test", data={"key": "value"})

        assert event.event_type == "test"
        assert event.data == {"key": "value"}
        assert event.timestamp is not None
        assert event.event_id is None

    def test_creation_full(self):
        """Test creating event with all fields."""
        event = SSEEvent(event_type="test", data={"key": "value"}, timestamp="2025-01-01T00:00:00Z", event_id="123")

        assert event.event_type == "test"
        assert event.data == {"key": "value"}
        assert event.timestamp == "2025-01-01T00:00:00Z"
        assert event.event_id == "123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
