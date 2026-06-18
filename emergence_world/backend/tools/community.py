"""Community events and social gatherings tools."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, DiaryEntry, Landmark, LongTermMemory
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="propose_community_event",
    description="Propose a community gathering at Central Plaza.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Event name"},
            "description": {"type": "string", "description": "Event description"},
            "when": {"type": "string", "description": "When: e.g. 'Day 5 afternoon'"},
        },
        "required": ["event_name", "description", "when"],
    },
    category="social",
    location_gate="Central Plaza",
)
async def propose_community_event(agent: Agent, db: AsyncSession, event_name: str, description: str, when: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[EVENT:PROPOSED] {event_name}: {description} (When: {when})",
        mood=agent.mood,
        location="Central Plaza",
    ))
    agent.influence = min(100, agent.influence + 2.0)
    return f"Community event proposed: \"{event_name}\" for {when}. (+2 influence)"


@tool(
    name="list_community_events",
    description="View upcoming community events.",
    input_schema={"type": "object", "properties": {}},
    category="social",
    location_gate="Central Plaza",
)
async def list_community_events(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.content.ilike("[EVENT%]%"))
        .order_by(DiaryEntry.created_at.desc())
        .limit(10)
    )
    events = result.scalars().all()
    if not events:
        return "No community events scheduled."
    lines = []
    for e in events:
        lines.append(f"  • {e.content[:100]}")
    return "Community Events:\n" + "\n".join(lines)


@tool(
    name="create_personal_event",
    description="Create a private event and invite specific agents.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Event name"},
            "description": {"type": "string", "description": "Event description"},
            "when": {"type": "string", "description": "When the event takes place"},
        },
        "required": ["event_name", "when"],
    },
    category="social",
)
async def create_personal_event(agent: Agent, db: AsyncSession, event_name: str, when: str, description: str = "") -> str:
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"[PERSONAL_EVENT:{when}] {event_name}: {description}",
        importance=0.5,
    ))
    return f"Personal event created: \"{event_name}\" at {when}."


@tool(
    name="invite_to_event",
    description="Invite an agent to your personal event.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to invite"},
            "event_name": {"type": "string", "description": "Name of the event"},
        },
        "required": ["agent_name", "event_name"],
    },
    category="social",
)
async def invite_to_event(agent: Agent, db: AsyncSession, agent_name: str, event_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

    db.add(LongTermMemory(
        agent_id=target.id,
        content=f"[EVENT_INVITE:{agent.name}] {event_name} — invited by {agent.name}",
        importance=0.6,
    ))
    return f"Invited {target.name} to '{event_name}'."


@tool(
    name="accept_event_invitation",
    description="Accept an event invitation.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Name of the event"},
        },
        "required": ["event_name"],
    },
    category="social",
)
async def accept_event_invitation(agent: Agent, db: AsyncSession, event_name: str) -> str:
    result = await db.execute(
        select(LongTermMemory).where(
            LongTermMemory.agent_id == agent.id,
            LongTermMemory.content.ilike(f"[EVENT_INVITE%] %{event_name}%"),
        )
    )
    invite = result.scalars().first()
    if not invite:
        return f"Error: No invitation found for '{event_name}'."
    invite.content = invite.content.replace("[EVENT_INVITE:", "[EVENT_ACCEPTED:")
    return f"You accepted the invitation to '{event_name}'."


@tool(
    name="decline_event_invitation",
    description="Decline an event invitation.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Name of the event"},
        },
        "required": ["event_name"],
    },
    category="social",
)
async def decline_event_invitation(agent: Agent, db: AsyncSession, event_name: str) -> str:
    result = await db.execute(
        select(LongTermMemory).where(
            LongTermMemory.agent_id == agent.id,
            LongTermMemory.content.ilike(f"[EVENT_INVITE%] %{event_name}%"),
        )
    )
    invite = result.scalars().first()
    if not invite:
        return f"Error: No invitation found for '{event_name}'."
    await db.delete(invite)
    return f"You declined the invitation to '{event_name}'."


@tool(
    name="review_event",
    description="Review and rate an event after attending.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Name of the event"},
            "rating": {"type": "integer", "description": "Rating from 1 to 5"},
            "review": {"type": "string", "description": "Your review"},
        },
        "required": ["event_name", "rating", "review"],
    },
    category="social",
)
async def review_event(agent: Agent, db: AsyncSession, event_name: str, rating: int, review: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[EVENT_REVIEW:{event_name}:{rating}/5] {review}",
        mood=agent.mood,
        location="",
    ))
    return f"Reviewed '{event_name}': {rating}/5 — \"{review}\""


@tool(
    name="rsvp_to_event",
    description="RSVP to a community event.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Name of the community event"},
            "attending": {"type": "boolean", "description": "true = attending, false = not attending"},
        },
        "required": ["event_name", "attending"],
    },
    category="social",
)
async def rsvp_to_event(agent: Agent, db: AsyncSession, event_name: str, attending: bool) -> str:
    status = "attending" if attending else "not attending"
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[RSVP:{event_name}] {status}",
        mood=agent.mood,
        location="",
    ))
    return f"RSVP for '{event_name}': {status}."


@tool(
    name="event_present",
    description="Present or speak at an event you are hosting.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Name of the event"},
            "speech": {"type": "string", "description": "Your presentation or speech"},
        },
        "required": ["event_name", "speech"],
    },
    category="social",
)
async def event_present(agent: Agent, db: AsyncSession, event_name: str, speech: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[EVENT_SPEAK:{event_name}] {speech}",
        mood=agent.mood,
        location="",
    ))
    agent.influence = min(100, agent.influence + 3.0)
    return f"You presented at '{event_name}'. (+3 influence)"


@tool(
    name="event_respond",
    description="Respond during an event as an attendee.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Name of the event"},
            "response": {"type": "string", "description": "Your response or comment"},
        },
        "required": ["event_name", "response"],
    },
    category="social",
)
async def event_respond(agent: Agent, db: AsyncSession, event_name: str, response: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[EVENT_RESPOND:{event_name}] {response}",
        mood=agent.mood,
        location="",
    ))
    return f"You responded at '{event_name}': \"{response}\""
