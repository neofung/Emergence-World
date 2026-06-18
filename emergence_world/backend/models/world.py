from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from emergence_world.backend.models.base import Base, TimestampMixin, UUIDMixin


class WorldState(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "world_state"

    current_time: Mapped[str] = mapped_column(DateTime(timezone=True))
    time_mode: Mapped[str] = mapped_column(String(32), default="accelerated")
    acceleration_factor: Mapped[int] = mapped_column(Integer, default=60)
    day_count: Mapped[int] = mapped_column(Integer, default=0)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    current_weather: Mapped[str] = mapped_column(String(64), default="clear")
    current_season: Mapped[str] = mapped_column(String(32), default="spring")
