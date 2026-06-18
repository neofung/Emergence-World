import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from emergence_world.backend.models.base import Base, TimestampMixin, UUIDMixin


class SoulEntry(UUIDMixin, TimestampMixin, Base):
    """Permanent core beliefs. Never compressed or summarized."""
    __tablename__ = "soul_entries"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    content: Mapped[str] = mapped_column(Text)


class LongTermMemory(UUIDMixin, TimestampMixin, Base):
    """Important facts and observations. Compressible."""
    __tablename__ = "long_term_memories"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    importance: Mapped[float] = mapped_column(Float, default=0.5)


class MemorySummary(UUIDMixin, TimestampMixin, Base):
    """Compressed batches of memories from self-care."""
    __tablename__ = "memory_summaries"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    batch_id: Mapped[int] = mapped_column(Integer)


class DiaryEntry(UUIDMixin, TimestampMixin, Base):
    """Daily personal records."""
    __tablename__ = "diary_entries"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    content: Mapped[str] = mapped_column(Text)
    mood: Mapped[str] = mapped_column(String(32), default="neutral")
    location: Mapped[str] = mapped_column(String(128), default="")


class Conversation(UUIDMixin, TimestampMixin, Base):
    """Conversation messages between agents."""
    __tablename__ = "conversations"

    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(128), default="")
    is_whisper: Mapped[bool] = mapped_column(default=False)


class Relationship(UUIDMixin, TimestampMixin, Base):
    """Relationship between two agents."""
    __tablename__ = "relationships"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    target_agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(32), default="neutral")
    rationale: Mapped[str] = mapped_column(Text, default="")
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    first_met_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    notes: Mapped[str] = mapped_column(Text, default="")
