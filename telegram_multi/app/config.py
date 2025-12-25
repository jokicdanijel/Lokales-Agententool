import json

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Telegram Multi-Bot Settings (strict mode)"""

    api_port: int = 8000
    api_host: str = "0.0.0.0"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://telegram_user:telegram_pass@postgres:5432/telegram_multi_db"
    redis_url: str = "redis://redis:6379"

    bearer_token: str = "default-bearer-token"
    admin_key: str = "admin-secret"
    webhook_secret: str = "webhook-secret"

    bot_tokens_mapping: str = '{"browser_opena6_bot": "TOKEN_1", "open2tele_bot": "TOKEN_2"}'
    telegram_api_timeout: int = 30

    log_level: str = "INFO"
    log_file: str = "logs/telegram_multi.log"

    class Config:
        env_file = ".env"
        extra = "forbid"  # Strict: keine unbekannten Felder

    @property
    def bots_dict(self) -> dict[str, str]:
        """Parse BOT_TOKENS_MAPPING JSON string"""
        try:
            return json.loads(self.bot_tokens_mapping)
        except json.JSONDecodeError:
            return {}


settings = Settings()
