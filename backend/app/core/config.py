from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]  # backend


class Settings(BaseSettings):
    app_name: str = "Teaching Agent System"
    app_env: str = "dev"
    app_debug: bool = True

    openai_base_url: str
    openai_api_key: str
    openai_model: str

    default_temperature: float = 0.2
    max_retry_count: int = 2
    llm_timeout_seconds: int = 90
    llm_default_max_tokens: int = 800

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()