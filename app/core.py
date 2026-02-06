"""Core application components: settings, auth, and rate limiting."""
import os
from functools import lru_cache, wraps
from typing import Callable, Any, List

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic_settings import BaseSettings, SettingsConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address


# =============================================================================
# Settings
# =============================================================================

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


# =============================================================================
# Authentication
# =============================================================================

security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify API key from Authorization header."""
    if not credentials or credentials.credentials != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# =============================================================================
# Rate Limiting
# =============================================================================

class NoOpLimiter:
    """No-op limiter for testing."""
    def limit(self, *args: Any, **kwargs: Any) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
                return func(*func_args, **func_kwargs)
            return wrapper
        return decorator


def _composite_key(request):  # type: ignore
    """Combine API key + IP address for rate limiting."""
    api_key = None
    auth = request.headers.get("Authorization") if hasattr(request, "headers") else None
    if auth and auth.startswith("Bearer "):
        api_key = auth.split(" ", 1)[1][:16]
    base = get_remote_address(request)
    return f"{base}:{api_key}" if api_key else base


# Use no-op limiter in tests, real limiter otherwise
limiter = NoOpLimiter() if os.getenv("PYTEST_CURRENT_TEST") else Limiter(key_func=_composite_key)
