from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Settings
    llm_provider: Literal["llama_cpp", "ollama"] = Field(default="llama_cpp")
    llama_cpp_base_url: str = Field(default="http://localhost:8080/v1")
    llama_cpp_api_key: str = Field(default="not-needed")
    producer_model: str = Field(default="local-model")
    jokey_model: str = Field(default="local-model")

    # Buffer Thresholds (in seconds)
    buffer_target_seconds: int = Field(default=300, ge=60)
    buffer_warning_seconds: int = Field(default=120, ge=30)
    buffer_emergency_seconds: int = Field(default=30, ge=10)

    # Segment Constraints (in seconds)
    segment_min_seconds: int = Field(default=90, ge=30)
    segment_target_seconds: int = Field(default=180, ge=60)
    segment_max_seconds: int = Field(default=300, ge=90)

    # Guardrails & Budgets
    max_tool_calls_per_cycle: int = Field(default=8, ge=1)
    max_research_seconds: int = Field(default=30, ge=5)
    max_agent_retries: int = Field(default=2, ge=0)

    # TTS Settings
    tts_provider: str = Field(default="local")
    tts_default_speed: float = Field(default=1.0, gt=0.0)

    # Logging
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()