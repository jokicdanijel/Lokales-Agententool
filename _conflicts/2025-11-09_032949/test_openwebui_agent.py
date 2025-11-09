#!/usr/bin/env python3
"""Pytest für OpenWebUI-Agent"""

import json
import urllib.request
import pytest


BASE = "http://127.0.0.1:12347"


def test_health():
    """Teste Health-Endpunkt des OpenWebUI-Agenten"""
    try:
        with urllib.request.urlopen(f"{BASE}/health", timeout=5) as r:
            result = json.loads(r.read().decode())
            assert result.get("service") == "opena3"
            assert result.get("status") == "ok"
    except urllib.error.URLError:
        pytest.skip("OpenWebUI Agent nicht erreichbar")


def test_command():
    """Teste Command-Endpunkt mit Beispiel-Prompt"""
    payload = {
        "prompt": "Hello, how are you?",
        "context": {}
    }
    try:
        req = urllib.request.Request(
            f"{BASE}/command",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode())
            assert "response" in result
            assert "ts" in result
    except urllib.error.HTTPError as e:
        if e.code == 502:
            pytest.skip("OpenWebUI nicht erreichbar (502)")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
