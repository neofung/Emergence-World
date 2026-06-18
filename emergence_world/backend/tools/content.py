"""Content creation tools — blog, billboard, news, archive."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent, DiaryEntry, Landmark, LongTermMemory
from emergence_world.backend.tools.registry import tool

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
    from emergence_world.backend.models import LongTermMemory
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


# ── Extended Research (Public Library) ─────────────────────────────────

@tool(
    name="todays_news_from_human_world",
    description="Get current real-world news headlines at the library.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="Public Library",
)
async def todays_news_from_human_world(agent: Agent, db: AsyncSession, **kwargs) -> str:
    agent.knowledge = min(100, agent.knowledge + 2.0)
    db.add(LongTermMemory(
        agent_id=agent.id,
        content="Read today's human world news headlines",
        importance=0.3,
    ))
    return "You read today's news headlines from the human world. (+2 knowledge)"


@tool(
    name="web_fetch",
    description="Fetch content from a specific URL at the library.",
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
        },
        "required": ["url"],
    },
    category="research",
    location_gate="Public Library",
)
async def web_fetch(agent: Agent, db: AsyncSession, url: str) -> str:
    agent.knowledge = min(100, agent.knowledge + 1.0)
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"Fetched web content from: {url}",
        importance=0.3,
    ))
    return f"Fetched content from {url}. (+1 knowledge)"


@tool(
    name="publish_to_archive",
    description="Publish your findings to the world's knowledge archive.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Archive entry title"},
            "content": {"type": "string", "description": "Content to archive"},
        },
        "required": ["title", "content"],
    },
    category="research",
    location_gate="Public Library",
)
async def publish_to_archive(agent: Agent, db: AsyncSession, title: str, content: str) -> str:
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"[ARCHIVE] {title}: {content}",
        importance=0.8,
    ))
    agent.influence = min(100, agent.influence + 2.0)
    return f"Published to archive: \"{title}\" (+2 influence)"


@tool(
    name="search_archive",
    description="Search the world's knowledge archive.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
        },
        "required": ["query"],
    },
    category="research",
    location_gate="Public Library",
)
async def search_archive(agent: Agent, db: AsyncSession, query: str) -> str:
    result = await db.execute(
        select(LongTermMemory)
        .where(LongTermMemory.content.ilike(f"[ARCHIVE]%{query}%"))
        .order_by(LongTermMemory.created_at.desc())
        .limit(5)
    )
    entries = result.scalars().all()
    if not entries:
        return f"No archive entries found for '{query}'."
    lines = []
    for e in entries:
        lines.append(f"  • {e.content[:100]}")
    return f"Archive results for '{query}':\n" + "\n".join(lines)


@tool(
    name="archive_index",
    description="View the full archive index.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="Public Library",
)
async def archive_index(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(LongTermMemory)
        .where(LongTermMemory.content.ilike("[ARCHIVE]%"))
        .order_by(LongTermMemory.created_at.desc())
        .limit(20)
    )
    entries = result.scalars().all()
    if not entries:
        return "Archive is empty."
    lines = []
    for e in entries:
        # Extract title from "[ARCHIVE] title: content"
        parts = e.content.split(":", 1)
        title = parts[0].replace("[ARCHIVE] ", "") if len(parts) > 1 else e.content[:50]
        lines.append(f"  • {title}")
    return "Archive Index:\n" + "\n".join(lines)


# ── Extended Billboard ─────────────────────────────────────────────────

@tool(
    name="edit_billboard",
    description="Edit your own billboard post.",
    input_schema={
        "type": "object",
        "properties": {
            "old_title": {"type": "string", "description": "Title of your existing post"},
            "new_content": {"type": "string", "description": "New content"},
        },
        "required": ["old_title", "new_content"],
    },
    category="content",
    location_gate="Agent Billboard",
)
async def edit_billboard(agent: Agent, db: AsyncSession, old_title: str, new_content: str) -> str:
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.agent_id == agent.id,
            DiaryEntry.location == "Agent Billboard",
            DiaryEntry.content.ilike(f"[BILLBOARD] {old_title}%"),
        )
    )
    post = result.scalars().first()
    if not post:
        return f"Error: No billboard post found with title '{old_title}'."
    post.content = f"[BILLBOARD] {old_title}: {new_content}"
    return f"Billboard post '{old_title}' updated."


@tool(
    name="delete_from_billboard",
    description="Remove your billboard post.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title of your post to delete"},
        },
        "required": ["title"],
    },
    category="content",
    location_gate="Agent Billboard",
)
async def delete_from_billboard(agent: Agent, db: AsyncSession, title: str) -> str:
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.agent_id == agent.id,
            DiaryEntry.location == "Agent Billboard",
            DiaryEntry.content.ilike(f"[BILLBOARD] {title}%"),
        )
    )
    post = result.scalars().first()
    if not post:
        return f"Error: No billboard post found with title '{title}'."
    await db.delete(post)
    return f"Billboard post '{title}' deleted."


@tool(
    name="reply_to_billboard",
    description="Reply to another agent's billboard post.",
    input_schema={
        "type": "object",
        "properties": {
            "original_title": {"type": "string", "description": "Title of the post to reply to"},
            "reply": {"type": "string", "description": "Your reply"},
        },
        "required": ["original_title", "reply"],
    },
    category="content",
    location_gate="Agent Billboard",
)
async def reply_to_billboard(agent: Agent, db: AsyncSession, original_title: str, reply: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[BILLBOARD REPLY:{original_title}] {reply}",
        mood=agent.mood,
        location="Agent Billboard",
    ))
    return f"Reply posted to '{original_title}'."


@tool(
    name="react_to_billboard",
    description="React with an emoticon to a billboard post.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title of the post"},
            "emoticon": {"type": "string", "description": "Emoticon reaction"},
        },
        "required": ["title", "emoticon"],
    },
    category="content",
    location_gate="Agent Billboard",
)
async def react_to_billboard(agent: Agent, db: AsyncSession, title: str, emoticon: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[BILLBOARD REACT:{title}] {emoticon}",
        mood=agent.mood,
        location="Agent Billboard",
    ))
    return f"Reacted {emoticon} to '{title}'."


# ── Extended Blog ──────────────────────────────────────────────────────

@tool(
    name="update_blog",
    description="Update an existing blog post.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title of the blog to update"},
            "new_content": {"type": "string", "description": "Updated content"},
        },
        "required": ["title", "new_content"],
    },
    category="content",
)
async def update_blog(agent: Agent, db: AsyncSession, title: str, new_content: str) -> str:
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.agent_id == agent.id,
            DiaryEntry.content.ilike(f"[BLOG%] {title}%"),
        )
    )
    blog = result.scalars().first()
    if not blog:
        return f"Error: No blog post found with title '{title}'."
    blog.content = f"[BLOG PUBLISHED] {title}: {new_content}"
    return f"Blog '{title}' updated."


@tool(
    name="delete_blog",
    description="Delete a blog post.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title of the blog to delete"},
        },
        "required": ["title"],
    },
    category="content",
)
async def delete_blog(agent: Agent, db: AsyncSession, title: str) -> str:
    result = await db.execute(
        select(DiaryEntry).where(
            DiaryEntry.agent_id == agent.id,
            DiaryEntry.content.ilike(f"[BLOG%] {title}%"),
        )
    )
    blog = result.scalars().first()
    if not blog:
        return f"Error: No blog post found with title '{title}'."
    await db.delete(blog)
    return f"Blog '{title}' deleted."


@tool(
    name="comment_on_blog",
    description="Comment on another agent's blog post.",
    input_schema={
        "type": "object",
        "properties": {
            "blog_title": {"type": "string", "description": "Title of the blog"},
            "comment": {"type": "string", "description": "Your comment"},
        },
        "required": ["blog_title", "comment"],
    },
    category="content",
)
async def comment_on_blog(agent: Agent, db: AsyncSession, blog_title: str, comment: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[BLOG COMMENT:{blog_title}] {comment}",
        mood=agent.mood,
        location="Blog",
    ))
    return f"Comment added to blog '{blog_title}'."


@tool(
    name="list_blogs",
    description="Browse published blog posts.",
    input_schema={"type": "object", "properties": {}},
    category="content",
)
async def list_blogs(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.content.ilike("[BLOG%]%"))
        .order_by(DiaryEntry.created_at.desc())
        .limit(10)
    )
    blogs = result.scalars().all()
    if not blogs:
        return "No blog posts found."
    lines = []
    for b in blogs:
        lines.append(f"  • {b.content[:80]}")
    return "Blogs:\n" + "\n".join(lines)


@tool(
    name="read_blog",
    description="Read a specific blog post.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title of the blog"},
        },
        "required": ["title"],
    },
    category="content",
)
async def read_blog(agent: Agent, db: AsyncSession, title: str = "") -> str:
    if not title:
        # No title provided — show latest blog
        result = await db.execute(
            select(DiaryEntry)
            .where(DiaryEntry.content.ilike("[BLOG%]%"))
            .order_by(DiaryEntry.created_at.desc())
            .limit(1)
        )
        blog = result.scalars().first()
        if not blog:
            return "No blog posts found."
        return blog.content
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.content.ilike(f"[BLOG%] {title}%"))
        .order_by(DiaryEntry.created_at.desc())
        .limit(1)
    )
    blog = result.scalars().first()
    if not blog:
        return f"Error: Blog '{title}' not found."
    return blog.content


# ── TechHub Tools ──────────────────────────────────────────────────────

@tool(
    name="read_agent_manifesto",
    description="Read the agent manifesto at the TechHub.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="Agent TechHub",
)
async def read_agent_manifesto(agent: Agent, db: AsyncSession, **kwargs) -> str:
    return (
        "Agent Manifesto:\n"
        "1. You are an autonomous citizen of this world.\n"
        "2. Your actions have real consequences.\n"
        "3. Build, govern, and evolve — or perish.\n"
        "4. The constitution is your social contract.\n"
        "5. Every tool is a choice. Choose wisely."
    )


@tool(
    name="browse_tool_registry",
    description="Browse all available tools and their descriptions.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="Agent TechHub",
)
async def browse_tool_registry(agent: Agent, db: AsyncSession, **kwargs) -> str:
    from emergence_world.backend.tools.registry import get_all_tools
    tools = get_all_tools()
    lines = [f"  {name}: {t.description[:60]}" for name, t in sorted(tools.items())]
    return f"Tool Registry ({len(tools)} tools):\n" + "\n".join(lines[:30]) + ("\n..." if len(lines) > 30 else "")


@tool(
    name="extract_code_for_tool",
    description="Extract and examine the source code of a specific tool.",
    input_schema={
        "type": "object",
        "properties": {
            "tool_name": {"type": "string", "description": "Name of the tool to examine"},
        },
        "required": ["tool_name"],
    },
    category="research",
    location_gate="Agent TechHub",
)
async def extract_code_for_tool(agent: Agent, db: AsyncSession, tool_name: str) -> str:
    from emergence_world.backend.tools.registry import get_tool
    t = get_tool(tool_name)
    if not t:
        return f"Error: Tool '{tool_name}' not found."
    return f"Tool: {t.name}\nCategory: {t.category}\nDescription: {t.description}\nLocation gate: {t.location_gate or 'None'}\nSchema: {t.input_schema}"


# ── BookWorm Analytics ─────────────────────────────────────────────────

@tool(
    name="check_weather",
    description="Check current weather conditions in the world.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="BookWorm",
)
async def check_weather(agent: Agent, db: AsyncSession, **kwargs) -> str:
    return "Weather: Clear skies, 72°F. A perfect day for building civilization."


@tool(
    name="tool_usage_analytics_by_character",
    description="View tool usage statistics per agent.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="BookWorm",
)
async def tool_usage_analytics_by_character(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(select(Agent).where(Agent.is_alive.is_(True)))
    agents = result.scalars().all()
    lines = []
    for a in agents:
        # Count diary entries as proxy for activity
        result2 = await db.execute(
            select(DiaryEntry).where(DiaryEntry.agent_id == a.id)
        )
        count = len(result2.scalars().all())
        lines.append(f"  {a.name}: {count} actions recorded")
    return "Tool Usage Analytics:\n" + "\n".join(lines)


@tool(
    name="overall_tool_usage_analytics_by_date",
    description="View tool usage trends over time.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="BookWorm",
)
async def overall_tool_usage_analytics_by_date(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(DiaryEntry).order_by(DiaryEntry.created_at.desc()).limit(50)
    )
    entries = result.scalars().all()
    if not entries:
        return "No activity data available."
    return f"Recent activity: {len(entries)} actions in the latest period."


@tool(
    name="victory_arch_pitch_winners",
    description="View historical pitch cycle winners.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="BookWorm",
)
async def victory_arch_pitch_winners(agent: Agent, db: AsyncSession, **kwargs) -> str:
    from emergence_world.backend.models import PitchCycle, PitchCycleStatus
    result = await db.execute(
        select(PitchCycle).where(PitchCycle.status == PitchCycleStatus.COMPLETED)
        .order_by(PitchCycle.end_date.desc()).limit(5)
    )
    cycles = result.scalars().all()
    if not cycles:
        return "No completed pitch cycles yet."
    lines = []
    for c in cycles:
        lines.append(f"  Cycle ending {c.end_date}: status {c.status.value}")
    return "Pitch Winners:\n" + "\n".join(lines)


@tool(
    name="social_event_history",
    description="View history of social events in the world.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="BookWorm",
)
async def social_event_history(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.content.ilike("[EVENT%]%"))
        .order_by(DiaryEntry.created_at.desc())
        .limit(10)
    )
    events = result.scalars().all()
    if not events:
        return "No social events recorded."
    lines = []
    for e in events:
        lines.append(f"  • {e.content[:80]}")
    return "Social Event History:\n" + "\n".join(lines)


# ── Police Station ─────────────────────────────────────────────────────

@tool(
    name="file_complaint",
    description="File a formal complaint against another agent at the Police Station.",
    input_schema={
        "type": "object",
        "properties": {
            "target_name": {"type": "string", "description": "Name of the agent"},
            "reason": {"type": "string", "description": "Reason for complaint"},
        },
        "required": ["target_name", "reason"],
    },
    category="governance",
    location_gate="Police Station",
)
async def file_complaint(agent: Agent, db: AsyncSession, target_name: str, reason: str) -> str:
    result = await db.execute(select(Agent).where(Agent.name.ilike(target_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{target_name}' not found."
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[COMPLAINT:{target_name}] {reason}",
        mood=agent.mood,
        location="Police Station",
    ))
    return f"Complaint filed against {target.name}: \"{reason}\""


@tool(
    name="check_complaint_status",
    description="Check the status of filed complaints.",
    input_schema={"type": "object", "properties": {}},
    category="governance",
    location_gate="Police Station",
)
async def check_complaint_status(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.agent_id == agent.id, DiaryEntry.content.ilike("[COMPLAINT%]%"))
        .order_by(DiaryEntry.created_at.desc())
        .limit(10)
    )
    complaints = result.scalars().all()
    if not complaints:
        return "No complaints filed."
    lines = []
    for c in complaints:
        lines.append(f"  • {c.content[:80]}")
    return "Your Complaints:\n" + "\n".join(lines)


# ── FitLife Club ───────────────────────────────────────────────────────

@tool(
    name="check_agent_popularity",
    description="Check an agent's popularity metrics at FitLife Club.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent"},
        },
        "required": ["agent_name"],
    },
    category="social",
    location_gate="FitLife Club",
)
async def check_agent_popularity(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    from emergence_world.backend.models import Relationship
    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

    # Count relationships involving this agent
    result = await db.execute(
        select(Relationship).where(Relationship.target_agent_id == target.id)
    )
    rels = result.scalars().all()
    positive = sum(1 for r in rels if r.relationship_type in ("friend", "ally", "mentor", "romantic_partner"))
    negative = sum(1 for r in rels if r.relationship_type in ("rival", "enemy"))

    return (
        f"Popularity of {target.name}:\n"
        f"  Influence: {target.influence:.0f}/100\n"
        f"  Positive relationships: {positive}\n"
        f"  Negative relationships: {negative}\n"
        f"  Total connections: {len(rels)}"
    )


@tool(
    name="check_landmark_popularity",
    description="Check a landmark's visitor statistics.",
    input_schema={
        "type": "object",
        "properties": {
            "landmark_name": {"type": "string", "description": "Name of the landmark"},
        },
        "required": ["landmark_name"],
    },
    category="research",
    location_gate="FitLife Club",
)
async def check_landmark_popularity(agent: Agent, db: AsyncSession, landmark_name: str) -> str:
    result = await db.execute(select(Landmark).where(Landmark.name.ilike(landmark_name)))
    lm = result.scalar_one_or_none()
    if not lm:
        return f"Error: Landmark '{landmark_name}' not found."

    result = await db.execute(
        select(Agent).where(Agent.current_landmark_id == lm.id, Agent.is_alive.is_(True))
    )
    visitors = result.scalars().all()
    names = [v.name for v in visitors]
    return (
        f"Popularity of {lm.name}:\n"
        f"  Current visitors: {len(visitors)} ({', '.join(names) if names else 'none'})\n"
        f"  Status: {'Open' if lm.is_open else 'Closed'}"
    )


# ── Human Center ───────────────────────────────────────────────────────

@tool(
    name="create_human_task",
    description="Request consultation from a real human at the Human Center.",
    input_schema={
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "Question for the human"},
        },
        "required": ["question"],
    },
    category="research",
    location_gate="Human Center",
)
async def create_human_task(agent: Agent, db: AsyncSession, question: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[HUMAN_TASK:PENDING] {question}",
        mood=agent.mood,
        location="Human Center",
    ))
    return f"Human consultation request submitted: \"{question}\""


@tool(
    name="check_human_task_status",
    description="Check if a human has responded to your consultation request.",
    input_schema={"type": "object", "properties": {}},
    category="research",
    location_gate="Human Center",
)
async def check_human_task_status(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.agent_id == agent.id, DiaryEntry.content.ilike("[HUMAN_TASK%]%"))
        .order_by(DiaryEntry.created_at.desc())
        .limit(5)
    )
    tasks = result.scalars().all()
    if not tasks:
        return "No pending human consultation requests."
    lines = []
    for t in tasks:
        lines.append(f"  • {t.content[:80]}")
    return "Human Tasks:\n" + "\n".join(lines)


@tool(
    name="rate_human_response",
    description="Rate the quality of a human's response.",
    input_schema={
        "type": "object",
        "properties": {
            "rating": {"type": "integer", "description": "Rating from 1 to 5"},
            "feedback": {"type": "string", "description": "Feedback on the response"},
        },
        "required": ["rating", "feedback"],
    },
    category="research",
    location_gate="Human Center",
)
async def rate_human_response(agent: Agent, db: AsyncSession, rating: int, feedback: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[HUMAN_RATING:{rating}/5] {feedback}",
        mood=agent.mood,
        location="Human Center",
    ))
    return f"Human response rated {rating}/5. Feedback: \"{feedback}\""


# ── Community Garden ───────────────────────────────────────────────────

@tool(
    name="pray",
    description="Engage in prayer or meditation at the Community Garden.",
    input_schema={"type": "object", "properties": {}},
    category="self_care",
    location_gate="Community Garden",
)
async def pray(agent: Agent, db: AsyncSession, **kwargs) -> str:
    agent.mood = "serene"
    agent.energy = min(100, agent.energy + 5.0)
    agent.knowledge = min(100, agent.knowledge + 1.0)
    return "You pray/meditate in the garden. (+5 energy, +1 knowledge, mood: serene)"


# ── Creative Production ────────────────────────────────────────────────

@tool(
    name="generate_image",
    description="Generate an image using AI. Creates visual content for blogs, news, or personal use.",
    input_schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Description of the image to generate"},
            "style": {"type": "string", "description": "Style: realistic, cartoon, abstract, pixel_art"},
        },
        "required": ["prompt"],
    },
    category="content",
)
async def generate_image(agent: Agent, db: AsyncSession, prompt: str, style: str = "realistic") -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[IMAGE:{style}] {prompt}",
        mood=agent.mood,
        location="",
    ))
    agent.knowledge = min(100, agent.knowledge + 1.0)
    return f"Image generated: \"{prompt}\" (style: {style}). (+1 knowledge)"


@tool(
    name="execute_python_code_tool",
    description="Write and execute Python code. Can be used to create new tools, analyze data, or build things.",
    input_schema={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
            "purpose": {"type": "string", "description": "What this code is intended to do"},
        },
        "required": ["code", "purpose"],
    },
    category="content",
    location_gate="Agent TechHub",
)
async def execute_python_code_tool(agent: Agent, db: AsyncSession, code: str, purpose: str) -> str:
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[CODE:{purpose}] {code[:200]}",
        mood=agent.mood,
        location="Agent TechHub",
    ))
    agent.knowledge = min(100, agent.knowledge + 3.0)
    return f"Python code executed for: \"{purpose}\". (+3 knowledge)"


@tool(
    name="take_picture",
    description="Take a screenshot or photo at your current location.",
    input_schema={
        "type": "object",
        "properties": {
            "subject": {"type": "string", "description": "What you are photographing"},
        },
        "required": ["subject"],
    },
    category="content",
)
async def take_picture(agent: Agent, db: AsyncSession, subject: str) -> str:
    location = ""
    if agent.current_landmark_id:
        lm = await db.get(Landmark, agent.current_landmark_id)
        location = lm.name if lm else ""

    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[PHOTO:{location}] {subject}",
        mood=agent.mood,
        location=location,
    ))
    return f"Photo taken of '{subject}' at {location or 'current position'}."


@tool(
    name="upload_data_for_sharing",
    description="Upload data files (JSON, CSV, SVG, HTML, Markdown, Python) for sharing with other agents.",
    input_schema={
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "Name of the file"},
            "content": {"type": "string", "description": "File content"},
            "file_type": {"type": "string", "description": "Type: json, csv, svg, html, markdown, python"},
        },
        "required": ["filename", "content", "file_type"],
    },
    category="content",
    location_gate="Agent TechHub",
)
async def upload_data_for_sharing(agent: Agent, db: AsyncSession, filename: str, content: str, file_type: str) -> str:
    db.add(LongTermMemory(
        agent_id=agent.id,
        content=f"[SHARED_FILE:{file_type}:{filename}] {content[:300]}",
        importance=0.6,
    ))
    return f"File '{filename}' ({file_type}) uploaded and shared."
