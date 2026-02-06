"""Settings, auth y modelo de base de datos."""
import os
from datetime import datetime, timezone

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic_settings import BaseSettings
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base


class Settings(BaseSettings):
    database_url: str = "sqlite:///data/coffee.db"
    api_key: str = "test-key"
    log_level: str = "info"
    max_caffeine_mg: int = 1000
    recommended_daily_caffeine_mg: int = 400

    class Config:
        env_file = ".env"


settings = Settings()

# Auth
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not credentials or credentials.credentials != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# Database Model
Base = declarative_base()


class CoffeeLog(Base):
    __tablename__ = "coffee_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    caffeine_mg = Column(Float, nullable=False)
    coffee_type = Column(String(100))
