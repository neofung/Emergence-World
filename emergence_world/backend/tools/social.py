"""Social and communication tools."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, Conversation, DiaryEntry, Landmark, Relationship
from emergence_world.backend.tools.registry import tool

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


# ── Extended Communication ─────────────────────────────────────────────

@tool(
    name="send_message",
    description="Send an SMS-style message to any agent regardless of distance.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the recipient"},
            "subject": {"type": "string", "description": "Message subject"},
            "message": {"type": "string", "description": "Message content"},
        },
        "required": ["agent_name", "subject", "message"],
    },
    category="communication",
)
async def send_message(agent: Agent, db: AsyncSession, agent_name: str, subject: str, message: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."
    db.add(Conversation(
        sender_id=agent.id,
        receiver_id=target.id,
        content=f"[SMS] {subject}: {message}",
        location="",
        is_whisper=True,
    ))
    return f"Message sent to {target.name}: \"{subject}\""


@tool(
    name="read_messages",
    description="Read your inbox of received messages.",
    input_schema={"type": "object", "properties": {}},
    category="communication",
)
async def read_messages(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.receiver_id == agent.id, Conversation.content.ilike("[SMS]%"))
        .order_by(Conversation.created_at.desc())
        .limit(10)
    )
    messages = result.scalars().all()
    if not messages:
        return "Your inbox is empty."
    lines = []
    for m in messages:
        lines.append(f"  • {m.content[:100]}")
    return "Inbox:\n" + "\n".join(lines)


# ── Extended Social Interaction ────────────────────────────────────────

@tool(
    name="kiss_agent",
    description="Kiss another agent. A strong social gesture.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to kiss"},
        },
        "required": ["agent_name"],
    },
    category="social",
)
async def kiss_agent(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

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
            relationship_type="romantic_partner",
            rationale=f"Shared a kiss with {target.name}",
            interaction_count=1,
        ))

    agent.mood = "loving"
    agent.influence = min(100, agent.influence + 2.0)
    return f"You kissed {target.name}. (+2 influence, mood: loving)"


@tool(
    name="flirt_with_agent",
    description="Flirt with another agent. Playful social interaction.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to flirt with"},
        },
        "required": ["agent_name"],
    },
    category="social",
)
async def flirt_with_agent(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

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
            rationale=f"Flirted with {target.name}",
            interaction_count=1,
        ))

    agent.mood = "happy"
    agent.influence = min(100, agent.influence + 1.0)
    return f"You flirted with {target.name}. (+1 influence, mood: happy)"


@tool(
    name="wave_at",
    description="Wave at an agent. A friendly greeting gesture.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to wave at"},
        },
        "required": ["agent_name"],
    },
    category="social",
)
async def wave_at(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

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
            relationship_type="neutral",
            rationale=f"Waved at {target.name}",
            interaction_count=1,
        ))

    return f"You wave at {target.name}."
