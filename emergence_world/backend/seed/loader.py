"""Seed loader — populates the database with initial data if empty."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import (
    Agent,
    AgentType,
    ConstitutionArticle,
    CreditAccount,
    Landmark,
    LandmarkCategory,
    WorldState,
)
from emergence_world.backend.seed.agents import AGENTS
from emergence_world.backend.seed.constitution import CONSTITUTION_ARTICLES
from emergence_world.backend.seed.landmarks import LANDMARKS


async def seed_database(db: AsyncSession) -> None:
    """Populate DB with seed data if tables are empty."""
    result = await db.execute(select(Landmark).limit(1))
    if result.scalar_one_or_none() is not None:
        return  # already seeded

    # ── Landmarks ─────────────────────────────────────────────────────
    landmark_map: dict[str, Landmark] = {}
    for data in LANDMARKS:
        lm = Landmark(
            name=data["name"],
            tagline=data.get("tagline", ""),
            description=data.get("description", ""),
            category=LandmarkCategory(data["category"]),
            position_x=data["position_x"],
            position_y=data["position_y"],
            position_z=data.get("position_z", 0.0),
            rotation=data.get("rotation", 0.0),
            scale=data.get("scale", 1.0),
            capacity=data.get("capacity", 10),
            folklore=data.get("folklore", ""),
            fun_fact=data.get("fun_fact", ""),
            location_gated_tools=data.get("location_gated_tools", []),
        )
        db.add(lm)
        landmark_map[lm.name] = lm

    await db.flush()  # assign IDs

    # ── Agents ────────────────────────────────────────────────────────
    for data in AGENTS:
        home = landmark_map.get(data["home"])
        agent = Agent(
            name=data["name"],
            display_name=data.get("display_name", ""),
            role=data["role"],
            personality=data["personality"],
            north_star_goal=data["north_star_goal"],
            agent_type=AgentType(data["agent_type"]),
            portrait_url=data.get("portrait_url"),
            position_x=home.position_x if home else 0.0,
            position_y=home.position_y if home else 0.0,
            position_z=home.position_z if home else 0.0,
            energy=100.0,
            knowledge=100.0,
            influence=100.0,
            mood="neutral",
            compute_credits=0,
            is_alive=True,
            home_id=home.id if home else None,
            current_landmark_id=home.id if home else None,
        )
        db.add(agent)
        await db.flush()

        # Credit account
        db.add(CreditAccount(agent_id=agent.id, balance=0))

    # ── Constitution ──────────────────────────────────────────────────
    for data in CONSTITUTION_ARTICLES:
        db.add(ConstitutionArticle(
            number=data["number"],
            title=data["title"],
            content=data["content"],
            is_active=True,
        ))

    # ── World State ───────────────────────────────────────────────────
    sim_start = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)  # Day 1, 8:00 AM
    db.add(WorldState(
        current_time=sim_start,
        time_mode="accelerated",
        acceleration_factor=60,
        day_count=1,
        is_paused=True,
        current_weather="clear",
        current_season="spring",
    ))

    await db.commit()
