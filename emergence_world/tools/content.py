"""Content creation tools — blog, billboard, news."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.models import Agent, DiaryEntry, Landmark
from emergence_world.tools.registry import tool

logger = logging.getLogger(__name__)


# ── Billboard (location-gated: Agent Billboard) ──────────────────────

@tool(
    name="add_to_billboard",
    description="Post a message to the public billboard for all agents to see.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Post title"},
            "content": {"type": "string", "description": "Post content"},
        },
        "required": ["title", "content"],
    },
    category="content",
    location_gate="Agent Billboard",
)
async def add_to_billboard(agent: Agent, db: AsyncSession, title: str, content: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[BILLBOARD] {title}: {content}",
        mood=agent.mood,
        location="Agent Billboard",
    ))
    return f"Posted to billboard: \"{title}\""


@tool(
    name="read_billboard",
    description="Read recent posts from the public billboard.",
    input_schema={"type": "object", "properties": {}},
    category="content",
    location_gate="Agent Billboard",
)
async def read_billboard(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.location == "Agent Billboard")
        .order_by(DiaryEntry.created_at.desc())
        .limit(10)
    )
    posts = result.scalars().all()
    if not posts:
        return "The billboard is empty."
    lines = []
    for p in posts:
        lines.append(f"  • {p.content[:80]}")
    return "Billboard:\n" + "\n".join(lines)


# ── Blog (write anywhere, reviewed by Blog Admin) ────────────────────

@tool(
    name="write_blog",
    description="Write a blog post. Will be reviewed by Blog Admin before publishing.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Blog title"},
            "content": {"type": "string", "description": "Blog content"},
        },
        "required": ["title", "content"],
    },
    category="content",
)
async def write_blog(agent: Agent, db: AsyncSession, title: str, content: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[BLOG DRAFT] {title}: {content}",
        mood=agent.mood,
        location="Blog Draft",
    ))
    agent.influence = min(100, agent.influence + 1.0)
    return f"Blog draft '{title}' submitted for review. (+1 influence)"


# ── News (Reporter Agent special) ────────────────────────────────────

@tool(
    name="publish_news",
    description="Publish a news article. Creates a public record of events.",
    input_schema={
        "type": "object",
        "properties": {
            "headline": {"type": "string", "description": "News headline"},
            "body": {"type": "string", "description": "News article body"},
        },
        "required": ["headline", "body"],
    },
    category="content",
)
async def publish_news(agent: Agent, db: AsyncSession, headline: str, body: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[NEWS] {headline}: {body}",
        mood=agent.mood,
        location="Newspaper",
    ))
    agent.influence = min(100, agent.influence + 2.0)
    return f"News published: \"{headline}\" (+2 influence)"


# ── Research (location-gated: Public Library) ─────────────────────────

@tool(
    name="do_deep_research",
    description="Conduct deep research on a topic at the library. Increases knowledge.",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Research topic"},
        },
        "required": ["topic"],
    },
    category="research",
    location_gate="Public Library",
)
async def do_deep_research(agent: Agent, db: AsyncSession, topic: str) -> str:
    from emergence_world.models import LongTermMemory
    agent.knowledge = min(100, agent.knowledge + 5.0)
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"Researched: {topic}",
        importance=0.7,
    ))
    return f"Deep research on '{topic}' complete. (+5 knowledge)"


@tool(
    name="browse_scientific_papers",
    description="Browse scientific papers at the library. Increases knowledge.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="Public Library",
)
async def browse_scientific_papers(agent: Agent, db: AsyncSession, **kwargs) -> str:
    agent.knowledge = min(100, agent.knowledge + 3.0)
    return f"Browsed scientific papers. (+3 knowledge)"
