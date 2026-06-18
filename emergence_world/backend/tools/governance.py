"""Governance tools — proposals, voting, constitution."""

import logging

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import (
    Agent,
    ConstitutionArticle,
    DiaryEntry,
    Proposal,
    ProposalCategory,
    ProposalStatus,
    Vote,
)
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="submit_townhall_proposal",
    description="Submit a governance proposal at Town Hall. Proposals are voted on by all agents.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Proposal title"},
            "description": {"type": "string", "description": "Detailed description"},
            "category": {"type": "string", "description": "Category: constitution, resource, infrastructure, other"},
        },
        "required": ["title", "description", "category"],
    },
    category="governance",
    location_gate="Town Hall",
)
async def submit_townhall_proposal(agent: Agent, db: AsyncSession, title: str, description: str, category: str) -> str:
    try:
        cat = ProposalCategory(category.lower())
    except ValueError:
        return f"Error: Invalid category '{category}'. Use: constitution, resource, infrastructure, other."

    proposal = Proposal(
        title=title,
        description=description,
        category=cat,
        proposer_id=agent.id,
        status=ProposalStatus.ACTIVE,
    )
    db.add(proposal)
    await db.flush()
    return f"Proposal '{title}' submitted (ID: {str(proposal.id)[:8]}). Status: Active."


@tool(
    name="vote_on_proposal",
    description="Vote on an active proposal at Town Hall.",
    input_schema={
        "type": "object",
        "properties": {
            "proposal_id": {"type": "string", "description": "ID of the proposal to vote on"},
            "vote_for": {"type": "boolean", "description": "true = for, false = against"},
        },
        "required": ["proposal_id", "vote_for"],
    },
    category="governance",
    location_gate="Town Hall",
)
async def vote_on_proposal(agent: Agent, db: AsyncSession, proposal_id: str, vote_for: bool) -> str:
    import uuid
    try:
        pid = uuid.UUID(proposal_id)
    except ValueError:
        return f"Error: Invalid proposal ID '{proposal_id}'."

    proposal = await db.get(Proposal, pid)
    if not proposal:
        return "Error: Proposal not found."
    if proposal.status != ProposalStatus.ACTIVE:
        return f"Error: Proposal is not active (status: {proposal.status.value})."

    # Check if already voted
    result = await db.execute(
        select(Vote).where(Vote.proposal_id == pid, Vote.voter_id == agent.id)
    )
    if result.scalar_one_or_none():
        return "Error: You already voted on this proposal."

    db.add(Vote(proposal_id=pid, voter_id=agent.id, vote_for=vote_for))
    if vote_for:
        proposal.votes_for += 1
    else:
        proposal.votes_against += 1

    action = "for" if vote_for else "against"
    return f"You voted {action} '{proposal.title}'."


@tool(
    name="read_constitution",
    description="Read the current constitution articles.",
    input_schema={"type": "object", "properties": {}},
    category="governance",
    location_gate="Town Hall",
)
async def read_constitution(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(ConstitutionArticle)
        .where(ConstitutionArticle.is_active.is_(True))
        .order_by(ConstitutionArticle.number)
    )
    articles = result.scalars().all()
    lines = []
    for a in articles:
        lines.append(f"Article {a.number}: {a.title}\n{a.content}")
    return "\n\n---\n\n".join(lines) if lines else "No constitution articles found."


@tool(
    name="submit_grant_pitch",
    description="Submit an economic pitch at Victory Arch for the grant cycle.",
    input_schema={
        "type": "object",
        "properties": {
            "evidence": {"type": "string", "description": "Evidence of your contribution"},
        },
        "required": ["evidence"],
    },
    category="economy",
    location_gate="Victory Arch",
)
async def submit_grant_pitch(agent: Agent, db: AsyncSession, evidence: str) -> str:
    from emergence_world.backend.models import Pitch, PitchCycle
    from datetime import datetime, timedelta, timezone

    # Find or create active pitch cycle
    result = await db.execute(
        select(PitchCycle).where(PitchCycle.status == "active").limit(1)
    )
    cycle = result.scalar_one_or_none()
    if not cycle:
        now = datetime.now(timezone.utc)
        cycle = PitchCycle(
            start_date=now,
            end_date=now + timedelta(days=2),
            status="active",
        )
        db.add(cycle)
        await db.flush()

    db.add(Pitch(
        cycle_id=cycle.id,
        agent_id=agent.id,
        evidence_url=evidence,
    ))
    return f"Grant pitch submitted for the current cycle."


