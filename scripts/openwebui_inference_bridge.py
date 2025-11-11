#!/usr/bin/env python3
"""
OpenWebUI ↔ Inference Bridge
- Routes OpenWebUI API requests to Inference Service
- /api/models → /models (Port 12348)
- /api/chat/completions → /chat/completions (Port 12348)
"""

import asyncio
import httpx
from typing import Any, Dict

INFERENCE_SERVICE = "http://127.0.0.1:12348"
OPENWEBUI_PORT = 3000


async def bridge_models() -> Dict[str, Any]:
    """Bridge /api/models from OpenWebUI to Inference Service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{INFERENCE_SERVICE}/models")
            r.raise_for_status()
            data = r.json()
            
            # Transform to OpenWebUI format
            models_list = data.get("models", [])
            return {
                "models": [
                    {
                        "id": m,
                        "object": "model",
                        "created": 0,
                        "owned_by": "inference",
                        "permission": [],
                        "root": m,
                        "parent": None
                    }
                    for m in models_list
                ]
            }
    except Exception as e:
        print(f"❌ Bridge models failed: {e}")
        return {"models": [], "error": str(e)}


async def bridge_completions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Bridge /api/chat/completions from OpenWebUI to Inference Service."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{INFERENCE_SERVICE}/chat/completions",
                json=payload,
            )
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"❌ Bridge completions failed: {e}")
        return {"error": str(e), "ok": False}


async def test_bridge():
    """Test the bridge."""
    print("=" * 80)
    print("🌉 OpenWebUI ↔ Inference Bridge Test")
    print("=" * 80)
    
    # Test models
    print("\n📋 Testing /models bridge:")
    models_response = await bridge_models()
    print(f"  Models available: {len(models_response.get('models', []))}")
    for model in models_response.get("models", [])[:3]:
        print(f"    - {model.get('id')}")
    
    # Test completions
    print("\n💬 Testing /chat/completions bridge:")
    completion_response = await bridge_completions({
        "model": "llama2",
        "messages": [{"role": "user", "content": "What is 2+2?"}],
        "max_tokens": 50,
    })
    
    if "choices" in completion_response:
        content = completion_response["choices"][0]["message"]["content"]
        print(f"  Response: {content[:100]}...")
        print(f"  Latency: {completion_response.get('latency_ms', 'N/A')}ms")
    else:
        print(f"  Error: {completion_response.get('error', 'Unknown')}")
    
    print("\n" + "=" * 80)
    print("✅ Bridge test complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_bridge())
