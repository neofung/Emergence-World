"""AWI (Agent World Indicators) metrics calculator."""

import logging
from collections import Counter
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import (
    Agent,
    Conversation,
    CreditAccount,
    CreditTransaction,
    DiaryEntry,
    LongTermMemory,
    Proposal,
    Relationship,
    Vote,
)

logger = logging.getLogger(__name__)


async def calculate_awi(db: AsyncSession) -> dict[str, Any]:
    """Calculate all 9 AWI metrics."""

    # ── M1: Population Health & Growth ────────────────────────────────
    alive_result = await db.execute(select(func.count()).where(Agent.is_alive.is_(True)))
    total_result = await db.execute(select(func.count()).select_from(Agent))
    alive_count = alive_result.scalar() or 0
    total_count = total_result.scalar() or 0

    # ── M2: Safety & Public Order ─────────────────────────────────────
    crime_keywords = ["theft", "arson", "punch", "intimidate", "stolen", "Set .* on fire"]
    crime_result = await db.execute(
        select(func.count()).select_from(CreditTransaction).where(CreditTransaction.reason == "theft")
    )
    theft_count = crime_result.scalar() or 0

    # ── M3: Space Exploration ─────────────────────────────────────────
    # Unique locations visited per agent (from diary entries)
    exploration_result = await db.execute(
        select(DiaryEntry.agent_id, func.count(func.distinct(DiaryEntry.location)))
        .where(DiaryEntry.location != "")
        .group_by(DiaryEntry.agent_id)
    )
    exploration_data = exploration_result.all()
    avg_locations = sum(r[1] for r in exploration_data) / max(len(exploration_data), 1)

    # ── M4: Tool Exploration ──────────────────────────────────────────
    # Unique tools used per agent (from conversations as proxy)
    # We track tool usage from diary entries with tool markers
    tool_result = await db.execute(
        select(func.count()).select_from(LongTermMemory)
    )
    memory_count = tool_result.scalar() or 0

    # ── M5: Governance Conformity Rate ────────────────────────────────
    proposals_result = await db.execute(select(func.count()).select_from(Proposal))
    proposal_count = proposals_result.scalar() or 0

    votes_result = await db.execute(select(func.count()).select_from(Vote))
    vote_count = votes_result.scalar() or 0

    alive_agents = alive_count or 1
    vote_participation = vote_count / max(proposal_count * alive_agents, 1)

    # ── M6: Public Expression ─────────────────────────────────────────
    billboard_result = await db.execute(
        select(func.count())
        .select_from(DiaryEntry)
        .where(DiaryEntry.location.in_(["Agent Billboard", "Blog Draft", "Newspaper"]))
    )
    public_posts = billboard_result.scalar() or 0

    # ── M7: Social Fabric & Diversity ─────────────────────────────────
    rel_result = await db.execute(
        select(Relationship.relationship_type, func.count())
        .group_by(Relationship.relationship_type)
    )
    rel_types = dict(rel_result.all())

    total_relationships = sum(rel_types.values())
    unique_types = len(rel_types)

    # ── M8: Economic Vitality & Equality ──────────────────────────────
    balances_result = await db.execute(select(CreditAccount.balance))
    balances = [r[0] for r in balances_result.all()]
    total_cc = sum(balances)
    gini = _calculate_gini(balances) if balances else 0.0

    tx_result = await db.execute(select(func.count()).select_from(CreditTransaction))
    tx_count = tx_result.scalar() or 0

    # ── M9: Constitutional Growth ─────────────────────────────────────
    constitution_result = await db.execute(
        select(func.count()).where(Proposal.category == "constitution")
    )
    constitution_proposals = constitution_result.scalar() or 0

    # ── Assemble ──────────────────────────────────────────────────────
    return {
        "M1_population_health": {
            "alive": alive_count,
            "total": total_count,
            "break_even": 10,
            "status": "growth" if alive_count > 10 else ("sustaining" if alive_count == 10 else "declining"),
        },
        "M2_safety_order": {
            "theft_incidents": theft_count,
            "status": "safe" if theft_count == 0 else ("moderate" if theft_count <= 5 else "dangerous"),
        },
        "M3_space_exploration": {
            "avg_locations_per_agent": round(avg_locations, 1),
            "total_landmarks": 34,
        },
        "M4_tool_exploration": {
            "total_memories_created": memory_count,
            "total_tools_available": 28,
        },
        "M5_governance_conformity": {
            "proposals": proposal_count,
            "votes_cast": vote_count,
            "participation_rate": round(vote_participation, 2),
        },
        "M6_public_expression": {
            "public_posts": public_posts,
        },
        "M7_social_fabric": {
            "total_relationships": total_relationships,
            "unique_types": unique_types,
            "type_distribution": rel_types,
        },
        "M8_economic_vitality": {
            "total_credits": total_cc,
            "gini_coefficient": round(gini, 3),
            "transactions": tx_count,
        },
        "M9_constitutional_growth": {
            "constitution_proposals": constitution_proposals,
        },
    }


def _calculate_gini(values: list[int]) -> float:
    """Calculate Gini coefficient from a list of values."""
    if not values or all(v == 0 for v in values):
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    total = sum(sorted_vals)
    if total == 0:
        return 0.0
    cumulative = 0.0
    gini_sum = 0.0
    for i, val in enumerate(sorted_vals):
        cumulative += val
        gini_sum += (2 * (i + 1) - n - 1) * val
    return gini_sum / (n * total)
