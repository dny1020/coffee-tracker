"""Rate limiter configuration.

Provides a single Limiter instance that can be imported anywhere without
creating circular imports. Tries to use Redis if configured, otherwise
falls back to in-memory storage.

In test mode (PYTEST_CURRENT_TEST set), provides a no-op limiter that doesn't
actually rate limit to avoid threading issues with TestClient.
"""
import os
from functools import wraps
from typing import Callable, Any
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.settings import settings


class NoOpLimiter:
    """No-op limiter for testing that doesn't actually limit requests."""
    
    def limit(self, *args: Any, **kwargs: Any) -> Callable:
        """Return a pass-through decorator that doesn't limit."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
                return func(*func_args, **func_kwargs)
            return wrapper
        return decorator


def _build_limiter() -> Limiter | NoOpLimiter:
    """Create a Limiter instance.

    Behavior:
    - In test runs (PYTEST_CURRENT_TEST present) return a no-op limiter.
    - If redis URL provided, verify connectivity with a ping before using it.
    - Fall back silently to in-memory on any failure.
    """
    # Use no-op limiter during pytest to avoid threading issues with TestClient
    if os.getenv("PYTEST_CURRENT_TEST"):
        return NoOpLimiter()
    
    redis_url = settings.redis_url or ""

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
