"""
opena18_Dashboard: Dashboard Extension Agent
Widget management, real-time updates, SSE streaming, custom layouts
GitHub Pattern: coolbits_unified_dashboard_server.py
"""

import asyncio
import json
import logging
import os
import secrets
import sys
import urllib.request
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena18_Dashboard", version="1.0.0", description="Dashboard Extension - Widgets & Real-time Streaming"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12366
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_widgets: dict[str, dict] = {}
_layouts: dict[str, dict] = {}
_subscribers: list[asyncio.Queue] = []

# ============================================================================
# DATA MODELS
# ============================================================================


class WidgetRequest(BaseModel):
    title: str
    type: str  # "metric", "chart", "table", "gauge"
    data_source: str  # "crm", "analytics", "sales"
    refresh_interval: int = 60  # seconds


class LayoutRequest(BaseModel):
    name: str
    widgets: list[str]  # widget IDs
    grid_config: dict[str, Any]  # position and size


class WidgetUpdateRequest(BaseModel):
    title: str | None = None
    type: str | None = None
    data_source: str | None = None
    refresh_interval: int | None = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: str | None):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict):
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena18_dashboard",
            "dst": "opena2",
            "kind": "DASHBOARD_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"},
        }

        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_widget_id() -> str:
    """Generate unique widget ID"""
    return f"WID_{secrets.token_hex(6).upper()}"


def _generate_layout_id() -> str:
    """Generate unique layout ID"""
    return f"LAY_{secrets.token_hex(6).upper()}"


def _generate_widget_data(widget_type: str, data_source: str) -> dict[str, Any]:
    """Generate simulated widget data"""
    data_map = {
        "metric": {"value": 42500, "unit": "USD", "label": f"Metric from {data_source}"},
        "chart": {"type": "bar", "labels": ["A", "B", "C", "D"], "values": [100, 200, 150, 300]},
        "table": {"columns": ["ID", "Name", "Value"], "rows": [["1", "Item A", "100"], ["2", "Item B", "200"]]},
        "gauge": {"value": 75, "min": 0, "max": 100, "label": "Performance"},
    }
    return data_map.get(widget_type, {"message": "Widget type not found"})


# ============================================================================
# SSE EVENT GENERATOR
# ============================================================================


async def _event_generator():
    """Generate SSE events for real-time updates"""
    queue = asyncio.Queue()
    _subscribers.append(queue)

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except TimeoutError:
                yield f"data: {json.dumps({'event': 'keepalive', 'ts': datetime.utcnow().isoformat()})}\n\n"
    finally:
        _subscribers.remove(queue)


async def _publish_event(event: dict):
    """Publish event to all subscribers"""
    for queue in _subscribers:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # Drop event if subscriber is slow


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena18_Dashboard",
        "port": PORT,
        "widgets": len(_widgets),
        "layouts": len(_layouts),
        "subscribers": len(_subscribers),
        "ts": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/widget/create")
async def create_widget(req: WidgetRequest, authorization: str = Header(None)):
    """Create new widget"""
    _validate_token(authorization)

    try:
        widget_id = _generate_widget_id()

        widget_entry = {
            "id": widget_id,
            "title": req.title,
            "type": req.type,
            "data_source": req.data_source,
            "refresh_interval": req.refresh_interval,
            "data": _generate_widget_data(req.type, req.data_source),
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }

        _widgets[widget_id] = widget_entry

        logger.info(f"🎨 Widget created: {widget_id} ({req.type})")

        await _archive(
            {"op": "WIDGET_CREATED", "widget_id": widget_id, "widget_type": req.type, "data_source": req.data_source}
        )

        await _publish_event(
            {"event": "widget_created", "widget_id": widget_id, "title": req.title, "ts": datetime.utcnow().isoformat()}
        )

        return {
            "strict": True,
            "widget_id": widget_id,
            "title": req.title,
            "type": req.type,
            "created": True,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Widget creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/widget/{widget_id}")
async def get_widget(widget_id: str, authorization: str = Header(None)):
    """Get widget details"""
    _validate_token(authorization)

    try:
        if widget_id not in _widgets:
            raise HTTPException(status_code=404, detail=f"Widget {widget_id} not found")

        widget = _widgets[widget_id]
        logger.info(f"🎨 Widget retrieved: {widget_id}")

        return {"strict": True, "widget": widget, "ts": datetime.utcnow().isoformat() + "Z"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Widget retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/layout/save")
async def save_layout(req: LayoutRequest, authorization: str = Header(None)):
    """Save custom dashboard layout"""
    _validate_token(authorization)

    try:
        layout_id = _generate_layout_id()

        layout_entry = {
            "id": layout_id,
            "name": req.name,
            "widgets": req.widgets,
            "grid_config": req.grid_config,
            "created_at": datetime.utcnow().isoformat(),
            "saved_at": datetime.utcnow().isoformat(),
        }

        _layouts[layout_id] = layout_entry

        logger.info(f"📐 Layout saved: {layout_id} ({req.name}) with {len(req.widgets)} widgets")

        await _archive(
            {"op": "LAYOUT_SAVED", "layout_id": layout_id, "layout_name": req.name, "widget_count": len(req.widgets)}
        )

        await _publish_event(
            {
                "event": "layout_saved",
                "layout_id": layout_id,
                "layout_name": req.name,
                "ts": datetime.utcnow().isoformat(),
            }
        )

        return {
            "strict": True,
            "layout_id": layout_id,
            "name": req.name,
            "widget_count": len(req.widgets),
            "saved": True,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Layout save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/layout/{layout_id}")
async def get_layout(layout_id: str, authorization: str = Header(None)):
    """Get layout details"""
    _validate_token(authorization)

    try:
        if layout_id not in _layouts:
            raise HTTPException(status_code=404, detail=f"Layout {layout_id} not found")

        layout = _layouts[layout_id]
        logger.info(f"📐 Layout retrieved: {layout_id}")

        return {"strict": True, "layout": layout, "ts": datetime.utcnow().isoformat() + "Z"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Layout retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh/realtime")
async def refresh_realtime(widget_ids: list[str], authorization: str = Header(None)):
    """Trigger real-time refresh of widgets"""
    _validate_token(authorization)

    try:
        updated_widgets = []

        for widget_id in widget_ids:
            if widget_id in _widgets:
                widget = _widgets[widget_id]
                widget["last_updated"] = datetime.utcnow().isoformat()
                widget["data"] = _generate_widget_data(widget["type"], widget["data_source"])
                updated_widgets.append(widget_id)

                await _publish_event(
                    {
                        "event": "widget_updated",
                        "widget_id": widget_id,
                        "new_data": widget["data"],
                        "ts": datetime.utcnow().isoformat(),
                    }
                )

        logger.info(f"🔄 Real-time refresh: {len(updated_widgets)} widgets")

        await _archive({"op": "REALTIME_REFRESH", "widget_count": len(updated_widgets), "widget_ids": updated_widgets})

        return {
            "strict": True,
            "updated_widgets": updated_widgets,
            "count": len(updated_widgets),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Real-time refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/stream")
async def data_stream(authorization: str = Header(None)):
    """Server-Sent Events stream for real-time updates"""
    _validate_token(authorization)

    logger.info("📡 SSE stream started")

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)

    return {
        "service": "opena18_Dashboard",
        "version": "1.0.0",
        "port": PORT,
        "widgets": len(_widgets),
        "layouts": len(_layouts),
        "sse_subscribers": len(_subscribers),
        "endpoints": 7,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting opena18_Dashboard on port {PORT}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
