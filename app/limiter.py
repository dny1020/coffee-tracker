"""Rate limiter configuration.

Provides a single Limiter instance that can be imported anywhere without
creating circular imports. Tries to use Redis if configured, otherwise
falls back to in-memory storage.
"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.settings import settings


def _build_limiter() -> Limiter:
    """Create a Limiter instance.

    Behavior:
    - In test runs (PYTEST_CURRENT_TEST present) always use in-memory backend.
    - If redis URL provided, verify connectivity with a ping before using it.
    - Fall back silently to in-memory on any failure.
    """
    redis_url = settings.redis_url or ""

    # Force memory backend during pytest to avoid external dependency
    if os.getenv("PYTEST_CURRENT_TEST"):
        return Limiter(key_func=_composite_key)

    if redis_url.startswith("redis://"):
        try:
            import redis  # type: ignore
            client = redis.from_url(redis_url)
            client.ping()
            return Limiter(key_func=_composite_key, storage_uri=redis_url)
        except Exception:
            # Fallback to memory if Redis not reachable
            pass
    return Limiter(key_func=_composite_key)


def _composite_key(request):  # type: ignore
    """Combine API key (if present) + remote address for fair limiting.
    Falls back to IP only when header absent.
    """
    api_key = None
    auth = request.headers.get("Authorization") if hasattr(request, "headers") else None
    if auth and auth.startswith("Bearer "):
        api_key = auth.split(" ", 1)[1][:16]  # truncate to avoid huge keys in storage
    base = get_remote_address(request)
    return f"{base}:{api_key}" if api_key else base


limiter = _build_limiter()
