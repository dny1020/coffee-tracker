"""Core: settings, auth, rate limiting, models."""
import os
from functools import lru_cache
from datetime import datetime, timezone

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic_settings import BaseSettings, SettingsConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base


class Settings(BaseSettings):
    database_url: str
    api_key: str
    log_level: str = "info"
    max_caffeine_mg: int = 1000
    recommended_daily_caffeine_mg: int = 400

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


# Auth
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    if not credentials or credentials.credentials != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# Rate Limiting
def _get_client_ip(request):
    return get_remote_address(request)


if os.getenv("PYTEST_CURRENT_TEST"):
    class NoOpLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = NoOpLimiter()
else:
    limiter = Limiter(key_func=_get_client_ip)


# Database Model
Base = declarative_base()


class CoffeeLog(Base):
    __tablename__ = "coffee_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    caffeine_mg = Column(Float, nullable=False)
    coffee_type = Column(String(100))
