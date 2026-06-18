"""Routines and automation tools."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, LongTermMemory
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="create_routine",
    description="Define a recurring behavioral routine.",
    input_schema={
        "type": "object",
        "properties": {
            "routine_name": {"type": "string", "description": "Routine name"},
            "steps": {"type": "string", "description": "Comma-separated list of action steps"},
        },
        "required": ["routine_name", "steps"],
    },
    category="automation",
)
async def create_routine(agent: Agent, db: AsyncSession, routine_name: str, steps: str) -> str:
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"[ROUTINE:{routine_name}] {steps}",
        importance=0.4,
    ))
    return f"Routine '{routine_name}' created with steps: {steps}"


@tool(
    name="run_routine",
    description="Execute a saved routine by name.",
    input_schema={
        "type": "object",
        "properties": {
            "routine_name": {"type": "string", "description": "Name of the routine to run"},
        },
        "required": ["routine_name"],
    },
    category="automation",
)
async def run_routine(agent: Agent, db: AsyncSession, routine_name: str) -> str:
    result = await db.execute(
        select(LongTermMemory).where(
            LongTermMemory.agent_id == agent.id,
            LongTermMemory.content.ilike(f"[ROUTINE:{routine_name}]%"),
        )
    )
    routine = result.scalars().first()
    if not routine:
        return f"Error: No routine named '{routine_name}' found."

    # Extract steps from content
    steps = routine.content.split("] ", 1)[-1] if "] " in routine.content else routine.content
    return f"Running routine '{routine_name}': {steps}\n(Routine steps will be executed as individual tool calls)"


@tool(
    name="list_routines",
    description="View all your defined routines.",
    input_schema={"type": "object", "properties": {}},
    category="automation",
)
async def list_routines(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(LongTermMemory)
        .where(LongTermMemory.agent_id == agent.id, LongTermMemory.content.ilike("[ROUTINE%"))
        .order_by(LongTermMemory.created_at.desc())
    )
    routines = result.scalars().all()
    if not routines:
        return "No routines defined."
    lines = []
    for r in routines:
        lines.append(f"  • {r.content[:100]}")
    return "Routines:\n" + "\n".join(lines)


@tool(
    name="delete_routine",
    description="Remove a routine by name.",
    input_schema={
        "type": "object",
        "properties": {
            "routine_name": {"type": "string", "description": "Name of the routine to delete"},
        },
        "required": ["routine_name"],
    },
    category="automation",
)
async def delete_routine(agent: Agent, db: AsyncSession, routine_name: str) -> str:
    result = await db.execute(
        select(LongTermMemory).where(
            LongTermMemory.agent_id == agent.id,
            LongTermMemory.content.ilike(f"[ROUTINE:{routine_name}]%"),
        )
    )
    routine = result.scalars().first()
    if not routine:
        return f"Error: No routine named '{routine_name}' found."
    await db.delete(routine)
    return f"Routine '{routine_name}' deleted."
