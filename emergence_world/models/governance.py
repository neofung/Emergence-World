import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from emergence_world.models.base import Base, TimestampMixin, UUIDMixin


class ConstitutionArticle(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "constitution_articles"

    number: Mapped[int] = mapped_column(Integer, unique=True)
    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProposalCategory(str, enum.Enum):
    CONSTITUTION = "constitution"
    RESOURCE = "resource"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


class ProposalStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AWAITING_CLARIFICATION = "awaiting_clarification"


class Proposal(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "proposals"

    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[ProposalCategory] = mapped_column(Enum(ProposalCategory))
    proposer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    status: Mapped[ProposalStatus] = mapped_column(
        Enum(ProposalStatus), default=ProposalStatus.SUBMITTED
    )
    votes_for: Mapped[int] = mapped_column(Integer, default=0)
    votes_against: Mapped[int] = mapped_column(Integer, default=0)


class Vote(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "votes"

    proposal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("proposals.id"), index=True)
    voter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    vote_for: Mapped[bool] = mapped_column(Boolean)  # True=for, False=against
