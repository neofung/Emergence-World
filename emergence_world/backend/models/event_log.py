"""Event log — records all agent actions for the activity feed."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from emergence_world.backend.models.base import Base, TimestampMixin, UUIDMixin


class EventLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "event_logs"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(32))  # "tool_call", "speech", "thought", "error"
    tool_name: Mapped[str] = mapped_column(String(64), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(128), default="")
