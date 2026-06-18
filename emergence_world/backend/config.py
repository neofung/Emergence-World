from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "sqlite+aiosqlite:///./emergence_world/backend/data/emergence.db"

    # LLM (Anthropic API)
    llm_base_url: str = "http://127.0.0.1:15721"
    llm_api_key: str = "PROXY_MANAGED"
    llm_default_model: str = "claude-sonnet-4-6"
    llm_max_tokens: int = 4096

    # Simulation
    time_mode: str = "accelerated"  # realtime | accelerated
    acceleration_factor: int = 60
    concurrent_agents: int = 1

    # World
    world_grid_size: int = 240
    hearing_distance: float = 25.0
    max_overheard_listeners: int = 4

    # Needs decay (hours to reach 0)
    energy_decay_hours: float = 30.0
    knowledge_decay_hours: float = 24.0
    influence_decay_hours: float = 36.0
    death_countdown_hours: float = 48.0

    # Economy
    boost_turn_cost: int = 1
    recharge_cost: int = 1
    victory_arch_cycle_days: int = 2
    victory_arch_reward_first: int = 20
    victory_arch_reward_runner: int = 10
    max_theft_amount: int = 10

    # Governance
    constitution_amendment_threshold: float = 0.7
    proposal_approval_threshold: float = 0.5

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # i18n
    language: str = "zh_cn"  # en, zh_cn


@lru_cache
def get_settings() -> Settings:
    return Settings()
