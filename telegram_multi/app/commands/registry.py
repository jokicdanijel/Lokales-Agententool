"""
CommandRegistry: Handle Telegram commands per bot.
Extensible handler pattern.
"""

import logging
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Bot, CommandLog

logger = logging.getLogger(__name__)


class BaseBotHandler(ABC):
    """Base handler for bot commands"""

    def __init__(self, bot_key: str, db: AsyncSession, bot_model: Bot):
        self.bot_key = bot_key
        self.db = db
        self.bot_model = bot_model

    async def handle_command(self, command: str, message: dict):
        """Route command to handler"""
        if command == "/start":
            return await self.cmd_start(message)
        elif command == "/help":
            return await self.cmd_help(message)
        elif command == "/status":
            return await self.cmd_status(message)
        else:
            return await self.cmd_unknown(message)

    async def handle_text(self, text: str, message: dict):
        """Handle free-form text (bot-specific)"""
        response = f"Echo: {text}"
        await self.log_command("text", response, "success")
        return response

    @abstractmethod
    async def cmd_start(self, message: dict):
        """Override: Handle /start"""

    @abstractmethod
    async def cmd_help(self, message: dict):
        """Override: Handle /help"""

    async def cmd_status(self, message: dict):
        """Default: Handle /status"""
        response = f"✅ Bot {self.bot_key} is online"
        await self.log_command("/status", response, "success")
        return response

    async def cmd_unknown(self, message: dict):
        """Default: Handle unknown command"""
        response = "Unknown command. Try /help"
        await self.log_command("unknown", response, "error")
        return response

    async def log_command(self, command: str, response: str, status: str):
        """Log command execution"""
        chat_id = str(message.get("chat", {}).get("id", "unknown"))
        log = CommandLog(
            bot_id=self.bot_model.id,
            chat_id=chat_id,
            command=command,
            response=response,
            status=status,
        )
        self.db.add(log)
        await self.db.commit()


class BrowserBotHandler(BaseBotHandler):
    """Handler for browser_opena6_bot"""

    async def cmd_start(self, message: dict):
        response = "🌐 Browser Agent Ready! /help for commands"
        await self.log_command("/start", response, "success")
        return response

    async def cmd_help(self, message: dict):
        response = """/help:
/navigate <url> - Open URL
/screenshot - Take screenshot
/extract <selector> - Extract data
/status - Bot status"""
        await self.log_command("/help", response, "success")
        return response


class Open2TeleHandler(BaseBotHandler):
    """Handler for open2tele_bot"""

    async def cmd_start(self, message: dict):
        response = "📞 Open2Tele Ready! /help for commands"
        await self.log_command("/start", response, "success")
        return response

    async def cmd_help(self, message: dict):
        response = """/help:
/forward - Forward to group
/notify - Send notification
/status - Bot status"""
        await self.log_command("/help", response, "success")
        return response


class CommandRegistry:
    """Factory for bot handlers"""

    HANDLERS = {
        "browser_opena6_bot": BrowserBotHandler,
        "open2tele_bot": Open2TeleHandler,
    }

    def __init__(self, bot_key: str, db: AsyncSession, bot_model: Bot):
        handler_class = self.HANDLERS.get(bot_key, BaseBotHandler)
        self.handler = handler_class(bot_key, db, bot_model)

    async def dispatch(self, update: dict, message: dict):
        """Dispatch to correct handler"""
        text = message.get("text", "")

        if text.startswith("/"):
            command = text.split()[0]
            return await self.handler.handle_command(command, message)
        else:
            return await self.handler.handle_text(text, message)
