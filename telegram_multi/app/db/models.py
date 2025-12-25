from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class Bot(SQLModel, table=True):
    """Telegram Bot Registration"""

    __tablename__ = "bots"

    id: int | None = Field(default=None, primary_key=True)
    bot_key: str = Field(index=True, unique=True)  # e.g., "browser_opena6_bot"
    bot_id: str = Field(index=True)  # Numeric bot ID from Telegram
    bot_name: str
    token: str
    webhook_url: str | None = None
    webhook_registered: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    chats: list["Chat"] = Relationship(back_populates="bot")
    updates: list["Update"] = Relationship(back_populates="bot")


class Chat(SQLModel, table=True):
    """Telegram Chat (user/group)"""

    __tablename__ = "chats"

    id: int | None = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bots.id")
    chat_id: str = Field(index=True)
    chat_type: str  # "private", "group", "supergroup", "channel"
    user_first_name: str | None = None
    user_last_name: str | None = None
    username: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    bot: Bot = Relationship(back_populates="chats")
    updates: list["Update"] = Relationship(back_populates="chat")


class Update(SQLModel, table=True):
    """Telegram Webhook Update (dedup via bot_id + update_id)"""

    __tablename__ = "updates"

    id: int | None = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bots.id", index=True)
    chat_id: int = Field(foreign_key="chats.id")
    update_id: str = Field(index=True, unique=True)  # Telegram's update_id (unique per bot)
    message_type: str  # "text", "photo", "document", etc.
    message_text: str | None = None
    raw_update: str  # Full JSON
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    bot: Bot = Relationship(back_populates="updates")
    chat: Chat = Relationship(back_populates="updates")


class CommandLog(SQLModel, table=True):
    """Command Execution Log"""

    __tablename__ = "command_logs"

    id: int | None = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bots.id", index=True)
    chat_id: str
    command: str  # e.g., "/start", "/help"
    response: str
    status: str = "success"  # "success", "error"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Job(SQLModel, table=True):
    """RQ Job Tracking"""

    __tablename__ = "jobs"

    id: int | None = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bots.id")
    job_id: str = Field(unique=True, index=True)
    task_type: str  # "navigate", "screenshot", etc.
    status: str = "queued"  # "queued", "running", "completed", "failed"
    result: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
