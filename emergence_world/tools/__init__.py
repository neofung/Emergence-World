"""Tools package — auto-registers all tools on import."""

from emergence_world.tools.registry import get_all_tools, get_tool, get_tools_for_location

# Import tool modules to trigger @tool registration
import emergence_world.tools.core  # noqa: F401
import emergence_world.tools.navigation  # noqa: F401
import emergence_world.tools.social  # noqa: F401
import emergence_world.tools.governance  # noqa: F401
import emergence_world.tools.content  # noqa: F401
import emergence_world.tools.crime  # noqa: F401

__all__ = ["get_all_tools", "get_tool", "get_tools_for_location"]
