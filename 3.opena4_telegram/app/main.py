from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import httpx

from .config import get_settings, Settings
from .models import TelegramUpdate, OutboxRequest, Safepoint
from .archiv_client import write_safepoint

app = FastAPI(title="Agent 4 - Telegram Agent", version="1.0.0")

UPDATES_TOTAL = Counter("telegram_updates_total", "Total Telegram updates received")
OUTBOX_TOTAL = Counter("telegram_outbox_total", "Total Telegram messages sent")

def tg_api_base(settings: Settings) -> str:
    return f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

@app.get("/health")
async def health(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "agent": settings.AGENT_ID, "env": settings.ENVIRONMENT}

@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

@app.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate, secret: str = Query(""), settings: Settings = Depends(get_settings)):
    if secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="invalid secret")
    UPDATES_TOTAL.inc()
    
    sp = Safepoint(
        agent_id=settings.AGENT_ID,
        direction="in",
        kind="telegram.update",
        payload=update.model_dump(),
        meta={},
    )
    await write_safepoint(sp)
    
    chat_id = None
    if update.message and "chat" in update.message:
        chat_id = update.message["chat"]["id"]
    if chat_id is not None:
        await send_message(OutboxRequest(chat_id=chat_id, text="✅ Empfang bestätigt."), settings)
    
    return {"ok": True}

@app.post("/inbox")
async def inbox(update: TelegramUpdate, settings: Settings = Depends(get_settings)):
    UPDATES_TOTAL.inc()
    sp = Safepoint(
        agent_id=settings.AGENT_ID,
        direction="in",
        kind="telegram.update",
        payload=update.model_dump(),
        meta={"source": "local"},
    )
    await write_safepoint(sp)
    return {"status": "archived"}

@app.post("/outbox")
async def outbox(req: OutboxRequest, settings: Settings = Depends(get_settings)):
    OUTBOX_TOTAL.inc()
    await send_message(req, settings)
    sp = Safepoint(
        agent_id=settings.AGENT_ID,
        direction="out",
        kind="telegram.message",
        payload={"chat_id": req.chat_id, "text": req.text},
        meta={},
    )
    await write_safepoint(sp)
    return {"status": "sent"}

async def send_message(req: OutboxRequest, settings: Settings):
    url = f"{tg_api_base(settings)}/sendMessage"
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, json=data)
        if r.status_code != 200 or not r.json().get("ok"):
            raise HTTPException(status_code=502, detail=f"telegram error: {r.text}")
