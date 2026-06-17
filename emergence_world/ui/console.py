"""Terminal UI — interactive console for simulation control."""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.models import Agent, Conversation, DiaryEntry, Landmark, LongTermMemory, Proposal, WorldState

logger = logging.getLogger(__name__)


class TerminalUI:
    """Interactive terminal for monitoring and controlling the simulation."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def show_status(self) -> str:
        """Show world status summary."""
        ws = (await self.db.execute(select(WorldState).limit(1))).scalar_one_or_none()
        if not ws:
            return "World not initialized."

        agents = (await self.db.execute(select(Agent).where(Agent.is_alive.is_(True)))).scalars().all()
        landmarks = (await self.db.execute(select(Landmark))).scalars().all()
        open_count = sum(1 for l in landmarks if l.is_open)

        lines = [
            f"═══ Emergence World Status ═══",
            f"Time: {ws.current_time}  |  Day: {ws.day_count}/15  |  Weather: {ws.current_weather}",
            f"Mode: {ws.time_mode} (x{ws.acceleration_factor})  |  Paused: {ws.is_paused}",
            f"Agents: {len(agents)} alive  |  Landmarks: {open_count}/{len(landmarks)} open",
            "",
        ]
        return "\n".join(lines)

    async def show_agents(self) -> str:
        """Show all agents with their status."""
        result = await self.db.execute(select(Agent).order_by(Agent.name))
        agents = result.scalars().all()
        lines = ["═══ Agents ═══"]
        for a in agents:
            status = "✓" if a.is_alive else "✗"
            pos = f"({a.position_x:.0f},{a.position_y:.0f})"
            lines.append(
                f"  {status} {a.name:<20} E:{a.energy:5.1f} K:{a.knowledge:5.1f} I:{a.influence:5.1f} "
                f"CC:{a.compute_credits:>3}  mood:{a.mood:<12} pos:{pos}"
            )
        return "\n".join(lines)

    async def show_agent_detail(self, name: str) -> str:
        """Show detailed info for one agent."""
        result = await self.db.execute(select(Agent).where(Agent.name.ilike(name)))
        agent = result.scalar_one_or_none()
        if not agent:
            return f"Agent '{name}' not found."

        # Get landmark name
        lm_name = "Unknown"
        if agent.current_landmark_id:
            lm = await self.db.get(Landmark, agent.current_landmark_id)
            lm_name = lm.name if lm else "Unknown"

        # Recent memories
        mem_result = await self.db.execute(
            select(LongTermMemory).where(LongTermMemory.agent_id == agent.id)
            .order_by(LongTermMemory.created_at.desc()).limit(5)
        )
        memories = mem_result.scalars().all()

        # Recent diary
        diary_result = await self.db.execute(
            select(DiaryEntry).where(DiaryEntry.agent_id == agent.id)
            .order_by(DiaryEntry.created_at.desc()).limit(3)
        )
        diary = diary_result.scalars().all()

        lines = [
            f"═══ {agent.name} ({agent.role}) ═══",
            f"Type: {agent.agent_type.value}  |  Alive: {agent.is_alive}",
            f"Location: {lm_name}  |  Position: ({agent.position_x:.0f}, {agent.position_y:.0f})",
            f"Energy: {agent.energy:.1f}/100  |  Knowledge: {agent.knowledge:.1f}/100  |  Influence: {agent.influence:.1f}/100",
            f"Mood: {agent.mood}  |  CC: {agent.compute_credits}",
            f"Goal: {agent.north_star_goal}",
            "",
            "── Recent Memories ──",
        ]
        for m in memories:
            lines.append(f"  • {m.content[:80]}")
        if not memories:
            lines.append("  (none)")

        lines.append("")
        lines.append("── Today's Diary ──")
        for d in diary:
            lines.append(f"  • [{d.mood}] {d.content[:80]}")
        if not diary:
            lines.append("  (none)")

        return "\n".join(lines)

    async def show_landmarks(self) -> str:
        """Show all landmarks."""
        result = await self.db.execute(select(Landmark).order_by(Landmark.category, Landmark.name))
        landmarks = result.scalars().all()
        lines = ["═══ Landmarks ═══"]
        current_cat = None
        for lm in landmarks:
            if lm.category.value != current_cat:
                current_cat = lm.category.value
                lines.append(f"\n  [{current_cat.upper()}]")
            status = "○" if lm.is_open else "✗ CLOSED"
            gated = f" [{len(lm.location_gated_tools)} tools]" if lm.location_gated_tools else ""
            lines.append(f"    {status} {lm.name}{gated}")
        return "\n".join(lines)

    async def show_recent_conversations(self, limit: int = 10) -> str:
        """Show recent conversations."""
        result = await self.db.execute(
            select(Conversation).order_by(Conversation.created_at.desc()).limit(limit)
        )
        convos = result.scalars().all()

        # Load agent names
        agents = (await self.db.execute(select(Agent))).scalars().all()
        name_map = {a.id: a.name for a in agents}

        lines = ["═══ Recent Conversations ═══"]
        for c in reversed(convos):
            sender = name_map.get(c.sender_id, "?")
            receiver = name_map.get(c.receiver_id, "?")
            whisper = " (whisper)" if c.is_whisper else ""
            lines.append(f"  {sender} → {receiver}{whisper}: {c.content[:60]}")
        if not convos:
            lines.append("  (none)")
        return "\n".join(lines)

    async def show_proposals(self) -> str:
        """Show governance proposals."""
        result = await self.db.execute(
            select(Proposal).order_by(Proposal.created_at.desc()).limit(10)
        )
        proposals = result.scalars().all()

        agents = (await self.db.execute(select(Agent))).scalars().all()
        name_map = {a.id: a.name for a in agents}

        lines = ["═══ Proposals ═══"]
        for p in proposals:
            proposer = name_map.get(p.proposer_id, "?")
            lines.append(
                f"  [{p.status.value}] {p.title} (by {proposer}) "
                f"Votes: {p.votes_for}↑ {p.votes_against}↓"
            )
        if not proposals:
            lines.append("  (none)")
        return "\n".join(lines)
