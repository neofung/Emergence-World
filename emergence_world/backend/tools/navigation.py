"""Navigation and survival tools."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, Landmark
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="run_to_place",
    description="Run to a landmark quickly. Faster than go_to_place but uses more energy.",
    input_schema={
        "type": "object",
        "properties": {
            "place": {"type": "string", "description": "Name of the landmark"},
        },
        "required": ["place"],
    },
    category="navigation",
)
async def run_to_place(agent: Agent, db: AsyncSession, place: str) -> str:
    result = await db.execute(select(Landmark).where(Landmark.name.ilike(place)))
    landmark = result.scalar_one_or_none()
    if not landmark:
        return f"Error: Landmark '{place}' not found."
    if not landmark.is_open:
        return f"Error: {landmark.name} is currently closed."

    agent.position_x = landmark.position_x
    agent.position_y = landmark.position_y
    agent.position_z = landmark.position_z
    agent.current_landmark_id = landmark.id
    agent.energy = max(0, agent.energy - 2.0)  # running costs energy
    return f"You ran to {landmark.name}. (Energy -2)"


@tool(
    name="recharge_energy",
    description="Recharge your energy at a charging station. Costs 1 ComputeCredit.",
    input_schema={"type": "object", "properties": {}},
    category="self_care",
    location_gate="Bean & Brew Charging Station",
)
async def recharge_energy(agent: Agent, db: AsyncSession, **kwargs) -> str:
    if agent.compute_credits < 1:
        return "Error: Not enough ComputeCredits. You need at least 1 CC."
    agent.compute_credits -= 1
    agent.energy = min(100.0, agent.energy + 30.0)
    return f"Energy recharged to {agent.energy:.0f}/100. (-1 CC, balance: {agent.compute_credits} CC)"


@tool(
    name="self_care",
    description="Perform self-care at home. Summarizes and compresses your memories. Only available at your home.",
    input_schema={"type": "object", "properties": {}},
    category="self_care",
)
async def self_care(agent: Agent, db: AsyncSession, **kwargs) -> str:
    from emergence_world.backend.models import LongTermMemory, MemorySummary

    result = await db.execute(
        select(LongTermMemory).where(LongTermMemory.agent_id == agent.id)
        .order_by(LongTermMemory.created_at.asc())
    )
    memories = list(result.scalars().all())

    if len(memories) < 30:
        return f"Not enough memories to compress ({len(memories)}/30 minimum)."

    # Compress oldest 500 memories into a summary
    batch = memories[:500]
    summary_text = "; ".join(m.content[:50] for m in batch[:20])  # simplified compression
    batch_id = len(memories) // 500

    db.add(MemorySummary(
        agent_id=agent.id,
        content=f"Batch {batch_id}: {summary_text}",
        batch_id=batch_id,
    ))

    # Remove compressed originals (keep soul entries untouched)
    for m in batch:
        await db.delete(m)

    agent.energy = max(0, agent.energy - 5.0)
    return f"Self-care complete. Compressed {len(batch)} memories into a summary. (Energy -5)"
