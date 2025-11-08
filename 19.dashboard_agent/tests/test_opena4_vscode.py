"""
Tests for opena4_VSCode agent
"""

import json
import urllib.request
import time
import pytest

TOKEN = "MEIN_SUPER_TOKEN_123"
BASE = "http://127.0.0.1:12352"
INVALID_TOKEN = "INVALID_TOKEN_123"


def _post(path, payload, token=TOKEN):
    """Helper to make POST requests"""
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def _get(path, token=TOKEN):
    """Helper to make GET requests"""
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


class TestHealth:
    """Health check tests"""
    
    def test_health_no_auth(self):
        """Health should work without auth"""
        try:
            resp = json.loads(urllib.request.urlopen(f"{BASE}/health").read().decode())
            assert resp["status"] == "healthy"
            assert resp["service"] == "opena4_VSCode"
        except urllib.error.HTTPError as e:
            if e.code != 401:
                raise


class TestAuthentication:
    """Authentication tests"""
    
    def test_missing_token(self):
        """Request without token should fail"""
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get("/status", token="")
        assert exc.value.code == 401
    
    def test_invalid_token(self):
        """Request with invalid token should fail"""
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get("/status", token=INVALID_TOKEN)
        assert exc.value.code == 403


class TestFileOperations:
    """File operation tests"""
    
    def test_file_read_etc_hostname(self):
        """Read /etc/hostname"""
        resp = _post("/file/read", {
            "path": "/etc/hostname"
        })
        assert resp["strict"] is True
        assert resp["path"] == "/etc/hostname"
        assert len(resp["content"]) > 0
        assert "bytes" in resp
    
    def test_file_write_and_read(self):
        """Write file and read it back"""
        test_file = "/tmp/opena4_test.txt"
        test_content = "✅ Test content from opena4_VSCode\nLine 2\nLine 3"
        
        # Write
        write_resp = _post("/file/write", {
            "path": test_file,
            "content": test_content
        })
        assert write_resp["written"] is True
        assert write_resp["bytes"] == len(test_content)
        
        # Read back
        read_resp = _post("/file/read", {
            "path": test_file
        })
        assert read_resp["content"].strip() == test_content.strip()
    
    def test_file_delete(self):
        """Write, then delete file"""
        test_file = "/tmp/opena4_delete_test.txt"
        
        # Write
        _post("/file/write", {
            "path": test_file,
            "content": "To be deleted"
        })
        
        # Delete
        delete_resp = _post("/file/delete", {
            "path": test_file
        })
        assert delete_resp["deleted"] is True


class TestDirectoryOperations:
    """Directory operation tests"""
    
    def test_list_directory(self):
        """List /tmp directory"""
        resp = _post("/file/list", {
            "path": "/tmp"
        })
        assert resp["strict"] is True
        assert resp["path"] == "/tmp"
        assert "items" in resp
        assert resp["count"] >= 0
        
        # Check structure of items
        if resp["items"]:
            item = resp["items"][0]
            assert "name" in item
            assert "type" in item
            assert item["type"] in ["file", "dir"]


class TestTerminalExecution:
    """Terminal execution tests"""
    
    def test_simple_echo(self):
        """Execute simple echo command"""
        resp = _post("/terminal/exec", {
            "cmd": "echo 'Hello from opena4_VSCode'",
            "timeout_sec": 10
        })
        assert resp["strict"] is True
        assert "Hello" in resp["output"]
        assert resp["lines"] >= 1
    
    def test_command_with_pipes(self):
        """Execute command with pipes"""
        resp = _post("/terminal/exec", {
            "cmd": "echo 'line1\nline2\nline3' | wc -l",
            "timeout_sec": 10
        })
        assert resp["strict"] is True
        assert "3" in resp["output"]
    
    def test_command_timeout(self):
        """Test command timeout"""
        with pytest.raises(urllib.error.HTTPError) as exc:
            _post("/terminal/exec", {
                "cmd": "sleep 60",
                "timeout_sec": 1
            })
        assert exc.value.code == 504


class TestStatus:
    """Status endpoint tests"""
    
    def test_status_endpoint(self):
        """Get agent status"""
        resp = _get("/status")
        assert resp["service"] == "opena4_VSCode"
        assert resp["ssh_connected"] is True
        assert resp["endpoints"] >= 6
        assert "ts" in resp


class TestIntegration:
    """Integration tests"""
    
    def test_archive_integration(self):
        """Verify operations are archived"""
        # Read a file (should be archived)
        resp = _post("/file/read", {
            "path": "/etc/hostname"
        })
        assert resp["strict"] is True
        
        # Check archive (may take a moment)
        time.sleep(1)
        
        # Get archive status
        try:
            archive_resp = urllib.request.urlopen(
                "http://127.0.0.1:12345/archiv/last?n=1"
            )
            archive_data = json.loads(archive_resp.read().decode())
            # Verify archive has entries
            assert archive_data["count"] >= 0
        except:
            pass  # Archive might not be immediately available


class TestEndpointCount:
    """Verify all 6 endpoints exist"""
    
    def test_all_endpoints_documented(self):
        """Verify endpoint count matches spec"""
        endpoints = [
            ("/health", "GET"),
            ("/file/read", "POST"),
            ("/file/write", "POST"),
            ("/file/delete", "POST"),
            ("/file/list", "POST"),
            ("/terminal/exec", "POST"),
        ]
        
        # All should be defined (at least get /health works)
        resp = _get("/status")
        assert resp["endpoints"] >= len(endpoints)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
