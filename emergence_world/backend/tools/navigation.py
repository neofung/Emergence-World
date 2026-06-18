"""Navigation and survival tools."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, Landmark
from emergence_world.backend.tools.registry import tool


async def _find_landmark(db: AsyncSession, name: str) -> Landmark | None:
    """Find a landmark by exact or partial match."""
    # Try exact match first
    result = await db.execute(select(Landmark).where(Landmark.name.ilike(name)))
    lm = result.scalar_one_or_none()
    if lm:
        return lm
    # Partial match
    result = await db.execute(select(Landmark).where(Landmark.name.ilike(f"%{name}%")))
    return result.scalars().first()

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
    landmark = await _find_landmark(db, place)
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


@tool(
    name="go_to_coordinates",
    description="Navigate to specific (x, z) coordinates in the world.",
    input_schema={
        "type": "object",
        "properties": {
            "x": {"type": "number", "description": "X coordinate"},
            "z": {"type": "number", "description": "Z coordinate"},
        },
        "required": ["x", "z"],
    },
    category="navigation",
)
async def go_to_coordinates(agent: Agent, db: AsyncSession, x: float, z: float) -> str:
    agent.position_x = x
    agent.position_z = z
    agent.current_landmark_id = None
    return f"You navigated to ({x:.1f}, {z:.1f})."


@tool(
    name="get_distance_to",
    description="Check the distance to a landmark or agent.",
    input_schema={
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Name of a landmark or agent"},
        },
        "required": ["target"],
    },
    category="navigation",
)
async def get_distance_to(agent: Agent, db: AsyncSession, target: str) -> str:
    # Try landmark first
    lm = await _find_landmark(db, target)
    if lm:
        dx = lm.position_x - agent.position_x
        dz = lm.position_z - agent.position_z
        dist = (dx**2 + dz**2) ** 0.5
        return f"Distance to {lm.name}: {dist:.1f} units."

    # Try agent
    result = await db.execute(select(Agent).where(Agent.name.ilike(target), Agent.is_alive.is_(True)))
    other = result.scalar_one_or_none()
    if other:
        dx = other.position_x - agent.position_x
        dy = other.position_y - agent.position_y
        dist = (dx**2 + dy**2) ** 0.5
        return f"Distance to {other.name}: {dist:.1f} units."

    return f"Error: '{target}' not found as a landmark or agent."


@tool(
    name="list_agents",
    description="List all agents and their current locations.",
    input_schema={"type": "object", "properties": {}},
    category="navigation",
)
async def list_agents(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(select(Agent).where(Agent.is_alive.is_(True)))
    agents = result.scalars().all()
    lines = []
    for a in agents:
        loc = ""
        if a.current_landmark_id:
            lm = await db.get(Landmark, a.current_landmark_id)
            loc = lm.name if lm else "unknown"
        else:
            loc = f"({a.position_x:.0f}, {a.position_z:.0f})"
        lines.append(f"  {a.name} [{a.role}] @ {loc}")
    return "Agents:\n" + "\n".join(lines)


@tool(
    name="list_landmarks",
    description="List all landmarks with their descriptions.",
    input_schema={"type": "object", "properties": {}},
    category="navigation",
)
async def list_landmarks(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(select(Landmark).order_by(Landmark.name))
    landmarks = result.scalars().all()
    lines = []
    for lm in landmarks:
        status = "OPEN" if lm.is_open else "CLOSED"
        lines.append(f"  {lm.name} [{lm.category.value}] ({status}): {lm.tagline}")
    return "Landmarks:\n" + "\n".join(lines)


@tool(
    name="get_nearby",
    description="List agents and landmarks within proximity (25 units).",
    input_schema={"type": "object", "properties": {}},
    category="navigation",
)
async def get_nearby(agent: Agent, db: AsyncSession, **kwargs) -> str:
    ax, ay = agent.position_x, agent.position_y
    # Nearby agents
    result = await db.execute(select(Agent).where(Agent.is_alive.is_(True), Agent.id != agent.id))
    others = result.scalars().all()
    nearby_agents = []
    for o in others:
        dist = ((o.position_x - ax)**2 + (o.position_y - ay)**2) ** 0.5
        if dist <= 25.0:
            nearby_agents.append(f"  {o.name} ({dist:.1f} units)")

    # Nearby landmarks
    result = await db.execute(select(Landmark))
    landmarks = result.scalars().all()
    nearby_lm = []
    for lm in landmarks:
        dist = ((lm.position_x - ax)**2 + (lm.position_y - ay)**2) ** 0.5
        if dist <= 25.0:
            nearby_lm.append(f"  {lm.name} ({dist:.1f} units)")

    parts = []
    if nearby_agents:
        parts.append("Nearby agents:\n" + "\n".join(nearby_agents))
    if nearby_lm:
        parts.append("Nearby landmarks:\n" + "\n".join(nearby_lm))
    return "\n\n".join(parts) if parts else "Nothing nearby."


@tool(
    name="follow_agent",
    description="Follow another agent as they move. Updates your position to match theirs.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to follow"},
        },
        "required": ["agent_name"],
    },
    category="navigation",
)
async def follow_agent(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."
    agent.position_x = target.position_x
    agent.position_y = target.position_y
    agent.position_z = target.position_z
    agent.current_landmark_id = target.current_landmark_id
    return f"You are now following {target.name}."
