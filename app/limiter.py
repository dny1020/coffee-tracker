"""Rate limiter with in-memory storage."""
import os
from functools import wraps
from typing import Callable, Any
from slowapi import Limiter
from slowapi.util import get_remote_address


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
