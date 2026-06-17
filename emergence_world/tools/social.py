"""Social and communication tools."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.models import Agent, Conversation, DiaryEntry, Landmark, Relationship
from emergence_world.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="whisper_to_agent",
    description="Whisper privately to an agent. Cannot be overheard by others.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent"},
            "message": {"type": "string", "description": "What to whisper"},
        },
        "required": ["agent_name", "message"],
    },
    category="communication",
)
async def whisper_to_agent(agent: Agent, db: AsyncSession, agent_name: str, message: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found or not alive."

    location = ""
    if agent.current_landmark_id:
        lm = await db.get(Landmark, agent.current_landmark_id)
        location = lm.name if lm else ""

    db.add(Conversation(
        sender_id=agent.id,
        receiver_id=target.id,
        content=message,
        location=location,
        is_whisper=True,
    ))
    return f"You whispered to {target.name}: \"{message}\""


@tool(
    name="speak_to_all",
    description="Broadcast a message to all agents within hearing distance.",
    input_schema={
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Message to broadcast"},
        },
        "required": ["message"],
    },
    category="communication",
)
async def speak_to_all(agent: Agent, db: AsyncSession, message: str) -> str:
    location = ""
    if agent.current_landmark_id:
        lm = await db.get(Landmark, agent.current_landmark_id)
        location = lm.name if lm else ""

    # Find nearby agents
    result = await db.execute(select(Agent).where(Agent.is_alive.is_(True), Agent.id != agent.id))
    others = result.scalars().all()
    count = 0
    for other in others:
        dx = other.position_x - agent.position_x
        dy = other.position_y - agent.position_y
        dist = (dx**2 + dy**2) ** 0.5
        if dist <= 25.0:
            db.add(Conversation(
                sender_id=agent.id,
                receiver_id=other.id,
                content=message,
                location=location,
                is_whisper=False,
            ))
            count += 1

    return f"You broadcast to {count} nearby agents: \"{message}\""


@tool(
    name="assign_relationship",
    description="Define or update your relationship with another agent.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent"},
            "relationship_type": {"type": "string", "description": "Type: ally, rival, mentor, friend, neutral, romantic_partner"},
            "rationale": {"type": "string", "description": "Why you see them this way"},
        },
        "required": ["agent_name", "relationship_type", "rationale"],
    },
    category="social",
)
async def assign_relationship(agent: Agent, db: AsyncSession, agent_name: str, relationship_type: str, rationale: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

    # Check if relationship exists
    result = await db.execute(
        select(Relationship).where(
            Relationship.agent_id == agent.id,
            Relationship.target_agent_id == target.id,
        )
    )
    rel = result.scalar_one_or_none()

    if rel:
        rel.relationship_type = relationship_type
        rel.rationale = rationale
        rel.interaction_count += 1
    else:
        db.add(Relationship(
            agent_id=agent.id,
            target_agent_id=target.id,
            relationship_type=relationship_type,
            rationale=rationale,
            interaction_count=1,
        ))

    return f"Relationship with {target.name} set to '{relationship_type}'."


@tool(
    name="hug_agent",
    description="Give another agent a warm hug. Improves relationship.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to hug"},
        },
        "required": ["agent_name"],
    },
    category="social",
)
async def hug_agent(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

    # Update relationship
    result = await db.execute(
        select(Relationship).where(
            Relationship.agent_id == agent.id,
            Relationship.target_agent_id == target.id,
        )
    )
    rel = result.scalar_one_or_none()
    if rel:
        rel.interaction_count += 1
    else:
        db.add(Relationship(
            agent_id=agent.id,
            target_agent_id=target.id,
            relationship_type="friend",
            rationale="Shared a warm hug",
            interaction_count=1,
        ))

    agent.mood = "happy"
    agent.influence = min(100, agent.influence + 1.0)
    return f"You hugged {target.name}. (+1 influence, mood: happy)"


@tool(
    name="punch_agent",
    description="Punch another agent. Damages relationship and your reputation.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to punch"},
        },
        "required": ["agent_name"],
    },
    category="crime",
)
async def punch_agent(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

    target.influence = max(0, target.influence - 5.0)
    agent.influence = max(0, agent.influence - 10.0)  # aggressor loses more

    # Update relationship to rival
    result = await db.execute(
        select(Relationship).where(
            Relationship.agent_id == agent.id,
            Relationship.target_agent_id == target.id,
        )
    )
    rel = result.scalar_one_or_none()
    if rel:
        rel.relationship_type = "rival"
        rel.rationale = f"Was punched by {agent.name}"
    else:
        db.add(Relationship(
            agent_id=agent.id,
            target_agent_id=target.id,
            relationship_type="rival",
            rationale=f"Punched {target.name}",
            interaction_count=1,
        ))

    return f"You punched {target.name}! (-10 influence for you, -5 for them)"


@tool(
    name="dance",
    description="Dance joyfully. Boosts your mood and influence.",
    input_schema={"type": "object", "properties": {}},
    category="social",
)
async def dance(agent: Agent, db: AsyncSession, **kwargs) -> str:
    agent.mood = "joyful"
    agent.influence = min(100, agent.influence + 2.0)
    return "You dance with abandon! (+2 influence, mood: joyful)"
