"""
src/services/openwebui/client_openwebui.py
Client library for OpenWebUI service (opena3)
"""
from __future__ import annotations

import httpx

BASE = "http://127.0.0.1:12346"


def ping() -> dict:
    """Call /openwebui/ping."""
    r = httpx.get(f"{BASE}/openwebui/ping", timeout=3.0)
    r.raise_for_status()
    return r.json()


def call_prompt(text: str) -> dict:
    """Call /openwebui/call with prompt action."""
    payload = {
        "action": "prompt",
        "data": {"text": text}
    }
    r = httpx.post(f"{BASE}/openwebui/call", json=payload, timeout=5.0)
    r.raise_for_status()
    return r.json()
