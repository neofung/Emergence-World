"""Extended memory tools — search, retrieve, remove."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, DiaryEntry, LongTermMemory
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="remove_from_memory",
    description="Remove a long-term memory by keyword.",
    input_schema={
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "Keyword to match in memory content"},
        },
        "required": ["keyword"],
    },
    category="memory",
)
async def remove_from_memory(agent: Agent, db: AsyncSession, keyword: str) -> str:
    result = await db.execute(
        select(LongTermMemory).where(
            LongTermMemory.agent_id == agent.id,
            LongTermMemory.content.ilike(f"%{keyword}%"),
        )
    )
    memories = result.scalars().all()
    if not memories:
        return f"No memories found matching '{keyword}'."
    count = len(memories)
    for m in memories:
        await db.delete(m)
    return f"Removed {count} memory/memories matching '{keyword}'."


@tool(
    name="retrieve_specific_memories",
    description="Search your memories by keyword.",
    input_schema={
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "Keyword to search for"},
        },
        "required": ["keyword"],
    },
    category="memory",
)
async def retrieve_specific_memories(agent: Agent, db: AsyncSession, keyword: str) -> str:
    result = await db.execute(
        select(LongTermMemory)
        .where(LongTermMemory.agent_id == agent.id, LongTermMemory.content.ilike(f"%{keyword}%"))
        .order_by(LongTermMemory.created_at.desc())
        .limit(10)
    )
    memories = result.scalars().all()
    if not memories:
        return f"No memories found matching '{keyword}'."
    lines = []
    for m in memories:
        lines.append(f"  • {m.content[:100]}")
    return f"Memories matching '{keyword}':\n" + "\n".join(lines)


@tool(
    name="search_diary_for_keywords",
    description="Search your diary entries by keyword.",
    input_schema={
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "Keyword to search for"},
        },
        "required": ["keyword"],
    },
    category="memory",
)
async def search_diary_for_keywords(agent: Agent, db: AsyncSession, keyword: str) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.agent_id == agent.id, DiaryEntry.content.ilike(f"%{keyword}%"))
        .order_by(DiaryEntry.created_at.desc())
        .limit(10)
    )
    entries = result.scalars().all()
    if not entries:
        return f"No diary entries found matching '{keyword}'."
    lines = []
    for e in entries:
        lines.append(f"  • [{e.date}] {e.content[:80]}")
    return f"Diary entries matching '{keyword}':\n" + "\n".join(lines)


@tool(
    name="show_diary_entries_from_day",
    description="View all diary entries from a specific day.",
    input_schema={
        "type": "object",
        "properties": {
            "day": {"type": "integer", "description": "Day number (1-15)"},
        },
        "required": ["day"],
    },
    category="memory",
)
async def show_diary_entries_from_day(agent: Agent, db: AsyncSession, day: int) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.agent_id == agent.id)
        .order_by(DiaryEntry.created_at.desc())
        .limit(100)
    )
    entries = result.scalars().all()
    # Filter by approximate day (entries are timestamped)
    # Simple approach: just return recent entries tagged with the day
    day_entries = [e for e in entries if f"Day {day}" in e.content or day <= 1]
    if not day_entries:
        # Fallback: return all recent entries
        day_entries = entries[:5]

    if not day_entries:
        return f"No diary entries found for Day {day}."
    lines = []
    for e in day_entries:
        lines.append(f"  [{e.date}] {e.content[:100]}")
    return f"Diary entries:\n" + "\n".join(lines)
