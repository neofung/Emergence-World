"""Tool registry — decorator-based tool registration."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.models import Agent

logger = logging.getLogger(__name__)

# Global registry
_TOOLS: dict[str, ToolDef] = {}


@dataclass
class ToolDef:
    name: str
    description: str
    input_schema: dict[str, Any]
    execute: Callable[[Agent, AsyncSession, dict[str, Any]], Coroutine[Any, Any, str]]
    category: str = "general"
    location_gate: str | None = None

    def to_anthropic_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


def tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    category: str = "general",
    location_gate: str | None = None,
) -> Callable:
    """Decorator to register a tool."""

    def decorator(func: Callable) -> Callable:
        _TOOLS[name] = ToolDef(
            name=name,
            description=description,
            input_schema=input_schema,
            execute=func,
            category=category,
            location_gate=location_gate,
        )
        return func

    return decorator


def get_tool(name: str) -> ToolDef | None:
    return _TOOLS.get(name)


def get_all_tools() -> dict[str, ToolDef]:
    return dict(_TOOLS)


def get_tools_for_location(landmark_name: str | None, gated_tools: list[str]) -> list[dict[str, Any]]:
    """Get Anthropic-format tool schemas for a location."""
    result = []
    for t in _TOOLS.values():
        if t.location_gate is None:
            result.append(t.to_anthropic_schema())
        elif t.location_gate == landmark_name:
            result.append(t.to_anthropic_schema())
    return result
