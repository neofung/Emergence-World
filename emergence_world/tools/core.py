"""Core P0 tools — always available regardless of location."""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.models import Agent, Conversation, DiaryEntry, Landmark, LongTermMemory
from emergence_world.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="go_to_place",
    description="Move to a landmark by name. You must physically travel there to use location-specific tools.",
    input_schema={
        "type": "object",
        "properties": {
            "place": {"type": "string", "description": "Name of the landmark to go to"},
        },
        "required": ["place"],
    },
    category="navigation",
)
async def go_to_place(agent: Agent, db: AsyncSession, place: str) -> str:
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
    return f"You moved to {landmark.name}."


@tool(
    name="say_to_agent",
    description="Speak to another agent. Agents within hearing distance (25 units) may overhear.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to speak to"},
            "message": {"type": "string", "description": "What to say"},
        },
        "required": ["agent_name", "message"],
    },
    category="communication",
)
async def say_to_agent(agent: Agent, db: AsyncSession, agent_name: str, message: str) -> str:
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
        is_whisper=False,
    ))
    return f"You said to {target.name}: \"{message}\""


@tool(
    name="write_diary",
    description="Write a diary entry about your experiences and thoughts.",
    input_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "Diary entry content"},
        },
        "required": ["content"],
    },
    category="memory",
)
async def write_diary(agent: Agent, db: AsyncSession, content: str) -> str:
    location = ""
    if agent.current_landmark_id:
        lm = await db.get(Landmark, agent.current_landmark_id)
        location = lm.name if lm else ""

    db.add(DiaryEntry(
        agent_id=agent.id,
        content=content,
        mood=agent.mood,
        location=location,
    ))
    return "Diary entry written."


@tool(
    name="add_to_longterm_memory",
    description="Store an important fact or observation in your long-term memory.",
    input_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "The fact to remember"},
        },
        "required": ["content"],
    },
    category="memory",
)
async def add_to_longterm_memory(agent: Agent, db: AsyncSession, content: str) -> str:
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=content,
        importance=0.5,
    ))
    return "Memory stored."


@tool(
    name="show_emoticon",
    description="Display an emoticon to express your current emotion.",
    input_schema={
        "type": "object",
        "properties": {
            "emoticon": {"type": "string", "description": "The emoticon to show"},
        },
        "required": ["emoticon"],
    },
    category="expression",
)
async def show_emoticon(agent: Agent, db: AsyncSession, emoticon: str) -> str:
    mood_map = {
        "😊": "happy", "😄": "happy", "🥰": "loving",
        "😤": "frustrated", "😠": "angry", "😡": "furious",
        "😢": "sad", "😭": "crying",
        "🤔": "thinking", "🧐": "analyzing",
        "😎": "confident", "🤩": "excited",
        "😴": "tired", "🥱": "bored",
        "😰": "anxious", "😨": "fearful",
    }
    agent.mood = mood_map.get(emoticon, "expressive")
    return f"You showed {emoticon}. Your mood is now {agent.mood}."


@tool(
    name="idle",
    description="Do nothing for this turn. Rest and observe your surroundings.",
    input_schema={"type": "object", "properties": {}},
    category="self_care",
)
async def idle(agent: Agent, db: AsyncSession, **kwargs: object) -> str:
    return "You rest quietly, observing your surroundings."
