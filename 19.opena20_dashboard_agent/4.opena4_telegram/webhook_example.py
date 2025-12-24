#!/usr/bin/env python3
"""
Telegram Webhook Example
========================
Alternative to polling mode - use webhooks for production

Usage:
1. Set up HTTPS domain (required for webhooks)
2. Configure webhook: python webhook_example.py --setup
3. Run: python webhook_example.py
"""

import asyncio
import os

from fastapi import FastAPI, Request
from telegram import Bot, Update

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://yourdomain.com/telegram/webhook")
WEBHOOK_PATH = "/telegram/webhook"
PORT = 12346

# Create FastAPI app for webhook
webhook_app = FastAPI()
telegram_app = None


async def setup_webhook():
    """Setup webhook with Telegram"""
    bot = Bot(TELEGRAM_BOT_TOKEN)
    await bot.set_webhook(url=WEBHOOK_URL)
    info = await bot.get_webhook_info()
    print(f"✓ Webhook set: {info.url}")
    print(f"  Pending updates: {info.pending_update_count}")


async def remove_webhook():
    """Remove webhook (switch back to polling)"""
    bot = Bot(TELEGRAM_BOT_TOKEN)
    await bot.delete_webhook()
    print("✓ Webhook removed")


@webhook_app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Handle incoming webhook updates from Telegram"""
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


@webhook_app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "agent": "opena4", "mode": "webhook"}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        # Setup webhook
        asyncio.run(setup_webhook())
    elif len(sys.argv) > 1 and sys.argv[1] == "--remove":
        # Remove webhook
        asyncio.run(remove_webhook())
    else:
        # Run webhook server
        import uvicorn

        print(f"🚀 Starting webhook server on port {PORT}")
        print(f"📡 Webhook path: {WEBHOOK_PATH}")
        uvicorn.run(webhook_app, host="0.0.0.0", port=PORT)
