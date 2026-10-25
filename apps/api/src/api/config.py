
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AEGIS API"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:13000",
]

    database_url: str = "postgresql+psycopg://aegis:aegis@localhost:5432/aegis"
    redis_url: str = "redis://localhost:6379/0"

    groq_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    mistral_api_key: SecretStr | None = None
    openrouter_api_key: SecretStr | None = None
    jev_api_key: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
