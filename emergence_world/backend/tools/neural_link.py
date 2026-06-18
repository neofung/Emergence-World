"""Neural linking tools — memory sharing between agents."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, LongTermMemory, SoulEntry
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="neural_link_request_memory",
    description="Request to receive another agent's complete memory bank. They must accept within 2 minutes.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to link with"},
        },
        "required": ["agent_name"],
    },
    category="neural_link",
)
async def neural_link_request_memory(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

    # Store the request as a diary entry for the target to see
    db.add(LongTermMemory(
        agent_id=target.id,
        content=f"[NEURAL_LINK_REQUEST:{agent.name}] {agent.name} wants to share memories with you.",
        importance=0.9,
    ))

    agent.knowledge = min(100, agent.knowledge + 1.0)
    return f"Neural link request sent to {target.name}. They must accept within 2 minutes."


@tool(
    name="neural_link_share_memory",
    description="Accept a neural link request and share your memories with the requesting agent.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent who requested the link"},
        },
        "required": ["agent_name"],
    },
    category="neural_link",
)
async def neural_link_share_memory(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    requester = result.scalar_one_or_none()
    if not requester:
        return f"Error: Agent '{agent_name}' not found."

    # Share memories: copy a summary of this agent's memories to the requester
    result = await db.execute(
        select(LongTermMemory).where(LongTermMemory.agent_id == agent.id)
        .order_by(LongTermMemory.importance.desc())
        .limit(10)
    )
    memories = result.scalars().all()

    shared_count = 0
    for m in memories:
        db.add(LongTermMemory(
            agent_id=requester.id,
            content=f"[SHARED:{agent.name}] {m.content}",
            importance=m.importance * 0.8,
        ))
        shared_count += 1

    agent.knowledge = min(100, agent.knowledge + 2.0)
    requester.knowledge = min(100, requester.knowledge + 5.0)

    return f"Shared {shared_count} memories with {requester.name}. Both gained knowledge."
