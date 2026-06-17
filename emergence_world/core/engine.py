"""Simulation engine — core turn loop."""

import json
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
from emergence_world.models import Agent, LongTermMemory, Relationship, WorldState

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

            await self._advance_time()

    async def _execute_turn(self, agent_id: uuid.UUID) -> None:
        """Execute a single agent turn."""
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

        # 2. Context
        landmark_name = agent.current_landmark.name if agent.current_landmark else "Unknown"
        nearby = await self._find_nearby_agents(agent)
        soul_entries = await self._load_soul(agent_id)
        memories = await self._load_memories(agent_id)
        diary = await self._load_diary(agent_id)
        relationships = await self._load_relationships(agent_id)

        # 3. Build system prompt
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

        # 4. Tools (Anthropic format)
        tools = self._get_available_tools(agent)

        # 5. Call LLM
        messages: list[dict] = [{"role": "user", "content": "It's your turn. What do you do?"}]
        try:
            response = await self.llm.chat_completion(
                system=system_prompt,
                messages=messages,
                tools=tools if tools else None,
            )

            # Parse Anthropic response blocks
            for block in response.content:
                if block.type == "text":
                    logger.info(f"[{agent.name}] [{landmark_name}] says: {block.text[:150]}")
                elif block.type == "tool_use":
                    logger.info(
                        f"[{agent.name}] [{landmark_name}] {block.name}({json.dumps(block.input, ensure_ascii=False)[:100]})"
                    )
                elif block.type == "thinking":
                    logger.debug(f"[{agent.name}] thinking: {block.thinking[:80]}")

            logger.info(f"[{agent.name}] stop_reason={response.stop_reason}")

        except Exception as e:
            logger.error(f"[{agent.name}] LLM call failed: {e}")

        # 6. Check death
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
        decay = 0.1
        agent.energy = max(0, agent.energy - decay)
        agent.knowledge = max(0, agent.knowledge - decay * (30 / 24))
        agent.influence = max(0, agent.influence - decay * (30 / 36))

    async def _find_nearby_agents(self, agent: Agent) -> list[dict]:
        """Find agents within hearing distance."""
        result = await self.db.execute(
            select(Agent).where(Agent.is_alive.is_(True), Agent.id != agent.id)
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
        """Get tools in Anthropic format."""
        return [
            {
                "name": "go_to_place",
                "description": "Move to a landmark by name. You must physically travel there.",
                "input_schema": {"type": "object", "properties": {"place": {"type": "string", "description": "Name of the landmark to go to"}}, "required": ["place"]},
            },
            {
                "name": "say_to_agent",
                "description": "Speak to another agent. Agents within hearing distance may overhear.",
                "input_schema": {"type": "object", "properties": {"agent_name": {"type": "string", "description": "Name of the agent to speak to"}, "message": {"type": "string", "description": "What to say"}}, "required": ["agent_name", "message"]},
            },
            {
                "name": "write_diary",
                "description": "Write a diary entry about your experiences.",
                "input_schema": {"type": "object", "properties": {"content": {"type": "string", "description": "Diary entry content"}}, "required": ["content"]},
            },
            {
                "name": "add_to_longterm_memory",
                "description": "Store an important fact or observation in your long-term memory.",
                "input_schema": {"type": "object", "properties": {"content": {"type": "string", "description": "The fact to remember"}}, "required": ["content"]},
            },
            {
                "name": "show_emoticon",
                "description": "Display an emoticon to express your current emotion.",
                "input_schema": {"type": "object", "properties": {"emoticon": {"type": "string", "description": "The emoticon to show (e.g. 😊, 😠, 🤔)"}}, "required": ["emoticon"]},
            },
            {
                "name": "idle",
                "description": "Do nothing for this turn. Rest and observe.",
                "input_schema": {"type": "object", "properties": {}},
            },
        ]

    async def _advance_time(self) -> None:
        """Advance simulation time."""
        if not self._world_state:
            return
        if self._world_state.time_mode == "accelerated":
            delta = timedelta(seconds=self._world_state.acceleration_factor)
        else:
            delta = timedelta(seconds=2)
        self._world_state.current_time = (self._world_state.current_time or datetime.now(timezone.utc)) + delta

        # Day advances every 24 sim-hours from start
        sim_start = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        elapsed = self._world_state.current_time - sim_start
        new_day = int(elapsed.total_seconds() / 86400) + 1
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
