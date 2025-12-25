import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.commands.registry import CommandRegistry
from app.config import settings
from app.db.models import Bot, Chat, Update
from app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook/{bot_key}")
async def webhook_handler(
    bot_key: str,
    update_data: dict,
    x_telegram_bot_api_secret_token: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Telegram webhook receiver (POST)

    Security:
    - Validates X-Telegram-Bot-Api-Secret-Token header
    - Deduplicates updates via (bot_id, update_id) constraint
    """

    # Validate webhook secret
    if x_telegram_bot_api_secret_token != settings.webhook_secret:
        logger.warning(f"Webhook secret mismatch for {bot_key}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Get bot
    stmt = select(Bot).where(Bot.bot_key == bot_key)
    bot = (await db.execute(stmt)).scalars().first()

    if not bot:
        logger.error(f"Bot not found: {bot_key}")
        raise HTTPException(status_code=404, detail="Bot not found")

    update_id = str(update_data.get("update_id", ""))

    try:
        # Verify/create chat
        message = update_data.get("message", {})
        chat_data = message.get("chat", {})
        chat_id = str(chat_data.get("id", "unknown"))

        stmt = select(Chat).where((Chat.bot_id == bot.id) & (Chat.chat_id == chat_id))
        chat = (await db.execute(stmt)).scalars().first()

        if not chat:
            chat = Chat(
                bot_id=bot.id,
                chat_id=chat_id,
                chat_type=chat_data.get("type", "private"),
                user_first_name=chat_data.get("first_name"),
                user_last_name=chat_data.get("last_name"),
                username=chat_data.get("username"),
            )
            db.add(chat)
            await db.flush()  # Get chat.id

        # Create/check update (dedup via constraint)
        update_obj = Update(
            bot_id=bot.id,
            chat_id=chat.id,
            update_id=update_id,
            message_type=message.get("text") and "text" or "other",
            message_text=message.get("text"),
            raw_update=json.dumps(update_data),
            processed=False,
        )
        db.add(update_obj)
        await db.commit()

        # Dispatch to handler
        registry = CommandRegistry(bot_key, db, bot)
        await registry.dispatch(update_data, message)

        # Mark as processed
        update_obj.processed = True
        await db.commit()

        return {"ok": True, "update_id": update_id}

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
