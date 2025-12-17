from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.session import get_db
from app.db.models import Bot
from app.config import settings
import requests
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin_key(x_admin_key: str = Header(None)):
    """Dependency: Verify admin key"""
    if x_admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


@router.post("/register-bot")
async def register_bot(
    bot_key: str,
    token: str,
    bot_name: str = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    """Register new bot (admin-only)"""
    try:
        # Get bot info from Telegram
        resp = requests.get(
            f"https://api.telegram.org/bot{token}/getMe",
            timeout=settings.telegram_api_timeout,
        )
        data = resp.json()
        
        if not data.get("ok"):
            raise HTTPException(status_code=400, detail="Invalid token")
        
        bot_info = data.get("result", {})
        bot_id = str(bot_info.get("id", ""))
        bot_name = bot_name or bot_info.get("username", "unknown")
        
        # Check if exists
        stmt = select(Bot).where(Bot.bot_key == bot_key)
        existing = (await db.execute(stmt)).scalars().first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Bot already registered")
        
        # Create bot
        bot = Bot(
            bot_key=bot_key,
            bot_id=bot_id,
            bot_name=bot_name,
            token=token,
        )
        db.add(bot)
        await db.commit()
        await db.refresh(bot)
        
        logger.info(f"Bot registered: {bot_key}")
        return {"status": "ok", "bot_key": bot_key, "bot_id": bot_id}
    
    except Exception as e:
        logger.error(f"Register bot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-webhooks")
async def set_webhooks(
    webhook_base_url: str,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    """Set webhooks for all bots (admin-only)"""
    stmt = select(Bot)
    bots = (await db.execute(stmt)).scalars().all()
    
    results = []
    
    for bot in bots:
        webhook_url = f"{webhook_base_url}/telegram/webhook/{bot.bot_key}"
        
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{bot.token}/setWebhook",
                json={
                    "url": webhook_url,
                    "secret_token": settings.webhook_secret,
                },
                timeout=settings.telegram_api_timeout,
            )
            
            if resp.json().get("ok"):
                bot.webhook_url = webhook_url
                bot.webhook_registered = True
                results.append({"bot_key": bot.bot_key, "status": "ok"})
            else:
                results.append({"bot_key": bot.bot_key, "status": "error"})
        
        except Exception as e:
            logger.error(f"Webhook error for {bot.bot_key}: {e}")
            results.append({"bot_key": bot.bot_key, "status": "error"})
    
    await db.commit()
    return {"webhooks_set": results}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "telegram_multi"}