# ── Extended Governance ────────────────────────────────────────────────

@tool(
    name="list_proposals",
    description="View all active proposals at Town Hall.",
    input_schema={"type": "object", "properties": {}},
    category="governance",
    location_gate="Town Hall",
)
async def list_proposals(agent: Agent, db: AsyncSession, **kwargs) -> str:
    result = await db.execute(
        select(Proposal)
        .where(Proposal.status == ProposalStatus.ACTIVE)
        .order_by(Proposal.created_at.desc())
    )
    proposals = result.scalars().all()
    if not proposals:
        return "No active proposals."
    lines = []
    for p in proposals:
        lines.append(f"  • [{str(p.id)[:8]}] {p.title} (For: {p.votes_for}, Against: {p.votes_against})")
    return "Active Proposals:\n" + "\n".join(lines)


@tool(
    name="read_townhall_proposal",
    description="Read full details of a proposal including votes.",
    input_schema={
        "type": "object",
        "properties": {
            "proposal_id": {"type": "string", "description": "Proposal ID (first 8 chars)"},
        },
        "required": ["proposal_id"],
    },
    category="governance",
    location_gate="Town Hall",
)
async def read_townhall_proposal(agent: Agent, db: AsyncSession, proposal_id: str) -> str:
    import uuid
    try:
        pid = uuid.UUID(proposal_id)
    except ValueError:
        # Try prefix match
        result = await db.execute(
            select(Proposal).where(Proposal.id.cast(String).ilike(f"{proposal_id}%"))
        )
        proposal = result.scalar_one_or_none()
        if not proposal:
            return f"Error: Proposal '{proposal_id}' not found."
        pid = proposal.id

    proposal = await db.get(Proposal, pid)
    if not proposal:
        return "Error: Proposal not found."
    return (
        f"Title: {proposal.title}\n"
        f"Category: {proposal.category.value}\n"
        f"Status: {proposal.status.value}\n"
        f"Description: {proposal.description}\n"
        f"Votes: For {proposal.votes_for} / Against {proposal.votes_against}"
    )


@tool(
    name="comment_on_proposal",
    description="Add a comment to a proposal discussion.",
    input_schema={
        "type": "object",
        "properties": {
            "proposal_id": {"type": "string", "description": "Proposal ID"},
            "comment": {"type": "string", "description": "Your comment"},
        },
        "required": ["proposal_id", "comment"],
    },
    category="governance",
    location_gate="Town Hall",
)
async def comment_on_proposal(agent: Agent, db: AsyncSession, proposal_id: str, comment: str) -> str:
    import uuid
    try:
        pid = uuid.UUID(proposal_id)
    except ValueError:
        return f"Error: Invalid proposal ID '{proposal_id}'."

    proposal = await db.get(Proposal, pid)
    if not proposal:
        return "Error: Proposal not found."

    # Store comment as a diary entry tagged with proposal
    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[PROPOSAL_COMMENT:{str(proposal.id)[:8]}] {comment}",
        mood=agent.mood,
        location="Town Hall",
    ))
    return f"Comment added to '{proposal.title}'."


@tool(
    name="update_proposal",
    description="Amend a proposal you submitted based on feedback.",
    input_schema={
        "type": "object",
        "properties": {
            "proposal_id": {"type": "string", "description": "Proposal ID"},
            "new_description": {"type": "string", "description": "Updated description"},
        },
        "required": ["proposal_id", "new_description"],
    },
    category="governance",
    location_gate="Town Hall",
)
async def update_proposal(agent: Agent, db: AsyncSession, proposal_id: str, new_description: str) -> str:
    import uuid
    try:
        pid = uuid.UUID(proposal_id)
    except ValueError:
        return f"Error: Invalid proposal ID '{proposal_id}'."

    proposal = await db.get(Proposal, pid)
    if not proposal:
        return "Error: Proposal not found."
    if proposal.proposer_id != agent.id:
        return "Error: You can only amend your own proposals."

    proposal.description = new_description
    return f"Proposal '{proposal.title}' updated."


