"""Minimal test configuration."""
import os
import pytest
from fastapi.testclient import TestClient

# Set test environment variables BEFORE importing anything
# Use shared cache for in-memory SQLite so tables persist across connections
os.environ["DATABASE_URL"] = "sqlite:///file:memdb1?mode=memory&cache=shared&uri=true"
os.environ["REDIS_URL"] = "memory://"
os.environ["API_KEY"] = "test-key-123"
os.environ["PYTEST_CURRENT_TEST"] = "true"
os.environ["SKIP_DB_INIT"] = "1"

from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    # Initialize database tables
    from app.database import init_db
    init_db()
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    """Auth headers for tests."""
    return {"Authorization": "Bearer test-key-123"}
