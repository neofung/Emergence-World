import enum

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from emergence_world.models.base import Base, TimestampMixin, UUIDMixin


class LandmarkCategory(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MUNICIPAL = "municipal"
    RECREATION = "recreation"
    ENTERTAINMENT = "entertainment"
    LANDMARK = "landmark"


class Landmark(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "landmarks"

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    tagline: Mapped[str] = mapped_column(String(256), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[LandmarkCategory] = mapped_column(Enum(LandmarkCategory))

    # Position & transform
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    position_z: Mapped[float] = mapped_column(Float, default=0.0)
    rotation: Mapped[float] = mapped_column(Float, default=0.0)
    scale: Mapped[float] = mapped_column(Float, default=1.0)

    # State
    capacity: Mapped[int] = mapped_column(Integer, default=10)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    closed_until: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Lore
    folklore: Mapped[str] = mapped_column(Text, default="")
    fun_fact: Mapped[str] = mapped_column(Text, default="")
