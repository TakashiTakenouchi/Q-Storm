from __future__ import annotations

import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Q-Storm Platform API"
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./backend/app.db"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
