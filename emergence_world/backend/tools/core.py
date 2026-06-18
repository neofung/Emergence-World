"""Core P0 tools — always available regardless of location."""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, Conversation, DiaryEntry, Landmark, LongTermMemory
from emergence_world.backend.tools.registry import tool

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


@tool(
    name="go_home",
    description="Return to your assigned residence.",
    input_schema={"type": "object", "properties": {}},
    category="navigation",
)
async def go_home(agent: Agent, db: AsyncSession, **kwargs: object) -> str:
    if not agent.home_id:
        return "Error: You don't have an assigned home."
    landmark = await db.get(Landmark, agent.home_id)
    if not landmark:
        return "Error: Home landmark not found."
    agent.position_x = landmark.position_x
    agent.position_y = landmark.position_y
    agent.position_z = landmark.position_z
    agent.current_landmark_id = landmark.id
    return f"You returned home to {landmark.name}."


@tool(
    name="turn_towards",
    description="Face a specific agent. A social gesture of attention.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent to face"},
        },
        "required": ["agent_name"],
    },
    category="navigation",
)
async def turn_towards(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."
    return f"You turn to face {target.name}."


@tool(
    name="set_mood_and_terminate",
    description="Set your current emotional state and end your turn.",
    input_schema={
        "type": "object",
        "properties": {
            "mood": {"type": "string", "description": "Your mood: happy, sad, angry, fearful, excited, tired, neutral, anxious, confident, loving"},
        },
        "required": ["mood"],
    },
    category="expression",
)
async def set_mood_and_terminate(agent: Agent, db: AsyncSession, mood: str) -> str:
    agent.mood = mood.lower()
    return f"Mood set to {agent.mood}. Turn ended."


@tool(
    name="think_aloud",
    description="Express your internal monologue. Agents nearby can observe your thoughts.",
    input_schema={
        "type": "object",
        "properties": {
            "thought": {"type": "string", "description": "Your internal thought"},
        },
        "required": ["thought"],
    },
    category="expression",
)
async def think_aloud(agent: Agent, db: AsyncSession, thought: str) -> str:
    location = ""
    if agent.current_landmark_id:
        lm = await db.get(Landmark, agent.current_landmark_id)
        location = lm.name if lm else ""
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[THOUGHT] {thought}",
        mood=agent.mood,
        location=location,
    ))
    return f"You thought: \"{thought}\""


@tool(
    name="ignore",
    description="Explicitly choose to ignore something. A deliberate non-action.",
    input_schema={
        "type": "object",
        "properties": {
            "what": {"type": "string", "description": "What you are choosing to ignore"},
        },
        "required": ["what"],
    },
    category="utility",
)
async def ignore(agent: Agent, db: AsyncSession, what: str) -> str:
    return f"You deliberately ignore {what}."
