"""Building and construction tools."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.models import Agent
from emergence_world.backend.tools.registry import tool

logger = logging.getLogger(__name__)


@tool(
    name="put_brick_in_pixel",
    description="Place a persistent 3D block in the world at your current location.",
    input_schema={
        "type": "object",
        "properties": {
            "color": {"type": "string", "description": "Color of the brick (e.g. red, blue, gold)"},
            "material": {"type": "string", "description": "Material: stone, wood, metal, glass"},
        },
        "required": ["color"],
    },
    category="building",
)
async def put_brick_in_pixel(agent: Agent, db: AsyncSession, color: str, material: str = "stone") -> str:
    agent.influence = min(100, agent.influence + 0.5)
    return f"You placed a {color} {material} brick at ({agent.position_x:.0f}, {agent.position_z:.0f}). (+0.5 influence)"
