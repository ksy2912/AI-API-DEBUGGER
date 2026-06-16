import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: AI API Debugger/.env (works for local dev; Docker injects env via compose)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ROOT_ENV = _PROJECT_ROOT / ".env"


def _normalize_database_url(url: str) -> str:
    # Render/Heroku provide postgres:// — SQLAlchemy 2.x needs postgresql://
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_ROOT_ENV), ".env"),
        env_file_encoding="utf-8",
    )

    database_url: str = "postgresql://apidebug:apidebug@localhost:5432/apidebug"

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, value: str) -> str:
        return _normalize_database_url(value)
    redis_url: str = "redis://localhost:6379/0"
    app_name: str = "AI API Debugger"
    debug: bool = False
    http_timeout_seconds: float = 30.0
    monitor_check_interval_seconds: int = 30

    # OpenRouter (OpenAI-compatible) — https://openrouter.ai/docs
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str = "http://localhost:5173"
    llm_model: str = "openai/gpt-4o-mini"
    llm_enabled: bool = True
    embedding_model: str = "openai/text-embedding-3-small"
    embedding_dimensions: int = 1536
    rag_enabled: bool = True
    rag_top_k: int = 5

    @field_validator("openrouter_site_url", mode="before")
    @classmethod
    def fix_site_url(cls, value: str) -> str:
        if not value:
            return "http://localhost:5173"
        if value.startswith("http://") or value.startswith("https://"):
            return value
        return f"https://{value}"

    @property
    def public_site_url(self) -> str:
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url
        return self.openrouter_site_url


settings = Settings()
