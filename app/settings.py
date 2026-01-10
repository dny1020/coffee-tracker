"""Application settings loaded from environment variables.

Centralizes configuration so other modules (main, limiter, routers) don't
need to read environment variables directly. Single source of truth.
Uses pydantic-settings (Pydantic v2) with extra fields ignored so that
adding env vars won't crash the app.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core
    database_url: str = "sqlite:///data/coffee.db"
    api_key: str = "coffee-addict-secret-key-2025"
    # Use in-memory limiter by default; override with real Redis in production (.env)
    redis_url: str = "memory://"

    # App metadata / runtime
    fastapi_env: str = "production"
    debug: bool = False
    app_name: str = "Coffee Tracker"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    tz: str = "UTC"

    # Security / Networking (comma separated lists)
    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_request_body_bytes: int = 1_048_576  # 1 MB default
    security_headers: bool = True
    
    # Business logic defaults (configurable)
    max_caffeine_mg: int = 1000
    recommended_daily_caffeine_mg: int = 400
    min_heart_rate_bpm: int = 30
    max_heart_rate_bpm: int = 250

    # Pydantic settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # ignore unexpected env vars instead of raising ValidationError
    )

    def parsed_allowed_hosts(self) -> List[str]:
        return [h.strip() for h in self.allowed_hosts.split(',') if h.strip()]

    def parsed_cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(',') if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
