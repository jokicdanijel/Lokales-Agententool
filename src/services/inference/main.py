#!/usr/bin/env python3
"""
Inference Service — llama-stack + Ollama Integration
- Central inference gateway for multi-model support
- Routes: /models, /completions, /health
- Port: 12348 (infer)
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from socket import gethostname

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# ────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────

SERVICE_NAME = "inference"
PROGRAM_TARGET = "infer"
PORT = int(os.getenv("INFERENCE_PORT", "12348"))
COORDINATOR_PORT = 12344
ARCHIVP_PORT = 12345
OLLAMA_ENDPOINT = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama2"

# Stats
STATS = {
    "completions_requested": 0,
    "tokens_processed": 0,
    "latency_p50": 0.0,
    "latency_p99": 0.0,
    "queue_depth": 0,
    "errors": 0,
}

LATENCIES = []  # Track latencies for percentiles


# ────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ────────────────────────────────────────────────────────────────────────

class CompletionRequest(BaseModel):
    """Inference request."""
    model: str = DEFAULT_MODEL
    prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = False


class CompletionResponse(BaseModel):
    """Inference response."""
    ok: bool
    model: str
    completion: str
    tokens: int
    latency_ms: float
    strict: bool = True


class ModelInfo(BaseModel):
    """Model metadata."""
    id: str
    name: str
    provider: str
    enabled: bool = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    program_target: str
    ollama_present: bool
    default_model: str
    models: List[str]
    stats: Dict[str, Any]


# ────────────────────────────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────────────────────────────

def _hostname() -> str:
    """Get hostname."""
    try:
        return gethostname()
    except Exception:
        return "unknown"


def _now() -> str:
    """Current timestamp (ISO 8601)."""
    return datetime.utcnow().isoformat() + "Z"


async def _check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{OLLAMA_ENDPOINT}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def _get_available_models() -> List[str]:
    """Fetch available models from Ollama."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_ENDPOINT}/api/tags")
            if r.status_code == 200:
                data = r.json()
                return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return [DEFAULT_MODEL]


async def _inference_ollama(
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float
) -> tuple[str, int, float]:
    """Call Ollama inference API."""
    url = f"{OLLAMA_ENDPOINT}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }
    
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            
        latency = time.time() - start_time
        data = r.json()
        completion = data.get("response", "")
        tokens = len(completion.split())
        
        STATS["tokens_processed"] += tokens
        LATENCIES.append(latency)
        
        # Update percentiles
        if len(LATENCIES) >= 1:
            sorted_latencies = sorted(LATENCIES)
            STATS["latency_p50"] = sorted_latencies[len(LATENCIES) // 2]
        if len(LATENCIES) >= 100:
            sorted_latencies = sorted(LATENCIES)
            STATS["latency_p99"] = sorted_latencies[int(len(LATENCIES) * 0.99)]
        
        return completion, tokens, latency
    
    except Exception as e:
        STATS["errors"] += 1
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


async def _store_safepoint(kind: str, body: Dict[str, Any]) -> None:
    """Delegate safepoint storage to OpenA2."""
    url = f"http://127.0.0.1:{ARCHIVP_PORT}/store/archivp"
    payload = {
        "src": PROGRAM_TARGET,
        "dst": "archivp",
        "kind": kind,
        "body": body,
        "strict": True,
        "ts": _now()
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
    except Exception as e:
        print(f"⚠️  Safepoint storage failed: {e}")
        STATS["errors"] += 1


# ────────────────────────────────────────────────────────────────────────
# FastAPI App
# ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"Inference Gateway — {PROGRAM_TARGET.upper()}",
    description="Multi-model inference service (llama-stack + Ollama)",
    version="1.0.0"
)


# ────────────────────────────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> HealthResponse:
    """Health check."""
    ollama_present = await _check_ollama()
    available_models = await _get_available_models() if ollama_present else [DEFAULT_MODEL]
    
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        program_target=PROGRAM_TARGET,
        ollama_present=ollama_present,
        default_model=DEFAULT_MODEL,
        models=available_models,
        stats=STATS,
    )


@app.get("/models")
async def list_models() -> Dict[str, Any]:
    """List available models."""
    models = await _get_available_models()
    
    await _store_safepoint("MODEL_LIST", {
        "models_count": len(models),
        "models": models,
    })
    
    return {
        "ok": True,
        "models": models,
        "default": DEFAULT_MODEL,
        "provider": "ollama",
    }


@app.post("/completions")
async def completions(req: CompletionRequest) -> CompletionResponse:
    """Generate completion via Ollama."""
    STATS["completions_requested"] += 1
    
    # Build prompt from messages or direct prompt
    if req.messages:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in req.messages])
    else:
        prompt = req.prompt or "Hello"
    
    # Call Ollama
    completion, tokens, latency = await _inference_ollama(
        model=req.model or DEFAULT_MODEL,
        prompt=prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature
    )
    
    # Store safepoint
    await _store_safepoint("COMPLETION", {
        "model": req.model,
        "prompt_tokens": len(prompt.split()),
        "completion_tokens": tokens,
        "latency_ms": latency * 1000,
    })
    
    return CompletionResponse(
        ok=True,
        model=req.model or DEFAULT_MODEL,
        completion=completion,
        tokens=tokens,
        latency_ms=latency * 1000,
    )


@app.post("/chat/completions")
async def chat_completions(req: CompletionRequest) -> Dict[str, Any]:
    """OpenAI-compatible chat completions endpoint."""
    STATS["completions_requested"] += 1
    
    # Build prompt from messages
    if req.messages:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in req.messages])
    else:
        prompt = req.prompt or "You are a helpful assistant."
    
    # Call Ollama
    completion, tokens, latency = await _inference_ollama(
        model=req.model or DEFAULT_MODEL,
        prompt=prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature
    )
    
    # Store safepoint
    await _store_safepoint("CHAT_COMPLETION", {
        "model": req.model,
        "messages_count": len(req.messages) if req.messages else 0,
        "completion_tokens": tokens,
        "latency_ms": latency * 1000,
    })
    
    return {
        "ok": True,
        "model": req.model or DEFAULT_MODEL,
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": completion
                }
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": tokens,
            "total_tokens": len(prompt.split()) + tokens
        },
        "latency_ms": latency * 1000,
    }


@app.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get current statistics."""
    return {
        "ok": True,
        "stats": STATS,
        "latencies_tracked": len(LATENCIES),
    }


# ────────────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=PORT,
        reload=False,
        access_log=False,
    )
