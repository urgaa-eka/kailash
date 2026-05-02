"""Shared settings base. Services subclass and add their own fields."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    """Common service settings loaded from env + .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    service_name: str = "service"
    version: str = "0.1.0"
    env: str = Field(default="dev", description="dev | staging | prod")
    log_level: str = "INFO"
    log_json: bool = True

    platform_internal_token: str | None = None
    cors_origins: str = "*"

    request_timeout_s: float = 30.0
