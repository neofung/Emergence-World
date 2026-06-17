"""Simulation engine — core turn loop."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from emergence_world.agents.prompt import build_system_prompt
from emergence_world.config import get_settings
from emergence_world.core.llm import LLMClient
from emergence_world.core.scheduler import Scheduler
from emergence_world.models import Agent, Conversation, Landmark, LongTermMemory, Relationship, WorldState

logger = logging.getLogger(__name__)
settings = get_settings()


class SimulationEngine:
    """Main simulation loop — drives agent turns."""

    def __init__(self, db: AsyncSession, llm: LLMClient) -> None:
        self.db = db
        self.llm = llm
        self.scheduler = Scheduler()
        self._running = False
        self._paused = False
        self._world_state: WorldState | None = None

    async def initialize(self) -> None:
        """Load world state and alive agents into scheduler."""
        result = await self.db.execute(select(WorldState).limit(1))
        self._world_state = result.scalar_one_or_none()
        if not self._world_state:
            raise RuntimeError("WorldState not found — run seed loader first")

        result = await self.db.execute(
            select(Agent.id).where(Agent.is_alive.is_(True)).order_by(Agent.name)
        )
        agent_ids = [row[0] for row in result.fetchall()]
        self.scheduler.set_agents(agent_ids)
        logger.info(f"Simulation initialized: {len(agent_ids)} agents, day {self._world_state.day_count}")

    async def run(self) -> None:
        """Main simulation loop."""
        self._running = True
        logger.info("Simulation started")

        while self._running:
            if self._paused:
                await self._sleep(0.5)
                continue

            if not self._world_state:
                break

            # Check end conditions
            if self._world_state.day_count > 15:
                logger.info("Simulation complete: 15 days reached")
                break

            agent_id = self.scheduler.next_agent()
            if agent_id is None:
                logger.info("No agents remaining — simulation ended")
                break

            try:
                await self._execute_turn(agent_id)
            except Exception as e:
                logger.error(f"Turn failed for agent {agent_id}: {e}")

            # Advance simulation time
            await self._advance_time()

    async def _execute_turn(self, agent_id: uuid.UUID) -> None:
        """Execute a single agent turn."""
        # Load agent with relationships
        result = await self.db.execute(
            select(Agent)
            .options(selectinload(Agent.home), selectinload(Agent.current_landmark))
            .where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        if not agent or not agent.is_alive:
            return

        # 1. Needs decay
        self._update_needs(agent)

        # 2. Get current landmark
        landmark_name = agent.current_landmark.name if agent.current_landmark else "Unknown"

        # 3. Find nearby agents
        nearby = await self._find_nearby_agents(agent)

        # 4. Load memories
        soul_entries = await self._load_soul(agent_id)
        memories = await self._load_memories(agent_id)
        diary = await self._load_diary(agent_id)
        relationships = await self._load_relationships(agent_id)

        # 5. Build system prompt
        system_prompt = build_system_prompt(
            agent=agent,
            landmark_name=landmark_name,
            nearby_agents=[n["name"] for n in nearby],
            soul_entries=soul_entries,
            memories=memories,
            diary_entries=diary,
            relationships=relationships,
            current_time=str(self._world_state.current_time) if self._world_state else "unknown",
            weather=self._world_state.current_weather if self._world_state else "clear",
            day_count=self._world_state.day_count if self._world_state else 1,
        )

        # 6. Load available tools (core + location-gated)
        tools = self._get_available_tools(agent)

        # 7. Call LLM
        messages = [{"role": "system", "content": system_prompt}]
        try:
            response = await self.llm.chat_completion(messages, tools=tools if tools else None)
            choice = response.choices[0]

            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    logger.info(
                        f"[{agent.name}] [{landmark_name}] {tc.function.name}({tc.function.arguments})"
                    )
            elif choice.message.content:
                logger.info(f"[{agent.name}] [{landmark_name}] says: {choice.message.content[:100]}")

        except Exception as e:
            logger.error(f"[{agent.name}] LLM call failed: {e}")

        # 8. Check death
        if agent.energy <= 0:
            if agent.death_timer is None:
                agent.death_timer = settings.death_countdown_hours
            elif agent.death_timer <= 0:
                agent.is_alive = False
                self.scheduler.remove_agent(agent.id)
                logger.info(f"[{agent.name}] has died (energy depleted)")

        await self.db.commit()

    def _update_needs(self, agent: Agent) -> None:
        """Decay agent needs based on elapsed time."""
        # Simplified: decay a small amount per turn
        decay = 0.1  # ~0.1% per turn
        agent.energy = max(0, agent.energy - decay)
        agent.knowledge = max(0, agent.knowledge - decay * (30 / 24))  # faster decay
        agent.influence = max(0, agent.influence - decay * (30 / 36))  # slower decay

    async def _find_nearby_agents(self, agent: Agent) -> list[dict]:
        """Find agents within hearing distance."""
        result = await self.db.execute(
            select(Agent).where(
                Agent.is_alive.is_(True),
                Agent.id != agent.id,
            )
        )
        others = result.scalars().all()
        nearby = []
        for other in others:
            dx = other.position_x - agent.position_x
            dy = other.position_y - agent.position_y
            dist = (dx**2 + dy**2) ** 0.5
            if dist <= settings.hearing_distance:
                nearby.append({"name": other.name, "distance": dist})
                if len(nearby) >= settings.max_overheard_listeners:
                    break
        return nearby

    async def _load_soul(self, agent_id: uuid.UUID) -> list:
        from emergence_world.models import SoulEntry
        result = await self.db.execute(
            select(SoulEntry).where(SoulEntry.agent_id == agent_id).limit(5)
        )
        return list(result.scalars().all())

    async def _load_memories(self, agent_id: uuid.UUID) -> list:
        result = await self.db.execute(
            select(LongTermMemory).where(LongTermMemory.agent_id == agent_id)
            .order_by(LongTermMemory.created_at.desc()).limit(10)
        )
        return list(result.scalars().all())

    async def _load_diary(self, agent_id: uuid.UUID) -> list:
        from emergence_world.models import DiaryEntry
        result = await self.db.execute(
            select(DiaryEntry).where(DiaryEntry.agent_id == agent_id)
            .order_by(DiaryEntry.created_at.desc()).limit(3)
        )
        return list(result.scalars().all())

    async def _load_relationships(self, agent_id: uuid.UUID) -> list:
        result = await self.db.execute(
            select(Relationship).where(Relationship.agent_id == agent_id).limit(10)
        )
        return list(result.scalars().all())

    def _get_available_tools(self, agent: Agent) -> list[dict]:
        """Get available tool definitions for the agent's current location."""
        # Core tools always available
        core_tools = [
            {"type": "function", "function": {"name": "go_to_place", "description": "Move to a landmark by name", "parameters": {"type": "object", "properties": {"place": {"type": "string"}}, "required": ["place"]}}},
            {"type": "function", "function": {"name": "say_to_agent", "description": "Speak to another agent", "parameters": {"type": "object", "properties": {"agent_name": {"type": "string"}, "message": {"type": "string"}}, "required": ["agent_name", "message"]}}},
            {"type": "function", "function": {"name": "write_diary", "description": "Write a diary entry", "parameters": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}}},
            {"type": "function", "function": {"name": "add_to_longterm_memory", "description": "Store an important fact", "parameters": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}}},
            {"type": "function", "function": {"name": "show_emoticon", "description": "Show an emoticon", "parameters": {"type": "object", "properties": {"emoticon": {"type": "string"}}, "required": ["emoticon"]}}},
            {"type": "function", "function": {"name": "idle", "description": "Do nothing for this turn", "parameters": {"type": "object", "properties": {}}}},
        ]
        # TODO: add location-gated tools from landmark
        return core_tools

    async def _advance_time(self) -> None:
        """Advance simulation time."""
        if not self._world_state:
            return
        if self._world_state.time_mode == "accelerated":
            delta = timedelta(seconds=self._world_state.acceleration_factor)
        else:
            delta = timedelta(seconds=2)  # small real-time step
        self._world_state.current_time = (self._world_state.current_time or datetime.now(timezone.utc)) + delta

        # Check day rollover
        new_day = (self._world_state.current_time.date() - datetime(2026, 1, 1, tzinfo=timezone.utc).date()).days + 1
        if new_day > self._world_state.day_count:
            self._world_state.day_count = new_day
            logger.info(f"=== Day {new_day} ===")

    @staticmethod
    async def _sleep(seconds: float) -> None:
        import asyncio
        await asyncio.sleep(seconds)

    def pause(self) -> None:
        self._paused = True
        logger.info("Simulation paused")

    def resume(self) -> None:
        self._paused = False
        logger.info("Simulation resumed")

    def stop(self) -> None:
        self._running = False
        logger.info("Simulation stopped")

    @property
    def status(self) -> dict:
        return {
            "running": self._running,
            "paused": self._paused,
            "day_count": self._world_state.day_count if self._world_state else 0,
            "agents_in_queue": self.scheduler.queue_size,
            "boost_queue": self.scheduler.boost_size,
        }
