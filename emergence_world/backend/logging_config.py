"""Logging configuration — two rotating log files (14-day retention)."""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).parent / "data" / "logs"

_FMT = "%(asctime)s [%(name)s] %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """Configure two log files + console output."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Console handler (existing behavior)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(_FMT, datefmt=_DATEFMT))
    root.addHandler(console)

    # World log — simulation engine, agents, tools
    world_handler = TimedRotatingFileHandler(
        LOG_DIR / "world.log",
        when="midnight",
        interval=1,
        backupCount=14,
        encoding="utf-8",
    )
    world_handler.setFormatter(logging.Formatter(_FMT, datefmt=_DATEFMT))
    world_handler.addFilter(WorldFilter())

    # Access log — HTTP requests from frontend
    access_handler = TimedRotatingFileHandler(
        LOG_DIR / "access.log",
        when="midnight",
        interval=1,
        backupCount=14,
        encoding="utf-8",
    )
    access_handler.setFormatter(logging.Formatter(_FMT, datefmt=_DATEFMT))
    access_handler.addFilter(AccessFilter())

    root.addHandler(world_handler)
    root.addHandler(access_handler)


# Simulation-related loggers
_WORLD_PREFIXES = (
    "emergence_world.backend.core",
    "emergence_world.backend.agents",
    "emergence_world.backend.tools",
    "emergence_world.backend.ui",
    "emergence_world.backend.seed",
)


class WorldFilter(logging.Filter):
    """Allow only simulation/world loggers."""

    def filter(self, record: logging.LogRecord) -> bool:
        return any(record.name.startswith(p) for p in _WORLD_PREFIXES)


class AccessFilter(logging.Filter):
    """Allow only HTTP access log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name == "access"
