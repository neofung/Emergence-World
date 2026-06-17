"""Tools package — auto-registers all tools on import."""

from emergence_world.tools.registry import get_all_tools, get_tool, get_tools_for_location

# Import core tools to trigger registration
import emergence_world.tools.core  # noqa: F401

__all__ = ["get_all_tools", "get_tool", "get_tools_for_location"]
