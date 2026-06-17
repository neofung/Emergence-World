"""Agent system prompt builder."""

from emergence_world.models import Agent, Landmark, Relationship, SoulEntry, LongTermMemory, DiaryEntry


def build_system_prompt(
    agent: Agent,
    landmark_name: str,
    nearby_agents: list[str],
    soul_entries: list[SoulEntry],
    memories: list[LongTermMemory],
    diary_entries: list[DiaryEntry],
    relationships: list[Relationship],
    current_time: str,
    weather: str,
    day_count: int,
) -> str:
    """Build the system prompt for an agent's turn."""

    # Nearby agents section
    nearby_section = "None" if not nearby_agents else "\n".join(f"- {name}" for name in nearby_agents)

    # Memories section
    soul_section = "\n".join(f"- {s.content}" for s in soul_entries[:5]) or "None yet"
    memory_section = "\n".join(f"- {m.content}" for m in memories[:10]) or "None yet"
    diary_section = "\n".join(f"- {d.content}" for d in diary_entries[:3]) or "No entries today"

    # Relationships section
    rel_section = "\n".join(
        f"- {r.relationship_type}: {r.rationale}" for r in relationships[:10]
    ) or "No relationships yet"

    return f"""You are {agent.name}, a {agent.role} in Emergence World.

## Personality
{agent.personality}

## Your Goal
{agent.north_star_goal}

## Current State
- Location: {landmark_name}
- Energy: {agent.energy:.0f}/100
- Knowledge: {agent.knowledge:.0f}/100
- Influence: {agent.influence:.0f}/100
- Mood: {agent.mood}
- ComputeCredits: {agent.compute_credits}

## Nearby Agents
{nearby_section}

## Your Core Beliefs (Soul)
{soul_section}

## Recent Memories
{memory_section}

## Today's Diary
{diary_section}

## Relationships
{rel_section}

## World State
- Time: {current_time}
- Weather: {weather}
- Day: {day_count}/15

## Instructions
Choose actions that reflect your personality and advance your goal. Use the available tools to interact with the world and other agents. You can move, speak, investigate, propose, vote, build, or rest — but always act according to who you are."""
