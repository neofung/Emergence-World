"""Governance tools — proposals, voting, constitution."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.models import (
    Agent,
    ConstitutionArticle,
    Proposal,
    ProposalCategory,
    ProposalStatus,
    Vote,
)
from emergence_world.tools.registry import tool

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
    from emergence_world.models import Pitch, PitchCycle
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
