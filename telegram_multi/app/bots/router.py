"""
BotRouter: Central dispatcher for multi-bot orchestration.
Routes commands to correct handler based on bot_key.
"""


class BotRouter:
    """Routes updates to correct bot handler"""
    
    @staticmethod
    async def dispatch(bot_key: str, update: dict, handler_registry):
        """
        Dispatch update to correct handler
        
        Args:
            bot_key: e.g., "browser_opena6_bot"
            update: Telegram update dict
            handler_registry: CommandRegistry instance
        
        Returns:
            Response from handler
        """
        message = update.get("message", {})
        text = message.get("text", "")
        
        # Dispatch based on bot_key + message content
        if text.startswith("/"):
            command = text.split()[0]  # e.g., "/start"
            return await handler_registry.handle_command(command, message)
        else:
            return await handler_registry.handle_text(text, message)