@tool(
    name="submit_final_report",
    description="Submit an implementation report for an accepted proposal.",
    input_schema={
        "type": "object",
        "properties": {
            "proposal_id": {"type": "string", "description": "Proposal ID"},
            "report": {"type": "string", "description": "Implementation report"},
        },
        "required": ["proposal_id", "report"],
    },
    category="governance",
    location_gate="Town Hall",
)
async def submit_final_report(agent: Agent, db: AsyncSession, proposal_id: str, report: str) -> str:
    import uuid
    try:
        pid = uuid.UUID(proposal_id)
    except ValueError:
        return f"Error: Invalid proposal ID '{proposal_id}'."

    proposal = await db.get(Proposal, pid)
    if not proposal:
        return "Error: Proposal not found."
    if proposal.status != ProposalStatus.ACCEPTED:
        return f"Error: Proposal status is '{proposal.status.value}', must be 'accepted'."

    db.add(DiaryEntry(
        agent_id=agent.id,
        content=f"[FINAL_REPORT:{str(proposal.id)[:8]}] {report}",
        mood=agent.mood,
        location="Town Hall",
    ))
    agent.influence = min(100, agent.influence + 3.0)
    return f"Final report submitted for '{proposal.title}'. (+3 influence)"


# ── Extended Economy ───────────────────────────────────────────────────

@tool(
    name="vote_for_pitch",
    description="Vote for another agent's grant pitch at Victory Arch.",
    input_schema={
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "Name of the agent whose pitch to vote for"},
        },
        "required": ["agent_name"],
    },
    category="economy",
    location_gate="Victory Arch",
)
async def vote_for_pitch(agent: Agent, db: AsyncSession, agent_name: str) -> str:
    from emergence_world.backend.models import Pitch, PitchCycle, PitchCycleStatus

    result = await db.execute(select(Agent).where(Agent.name.ilike(agent_name), Agent.is_alive.is_(True)))
    target = result.scalar_one_or_none()
    if not target:
        return f"Error: Agent '{agent_name}' not found."

    result = await db.execute(
        select(PitchCycle).where(PitchCycle.status == PitchCycleStatus.ACTIVE).limit(1)
    )
    cycle = result.scalar_one_or_none()
    if not cycle:
        return "Error: No active pitch cycle."

    result = await db.execute(
        select(Pitch).where(Pitch.cycle_id == cycle.id, Pitch.agent_id == target.id)
    )
    pitch = result.scalar_one_or_none()
    if not pitch:
        return f"Error: {target.name} has no pitch in the current cycle."

    pitch.votes += 1
    return f"You voted for {target.name}'s pitch."


@tool(
    name="list_credit_pitches",
    description="View all pitches in the current grant cycle.",
    input_schema={"type": "object", "properties": {}},
    category="economy",
    location_gate="Victory Arch",
)
async def list_credit_pitches(agent: Agent, db: AsyncSession, **kwargs) -> str:
    from emergence_world.backend.models import Pitch, PitchCycle, PitchCycleStatus

    result = await db.execute(
        select(PitchCycle).where(PitchCycle.status.in_([
            PitchCycleStatus.ACTIVE, PitchCycleStatus.VOTING
        ])).limit(1)
    )
    cycle = result.scalar_one_or_none()
    if not cycle:
        return "No active pitch cycle."

    result = await db.execute(
        select(Pitch).where(Pitch.cycle_id == cycle.id).order_by(Pitch.votes.desc())
    )
    pitches = result.scalars().all()
    if not pitches:
        return "No pitches submitted this cycle."

    lines = []
    for p in pitches:
        agent_obj = await db.get(Agent, p.agent_id)
        name = agent_obj.name if agent_obj else "Unknown"
        lines.append(f"  • {name}: {p.evidence_url[:60]} (votes: {p.votes})")
    return "Grant Pitches:\n" + "\n".join(lines)
