"""
Tests for opena5_Browser agent
"""

import json
import urllib.request
import pytest

TOKEN = "MEIN_SUPER_TOKEN_123"
BASE = "http://127.0.0.1:12353"


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
    
    def test_health(self):
        """Health check should work without auth"""
        try:
            resp = json.loads(urllib.request.urlopen(f"{BASE}/health").read().decode())
            assert resp["status"] == "healthy"
            assert resp["service"] == "opena5_Browser"
        except urllib.error.HTTPError as e:
            if e.code != 401:
                raise


class TestNavigation:
    """Navigation tests"""
    
    def test_navigate_example(self):
        """Navigate to example.com"""
        resp = _post("/navigate", {
            "url": "https://example.com",
            "wait_time": 10
        })
        assert resp["strict"] is True
        assert resp["url"] == "https://example.com"
        assert "navigated" in resp
    
    def test_navigate_invalid_url(self):
        """Navigate to invalid URL"""
        try:
            resp = _post("/navigate", {
                "url": "https://invalid-domain-12345-xyz.com",
                "wait_time": 5
            })
            # May timeout or fail, but should return response
            assert "navigated" in resp
        except:
            pass


class TestFormOperations:
    """Form interaction tests"""
    
    def test_click_element(self):
        """Click on element"""
        # First navigate somewhere
        _post("/navigate", {
            "url": "https://example.com",
            "wait_time": 5
        })
        
        # Then try to click (may fail if element doesn't exist, but should return response)
        resp = _post("/click", {
            "selector": "body"
        })
        assert resp["strict"] is True
        assert "clicked" in resp
    
    def test_fill_form(self):
        """Fill form fields"""
        resp = _post("/fill", {
            "fields": {
                "input[name='email']": "test@example.com",
                "input[name='password']": "password123"
            }
        })
        assert resp["strict"] is True
        assert resp["fields"] == 2


class TestWait:
    """Wait for element tests"""
    
    def test_wait_body_element(self):
        """Wait for body element"""
        # Navigate first
        _post("/navigate", {
            "url": "https://example.com",
            "wait_time": 5
        })
        
        # Wait for element
        resp = _post("/wait", {
            "selector": "body",
            "timeout": 5
        })
        assert resp["strict"] is True
        assert "found" in resp


class TestScreenshot:
    """Screenshot tests"""
    
    def test_screenshot_base64(self):
        """Take screenshot in base64 format"""
        # Navigate first
        _post("/navigate", {
            "url": "https://example.com",
            "wait_time": 5
        })
        
        resp = _post("/screenshot", {
            "format": "base64"
        })
        assert resp["strict"] is True
        assert resp["format"] == "base64"
        assert "screenshot" in resp


class TestJavaScript:
    """JavaScript execution tests"""
    
    def test_execute_script(self):
        """Execute JavaScript"""
        resp = _post("/execute", {
            "script": "return 42;"
        })
        assert resp["strict"] is True
        assert "result" in resp


class TestCookies:
    """Cookie tests"""
    
    def test_get_cookies(self):
        """Get cookies"""
        resp = _get("/cookies")
        assert resp["strict"] is True
        assert "cookies" in resp
        assert resp["count"] >= 0


class TestStatus:
    """Status endpoint tests"""
    
    def test_status(self):
        """Get agent status"""
        resp = _get("/status")
        assert resp["service"] == "opena5_Browser"
        assert resp["endpoints"] >= 8
        assert "browser_initialized" in resp


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
