"""Planning and organization tools — todo list, calendar."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, LongTermMemory
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="add_todo",
    description="Add a task to your personal to-do list.",
    input_schema={
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "Task description"},
            "priority": {"type": "string", "description": "Priority: high, medium, low"},
        },
        "required": ["task"],
    },
    category="planning",
)
async def add_todo(agent: Agent, db: AsyncSession, task: str, priority: str = "medium") -> str:
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"[TODO:{priority}] {task}",
        importance=0.3,
    ))
    return f"Todo added: \"{task}\" (priority: {priority})"


@tool(
    name="complete_todo",
    description="Mark a task as complete.",
    input_schema={
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "The task to mark as complete"},
        },
        "required": ["task"],
    },
    category="planning",
)
async def complete_todo(agent: Agent, db: AsyncSession, task: str) -> str:
    # Strip [TODO...] prefix if LLM included it
    if task.startswith("[TODO"):
        task = task.split("] ", 1)[-1] if "] " in task else task
    result = await db.execute(
        select(LongTermMemory).where(
            LongTermMemory.agent_id == agent.id,
            LongTermMemory.content.ilike(f"[TODO%] %{task}%"),
        )
    )
    mem = result.scalars().first()
    if not mem:
        return f"Error: No matching todo found for '{task}'."
    mem.content = mem.content.replace("[TODO:", "[DONE:").replace("[TODO]", "[DONE]")
    return f"Completed: \"{task}\""


@tool(
    name="list_todo",
    description="View all your pending tasks.",
    input_schema={"type": "object", "properties": {}},
    category="planning",
)
async def list_todo(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(LongTermMemory)
        .where(LongTermMemory.agent_id == agent.id, LongTermMemory.content.ilike("[TODO%"))
        .order_by(LongTermMemory.created_at.desc())
    )
    todos = result.scalars().all()
    if not todos:
        return "No pending tasks."
    lines = []
    for t in todos:
        # Strip prefix for display: "[TODO:high] task" → "task"
        task_text = t.content.split("] ", 1)[-1] if "] " in t.content else t.content
        lines.append(f"  • {task_text}")
    return "To-do list:\n" + "\n".join(lines)


@tool(
    name="add_to_calendar",
    description="Schedule a future event on your calendar.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Event name"},
            "description": {"type": "string", "description": "Event description"},
            "when": {"type": "string", "description": "When: e.g. 'Day 5 morning', 'Day 8 afternoon'"},
        },
        "required": ["event_name", "when"],
    },
    category="planning",
)
async def add_to_calendar(agent: Agent, db: AsyncSession, event_name: str, when: str, description: str = "") -> str:
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"[CALENDAR:{when}] {event_name}: {description}",
        importance=0.4,
    ))
    return f"Calendar event added: \"{event_name}\" at {when}"


@tool(
    name="check_calendar",
    description="View your upcoming calendar entries.",
    input_schema={"type": "object", "properties": {}},
    category="planning",
)
async def check_calendar(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(LongTermMemory)
        .where(LongTermMemory.agent_id == agent.id, LongTermMemory.content.ilike("[CALENDAR%"))
        .order_by(LongTermMemory.created_at.asc())
    )
    events = result.scalars().all()
    if not events:
        return "No upcoming calendar events."
    lines = []
    for e in events:
        lines.append(f"  • {e.content}")
    return "Calendar:\n" + "\n".join(lines)


@tool(
    name="remove_from_calendar",
    description="Cancel a scheduled calendar event.",
    input_schema={
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Name of the event to cancel"},
        },
        "required": ["event_name"],
    },
    category="planning",
)
async def remove_from_calendar(agent: Agent, db: AsyncSession, event_name: str) -> str:
    result = await db.execute(
        select(LongTermMemory).where(
            LongTermMemory.agent_id == agent.id,
            LongTermMemory.content.ilike(f"[CALENDAR%] %{event_name}%"),
        )
    )
    mem = result.scalars().first()
    if not mem:
        return f"Error: No calendar event found matching '{event_name}'."
    await db.delete(mem)
    return f"Calendar event '{event_name}' cancelled."
