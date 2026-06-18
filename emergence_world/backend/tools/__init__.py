"""Tools package — auto-registers all tools on import."""

from emergence_world.backend.tools.registry import get_all_tools, get_tool, get_tools_for_location

# Import tool modules to trigger @tool registration
import emergence_world.backend.tools.core  # noqa: F401
import emergence_world.backend.tools.navigation  # noqa: F401
import emergence_world.backend.tools.social  # noqa: F401
import emergence_world.backend.tools.governance  # noqa: F401
import emergence_world.backend.tools.content  # noqa: F401
import emergence_world.backend.tools.crime  # noqa: F401

__all__ = ["get_all_tools", "get_tool", "get_tools_for_location"]
