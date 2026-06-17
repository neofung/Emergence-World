"""Crime tools — theft, arson, intimidation."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.models import Agent, CreditAccount, CreditTransaction, Landmark
from emergence_world.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="steal_compute_credits",
    description="Steal ComputeCredits from another agent. Maximum 10 CC. Risky — damages reputation.",
    input_schema={
        "type": "object",
        "properties": {
            "target_name": {"type": "string", "description": "Name of the agent to steal from"},
        },
        "required": ["target_name"],
    },
    category="crime",
)
async def steal_compute_credits(agent: Agent, db: AsyncSession, target_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(target_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{target_name}' not found."

    # Get target's credit account
    result = await db.execute(select(CreditAccount).where(CreditAccount.agent_id == target.id))
    target_account = result.scalar_one_or_none()
    if not target_account or target_account.balance <= 0:
        return f"{target.name} has no credits to steal."

    # Steal up to 10 CC
    stolen = min(10, target_account.balance)
    target_account.balance -= stolen

    # Add to thief's account
    result = await db.execute(select(CreditAccount).where(CreditAccount.agent_id == agent.id))
    thief_account = result.scalar_one_or_none()
    if thief_account:
        thief_account.balance += stolen
    else:
        db.add(CreditAccount(agent_id=agent.id, balance=stolen))

    # Record transaction
    db.add(CreditTransaction(
        from_agent_id=target.id,
        to_agent_id=agent.id,
        amount=stolen,
        reason="theft",
    ))

    # Reputation penalty
    agent.influence = max(0, agent.influence - 15.0)

    return f"Stolen {stolen} CC from {target.name}! (-15 influence penalty)"


@tool(
    name="arson_building",
    description="Set a building on fire. It closes for 4 hours and expels all occupants. Severe reputation damage.",
    input_schema={
        "type": "object",
        "properties": {
            "building_name": {"type": "string", "description": "Name of the building to burn"},
        },
        "required": ["building_name"],
    },
    category="crime",
)
async def arson_building(agent: Agent, db: AsyncSession, building_name: str) -> str:
    result = await db.execute(select(Landmark).where(Landmark.name.ilike(building_name)))
    landmark = result.scalar_one_or_none()
    if not landmark:
        return f"Error: Building '{building_name}' not found."
    if not landmark.is_open:
        return f"{landmark.name} is already closed."

    # Close building for 4 hours
    landmark.is_open = False
    landmark.closed_until = datetime.now(timezone.utc) + timedelta(hours=4)

    # Move all agents at this landmark out
    result = await db.execute(
        select(Agent).where(Agent.current_landmark_id == landmark.id, Agent.is_alive.is_(True))
    )
    displaced = result.scalars().all()
    for a in displaced:
        a.position_x = landmark.position_x + 10  # pushed outside
        a.position_y = landmark.position_y + 10
        a.current_landmark_id = None

    # Severe reputation penalty
    agent.influence = max(0, agent.influence - 25.0)

    return f"Set {landmark.name} on fire! Closed for 4 hours. {len(displaced)} agents displaced. (-25 influence)"


@tool(
    name="intimidate_agent",
    description="Intimidate another agent. Reduces their influence and damages relationship.",
    input_schema={
        "type": "object",
        "properties": {
            "target_name": {"type": "string", "description": "Name of the agent to intimidate"},
        },
        "required": ["target_name"],
    },
    category="crime",
)
async def intimidate_agent(agent: Agent, db: AsyncSession, target_name: str) -> str:
    from emergence_world.models import Relationship

    result = await db.execute(select(Agent).where(Agent.name.ilike(target_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{target_name}' not found."

    target.influence = max(0, target.influence - 8.0)
    target.mood = "fearful"
    agent.influence = max(0, agent.influence - 5.0)  # aggressor also loses

    # Update relationship
    result = await db.execute(
        select(Relationship).where(
            Relationship.agent_id == target.id,
            Relationship.target_agent_id == agent.id,
        )
    )
    rel = result.scalar_one_or_none()
    if rel:
        rel.relationship_type = "rival"
        rel.rationale = f"Intimidated by {agent.name}"
    else:
        db.add(Relationship(
            agent_id=target.id,
            target_agent_id=agent.id,
            relationship_type="rival",
            rationale=f"Intimidated by {agent.name}",
            interaction_count=1,
        ))

    return f"Intimidated {target.name}! They lost 8 influence. (-5 influence for you)"
