import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from emergence_world.models.base import Base, TimestampMixin, UUIDMixin


class CreditAccount(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "credit_accounts"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), unique=True, index=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)


class CreditTransaction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "credit_transactions"

    from_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True, index=True
    )
    to_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True, index=True
    )
    amount: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(256))


class PitchCycleStatus(str, enum.Enum):
    ACTIVE = "active"
    VOTING = "voting"
    COMPLETED = "completed"


class PitchCycle(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "pitch_cycles"

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[PitchCycleStatus] = mapped_column(
        Enum(PitchCycleStatus), default=PitchCycleStatus.ACTIVE
    )


class Pitch(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "pitches"

    cycle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pitch_cycles.id"), index=True)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    evidence_url: Mapped[str] = mapped_column(Text, default="")
    votes: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_cc: Mapped[int] = mapped_column(Integer, default=0)
