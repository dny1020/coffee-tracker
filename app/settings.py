"""Application settings from environment variables."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database & Auth
    database_url: str = "sqlite:///data/coffee.db"
    api_key: str = "coffee-addict-secret-key-2025"

    # App
    fastapi_env: str = "production"
    debug: bool = False
    log_level: str = "info"
    tz: str = "UTC"

    # Security
    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:3000"
    max_request_body_bytes: int = 1_048_576
    security_headers: bool = True
    metrics_public: bool = True
    
    # Validation limits
    max_caffeine_mg: int = 1000
    recommended_daily_caffeine_mg: int = 400


    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    def parsed_allowed_hosts(self) -> List[str]:
        return [h.strip() for h in self.allowed_hosts.split(',') if h.strip()]

    def parsed_cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(',') if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
