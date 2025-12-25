from typing import Any

from pydantic import BaseModel, Field


class TelegramUpdate(BaseModel):
    update_id: int
    message: dict[str, Any] | None = None
    edited_message: dict[str, Any] | None = None
    callback_query: dict[str, Any] | None = None


class Safepoint(BaseModel):
    agent_id: str
    direction: str
    kind: str
    payload: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)


class OutboxRequest(BaseModel):
    chat_id: int
    text: str
    parse_mode: str | None = None
    reply_to_message_id: int | None = None
