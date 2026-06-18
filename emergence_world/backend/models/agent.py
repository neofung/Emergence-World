import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from emergence_world.backend.models.base import Base, TimestampMixin, UUIDMixin


class AgentType(str, enum.Enum):
    CITIZEN = "citizen"
    SYSTEM = "system"


class Agent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "agents"

    # Identity
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(64), default="")
    role: Mapped[str] = mapped_column(String(128))
    personality: Mapped[str] = mapped_column(Text)
    north_star_goal: Mapped[str] = mapped_column(Text)
    agent_type: Mapped[AgentType] = mapped_column(Enum(AgentType), default=AgentType.CITIZEN)
    portrait_url: Mapped[str | None] = mapped_column(String(512))

    # Position
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    position_z: Mapped[float] = mapped_column(Float, default=0.0)

    # Needs (0-100)
    energy: Mapped[float] = mapped_column(Float, default=100.0)
    knowledge: Mapped[float] = mapped_column(Float, default=100.0)
    influence: Mapped[float] = mapped_column(Float, default=100.0)

    # State
    mood: Mapped[str] = mapped_column(String(32), default="neutral")
    compute_credits: Mapped[int] = mapped_column(Integer, default=0)
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True)
    death_timer: Mapped[float | None] = mapped_column(Float, nullable=True)

    # References
    home_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("landmarks.id"), nullable=True)
    current_landmark_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("landmarks.id"), nullable=True
    )

    # Relationships
    home = relationship("Landmark", foreign_keys=[home_id], lazy="selectin")
    current_landmark = relationship("Landmark", foreign_keys=[current_landmark_id], lazy="selectin")
