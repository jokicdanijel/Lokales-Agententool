from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    WEBHOOK_SECRET: str = "change-me"
    PUBLIC_BASE_URL: str = "http://localhost:12347"
    HOST: str = "0.0.0.0"
    PORT: int = 12347
    OPENA2_URL: str = "http://localhost:12345"
    KORDP_URL: str = "http://localhost:12346"
    AGENT_ID: str = "opena4_telegram"
    ENVIRONMENT: str = "dev"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
