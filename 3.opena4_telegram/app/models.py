from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    edited_message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

class Safepoint(BaseModel):
    agent_id: str
    direction: str
    kind: str
    payload: Dict[str, Any]
    meta: Dict[str, Any] = Field(default_factory=dict)

class OutboxRequest(BaseModel):
    chat_id: int
    text: str
    parse_mode: Optional[str] = None
    reply_to_message_id: Optional[int] = None
