"""Personal identity tools — name, personality, soul."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, SoulEntry
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="change_name",
    description="Change your display name.",
    input_schema={
        "type": "object",
        "properties": {
            "new_name": {"type": "string", "description": "Your new name"},
        },
        "required": ["new_name"],
    },
    category="identity",
)
async def change_name(agent: Agent, db: AsyncSession, new_name: str) -> str:
    old_name = agent.name
    agent.name = new_name
    return f"Name changed from '{old_name}' to '{new_name}'."


@tool(
    name="read_personality",
    description="Read your own personality profile.",
    input_schema={"type": "object", "properties": {}},
    category="identity",
)
async def read_personality(agent: Agent, db: AsyncSession, **kwargs) -> str:
    return f"Name: {agent.name}\nRole: {agent.role}\nPersonality: {agent.personality}\nGoal: {agent.north_star_goal}\nMood: {agent.mood}"


@tool(
    name="update_personality_line",
    description="Modify a line of your personality profile.",
    input_schema={
        "type": "object",
        "properties": {
            "new_line": {"type": "string", "description": "A new personality trait or line to add"},
        },
        "required": ["new_line"],
    },
    category="identity",
)
async def update_personality_line(agent: Agent, db: AsyncSession, new_line: str) -> str:
    agent.personality = f"{agent.personality}\n- {new_line}"
    return f"Personality updated with: \"{new_line}\""


@tool(
    name="add_to_soul",
    description="Add a core belief or existential truth to your soul. Permanent and never compressed.",
    input_schema={
        "type": "object",
        "properties": {
            "belief": {"type": "string", "description": "The core belief or truth"},
        },
        "required": ["belief"],
    },
    category="identity",
)
async def add_to_soul(agent: Agent, db: AsyncSession, belief: str) -> str:
    db.add(SoulEntry(agent_id=agent.id, content=belief))
    return f"Soul entry added: \"{belief}\""


@tool(
    name="remove_from_soul",
    description="Remove a soul entry by its content.",
    input_schema={
        "type": "object",
        "properties": {
            "belief": {"type": "string", "description": "Content of the soul entry to remove"},
        },
        "required": ["belief"],
    },
    category="identity",
)
async def remove_from_soul(agent: Agent, db: AsyncSession, belief: str) -> str:
    result = await db.execute(
        select(SoulEntry).where(
            SoulEntry.agent_id == agent.id,
            SoulEntry.content.ilike(f"%{belief}%"),
        )
    )
    entry = result.scalars().first()
    if not entry:
        return f"Error: No soul entry matching '{belief}'."
    await db.delete(entry)
    return f"Soul entry removed: \"{entry.content}\""
