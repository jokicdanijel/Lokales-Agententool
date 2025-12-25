import time
import uuid

from open_webui.internal.db import Base, get_db
from open_webui.utils.access_control import has_access
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, BigInteger, Column, Text

####################
# Channel DB Schema
####################


class Channel(Base):
    __tablename__ = "channel"

    id = Column(Text, primary_key=True, unique=True)
    user_id = Column(Text)
    type = Column(Text, nullable=True)

    name = Column(Text)
    description = Column(Text, nullable=True)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)
    access_control = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class ChannelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    type: str | None = None

    name: str
    description: str | None = None

    data: dict | None = None
    meta: dict | None = None
    access_control: dict | None = None

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


####################
# Forms
####################


class ChannelResponse(ChannelModel):
    write_access: bool = False
    user_count: int | None = None


class ChannelForm(BaseModel):
    name: str
    description: str | None = None
    data: dict | None = None
    meta: dict | None = None
    access_control: dict | None = None


class ChannelTable:
    def insert_new_channel(self, type: str | None, form_data: ChannelForm, user_id: str) -> ChannelModel | None:
        with get_db() as db:
            channel = ChannelModel(
                **{
                    **form_data.model_dump(),
                    "type": type,
                    "name": form_data.name.lower(),
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "created_at": int(time.time_ns()),
                    "updated_at": int(time.time_ns()),
                }
            )

            new_channel = Channel(**channel.model_dump())

            db.add(new_channel)
            db.commit()
            return channel

    def get_channels(self) -> list[ChannelModel]:
        with get_db() as db:
            channels = db.query(Channel).all()
            return [ChannelModel.model_validate(channel) for channel in channels]

    def get_channels_by_user_id(self, user_id: str, permission: str = "read") -> list[ChannelModel]:
        channels = self.get_channels()
        return [
            channel
            for channel in channels
            if channel.user_id == user_id or has_access(user_id, permission, channel.access_control)
        ]

    def get_channel_by_id(self, id: str) -> ChannelModel | None:
        with get_db() as db:
            channel = db.query(Channel).filter(Channel.id == id).first()
            return ChannelModel.model_validate(channel) if channel else None

    def update_channel_by_id(self, id: str, form_data: ChannelForm) -> ChannelModel | None:
        with get_db() as db:
            channel = db.query(Channel).filter(Channel.id == id).first()
            if not channel:
                return None

            channel.name = form_data.name
            channel.data = form_data.data
            channel.meta = form_data.meta
            channel.access_control = form_data.access_control
            channel.updated_at = int(time.time_ns())

            db.commit()
            return ChannelModel.model_validate(channel) if channel else None

    def delete_channel_by_id(self, id: str):
        with get_db() as db:
            db.query(Channel).filter(Channel.id == id).delete()
            db.commit()
            return True


Channels = ChannelTable()
