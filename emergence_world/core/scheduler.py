"""Round-robin scheduler with boost queue priority."""

import uuid
from collections import deque


class Scheduler:
    """Manages turn order for agents."""

    def __init__(self) -> None:
        self._agent_queue: deque[uuid.UUID] = deque()
        self._boost_queue: deque[uuid.UUID] = deque()

    def set_agents(self, agent_ids: list[uuid.UUID]) -> None:
        """Initialize the round-robin queue with alive agents."""
        self._agent_queue = deque(agent_ids)

    def add_boost(self, agent_id: uuid.UUID) -> None:
        """Add an agent to the boost queue (paid 1 CC)."""
        self._boost_queue.append(agent_id)

    def next_agent(self) -> uuid.UUID | None:
        """Get the next agent to act. Boost queue has priority."""
        if self._boost_queue:
            return self._boost_queue.popleft()
        if self._agent_queue:
            agent = self._agent_queue.popleft()
            self._agent_queue.append(agent)  # round-robin: put back at end
            return agent
        return None

    def remove_agent(self, agent_id: uuid.UUID) -> None:
        """Remove a dead or removed agent from scheduling."""
        if agent_id in self._agent_queue:
            self._agent_queue.remove(agent_id)
        while agent_id in self._boost_queue:
            self._boost_queue.remove(agent_id)

    @property
    def queue_size(self) -> int:
        return len(self._agent_queue) + len(self._boost_queue)

    @property
    def boost_size(self) -> int:
        return len(self._boost_queue)
