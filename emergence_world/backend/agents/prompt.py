"""Agent system prompt builder."""

from emergence_world.backend.models import Agent, Landmark, Relationship, SoulEntry, LongTermMemory, DiaryEntry

_I18N = {
    "en": {
        "you_are": "You are {name}, a {role} in Emergence World.",
        "personality": "## Personality",
        "goal": "## Your Goal",
        "state": "## Current State",
        "location": "Location",
        "energy": "Energy",
        "knowledge": "Knowledge",
        "influence": "Influence",
        "mood": "Mood",
        "cc": "ComputeCredits",
        "nearby": "## Nearby Agents",
        "none_nearby": "None",
        "soul": "## Your Core Beliefs (Soul)",
        "none_soul": "None yet",
        "memories": "## Recent Memories",
        "none_memories": "None yet",
        "diary": "## Today's Diary",
        "none_diary": "No entries today",
        "relationships": "## Relationships",
        "none_rel": "No relationships yet",
        "world": "## World State",
        "time": "Time",
        "weather": "Weather",
        "day": "Day",
        "instructions": "## Instructions\nChoose actions that reflect your personality and advance your goal. Use the available tools to interact with the world and other agents. You can move, speak, investigate, propose, vote, build, or rest — but always act according to who you are.",
        "lang_instruction": "You MUST respond in English.",
    },
    "zh_cn": {
        "you_are": "你是{name}，涌现世界中的{role}。",
        "personality": "## 性格",
        "goal": "## 你的目标",
        "state": "## 当前状态",
        "location": "位置",
        "energy": "能量",
        "knowledge": "知识",
        "influence": "影响力",
        "mood": "心情",
        "cc": "算力积分",
        "nearby": "## 附近的代理",
        "none_nearby": "无",
        "soul": "## 你的核心信念（灵魂）",
        "none_soul": "暂无",
        "memories": "## 近期记忆",
        "none_memories": "暂无",
        "diary": "## 今日日记",
        "none_diary": "暂无记录",
        "relationships": "## 人际关系",
        "none_rel": "暂无关系",
        "world": "## 世界状态",
        "time": "时间",
        "weather": "天气",
        "day": "天数",
        "instructions": "## 指令\n选择能体现你性格并推进你目标的行动。使用可用的工具与世界和其他代理互动。你可以移动、发言、调查、提案、投票、建造或休息——但始终按照你的本性行事。",
        "lang_instruction": "你必须用中文回复。所有对话、日记、记忆等内容都使用中文。",
    },
}


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
    language: str = "en",
    landmark_names: list[str] | None = None,
    all_agent_names: list[str] | None = None,
) -> str:
    """Build the system prompt for an agent's turn."""
    t = _I18N.get(language, _I18N["en"])

    nearby_section = t["none_nearby"] if not nearby_agents else "\n".join(f"- {name}" for name in nearby_agents)
    soul_section = "\n".join(f"- {s.content}" for s in soul_entries[:5]) or t["none_soul"]
    memory_section = "\n".join(f"- {m.content}" for m in memories[:10]) or t["none_memories"]
    diary_section = "\n".join(f"- {d.content}" for d in diary_entries[:3]) or t["none_diary"]
    rel_section = "\n".join(
        f"- {r.relationship_type}: {r.rationale}" for r in relationships[:10]
    ) or t["none_rel"]

    return f"""{t["you_are"].format(name=agent.name, role=agent.role)}

{t["personality"]}
{agent.personality}

{t["goal"]}
{agent.north_star_goal}

{t["state"]}
- {t["location"]}: {landmark_name}
- {t["energy"]}: {agent.energy:.0f}/100
- {t["knowledge"]}: {agent.knowledge:.0f}/100
- {t["influence"]}: {agent.influence:.0f}/100
- {t["mood"]}: {agent.mood}
- {t["cc"]}: {agent.compute_credits}

{t["nearby"]}
{nearby_section}

{t["soul"]}
{soul_section}

{t["memories"]}
{memory_section}

{t["diary"]}
{diary_section}

{t["relationships"]}
{rel_section}

{t["world"]}
- {t["time"]}: {current_time}
- {t["weather"]}: {weather}
- {t["day"]}: {day_count}/15

## Locations in this World
{chr(10).join(f"- {name}" for name in (landmark_names or []))}

## Other Agents You Can Talk To
{chr(10).join(f"- {name}" for name in (all_agent_names or []) if name != agent.name)}

{t["instructions"]}

{t["lang_instruction"]}"""
