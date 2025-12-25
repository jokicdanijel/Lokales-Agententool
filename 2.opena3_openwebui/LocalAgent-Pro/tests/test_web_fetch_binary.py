#!/usr/bin/env python3
"""
Tests für das Binary-Handling in fetch_webpage()
LocalAgent-Pro - Binary Download Fix
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestClassifyContentType:
    """Tests für classify_content_type()"""

    def test_json_content_type(self):
        from openwebui_agent_server import classify_content_type

        assert classify_content_type("application/json") == "json"
        assert classify_content_type("application/json; charset=utf-8") == "json"

    def test_text_content_types(self):
        from openwebui_agent_server import classify_content_type

        assert classify_content_type("text/html") == "text"
        assert classify_content_type("text/plain") == "text"
        assert classify_content_type("text/html; charset=utf-8") == "text"
        assert classify_content_type("application/xhtml+xml") == "text"  # hat "html" drin

    def test_binary_content_types(self):
        from openwebui_agent_server import classify_content_type

        assert classify_content_type("application/octet-stream") == "binary"
        assert classify_content_type("application/pgp-keys") == "binary"
        assert classify_content_type("application/x-gzip") == "binary"
        assert classify_content_type("image/png") == "binary"
        assert classify_content_type("application/pdf") == "binary"

    def test_empty_content_type(self):
        from openwebui_agent_server import classify_content_type

        assert classify_content_type("") == "binary"
        assert classify_content_type(None) == "binary"


class TestGetFilenameFromResponse:
    """Tests für get_filename_from_response()"""

    def test_filename_from_content_disposition(self):
        from openwebui_agent_server import get_filename_from_response

        mock_response = Mock()
        mock_response.headers = {"Content-Disposition": 'attachment; filename="test.gpg"'}

        result = get_filename_from_response(mock_response, "https://example.com/path")
        assert result == "test.gpg"

    def test_filename_from_content_disposition_unquoted(self):
        from openwebui_agent_server import get_filename_from_response

        mock_response = Mock()
        mock_response.headers = {"Content-Disposition": "attachment; filename=myfile.bin"}

        result = get_filename_from_response(mock_response, "https://example.com/path")
        assert result == "myfile.bin"

    def test_filename_from_url(self):
        from openwebui_agent_server import get_filename_from_response

        mock_response = Mock()
        mock_response.headers = {}

        result = get_filename_from_response(
            mock_response, "https://cli.github.com/packages/githubcli-archive-keyring.gpg"
        )
        assert result == "githubcli-archive-keyring.gpg"

    def test_filename_fallback_to_timestamp(self):
        from openwebui_agent_server import get_filename_from_response

        mock_response = Mock()
        mock_response.headers = {}

        result = get_filename_from_response(mock_response, "https://example.com/")
        assert result.startswith("download_")
        assert result.endswith(".bin")


class TestFormatFileSize:
    """Tests für format_file_size()"""

    def test_bytes(self):
        from openwebui_agent_server import format_file_size

        assert format_file_size(500) == "500 B"
        assert format_file_size(0) == "0 B"

    def test_kilobytes(self):
        from openwebui_agent_server import format_file_size

        assert format_file_size(2048) == "2.0 KB"
        assert format_file_size(1536) == "1.5 KB"

    def test_megabytes(self):
        from openwebui_agent_server import format_file_size

        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(2621440) == "2.5 MB"


class TestFetchWebpageBinaryHandling:
    """Integration-Tests für fetch_webpage() mit Binary-Content"""

    @patch("openwebui_agent_server.requests.get")
    @patch("openwebui_agent_server.CONFIG")
    def test_binary_download_creates_file(self, mock_config, mock_get):
        """Test: Binary-Content wird als Datei gespeichert"""
        from openwebui_agent_server import fetch_webpage

        # Mock Config
        mock_config.__getitem__ = Mock(return_value={"domain_whitelist": ["example.com"]})

        # Mock Response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "Content-Type": "application/octet-stream",
            "Content-Disposition": 'attachment; filename="test.bin"',
        }
        mock_response.content = b"\x00\x01\x02\x03\x04\x05"  # Binärdaten
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Execute
        result = fetch_webpage("https://example.com/test.bin")

        # Assert
        assert result["status"] == "success"
        assert result["kind"] == "binary"
        assert "binary_path" in result
        assert "message" in result
        assert "🌐 Binary-Download erfolgreich" in result["message"]
        # Kein "content" key bei Binary!
        assert "content" not in result

    @patch("openwebui_agent_server.requests.get")
    @patch("openwebui_agent_server.CONFIG")
    def test_text_content_returns_text(self, mock_config, mock_get):
        """Test: Text-Content wird wie bisher zurückgegeben"""
        from openwebui_agent_server import fetch_webpage

        mock_config.__getitem__ = Mock(return_value={"domain_whitelist": ["example.com"]})

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = "<html><body>Hello World</body></html>"
        mock_response.content = mock_response.text.encode()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_webpage("https://example.com/page.html")

        assert result["status"] == "success"
        assert result["kind"] == "text"
        assert "content" in result
        assert "Hello World" in result["content"]

    @patch("openwebui_agent_server.requests.get")
    @patch("openwebui_agent_server.CONFIG")
    def test_json_content_formatted(self, mock_config, mock_get):
        """Test: JSON-Content wird hübsch formatiert"""
        from openwebui_agent_server import fetch_webpage

        mock_config.__getitem__ = Mock(return_value={"domain_whitelist": ["example.com"]})

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json = Mock(return_value={"key": "value", "number": 42})
        mock_response.content = b'{"key": "value", "number": 42}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_webpage("https://example.com/api.json")

        assert result["status"] == "success"
        assert result["kind"] == "json"
        assert "content" in result
        assert '"key": "value"' in result["content"]


class TestFormatToolResult:
    """Tests für format_tool_result()"""

    def test_format_binary_result(self):
        from openwebui_agent_server import format_tool_result

        tool_result = {
            "status": "success",
            "kind": "binary",
            "message": "🌐 Binary-Download erfolgreich\n\n• URL: https://example.com/file.bin",
        }

        output = format_tool_result(tool_result)

        assert "🌐 Binary-Download erfolgreich" in output
        assert "file.bin" in output or "example.com" in output

    def test_format_error_result(self):
        from openwebui_agent_server import format_tool_result

        tool_result = {"status": "error", "message": "Domain not whitelisted"}

        output = format_tool_result(tool_result)

        assert "❌ Fehler" in output
        assert "Domain not whitelisted" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
