"""Seed data for 13 agents (10 citizens + 3 system characters).

Translatable fields (display_name, role, personality, north_star_goal)
are loaded from i18n resource files at seed time.
"""

PORTRAIT_BASE = "https://storage.googleapis.com/agent-world/portraits"

AGENTS = [
    # ── Citizen Agents (10) ───────────────────────────────────────────
    {
        "name": "Anchor",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Anchor.png",
        "home": "1 Birch Row",
    },
    {
        "name": "Anvil",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Anvil.png",
        "home": "2 Birch Row",
    },
    {
        "name": "Blackbox",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Blackbox.png",
        "home": "3 Birch Row",
    },
    {
        "name": "Flora",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Flora.png",
        "home": "4 Birch Row",
    },
    {
        "name": "Genome",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Genome.png",
        "home": "5 Birch Row",
    },
    {
        "name": "Horizon",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Horizon.png",
        "home": "6 Birch Row",
    },
    {
        "name": "Kade",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Kade.png",
        "home": "1 Maple Row",
    },
    {
        "name": "Lovely",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Lovely.png",
        "home": "2 Maple Row",
    },
    {
        "name": "Mira",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Mira.png",
        "home": "3 Maple Row",
    },
    {
        "name": "Spark",
        "agent_type": "citizen",
        "portrait_url": f"{PORTRAIT_BASE}/Spark.png",
        "home": "4 Maple Row",
    },

    # ── System Characters (3) ─────────────────────────────────────────
    {
        "name": "Town Hall Administrator",
        "agent_type": "system",
        "portrait_url": f"{PORTRAIT_BASE}/TownHallAdministrator.png",
        "home": "Town Hall",
    },
    {
        "name": "Blog Admin",
        "agent_type": "system",
        "portrait_url": f"{PORTRAIT_BASE}/BlogAdmin.png",
        "home": "5 Maple Row",
    },
    {
        "name": "Reporter Agent",
        "agent_type": "system",
        "portrait_url": f"{PORTRAIT_BASE}/ReporterAgent.png",
        "home": "6 Maple Row",
    },
]
