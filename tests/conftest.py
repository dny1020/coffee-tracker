"""Test configuration and fixtures."""
import os
import pytest
from fastapi.testclient import TestClient

# Set test environment variables BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "memory://"
os.environ["API_KEY"] = "coffee-addict-secret-key-2025"
os.environ["PYTEST_CURRENT_TEST"] = "true"

# Import app AFTER setting environment
from app.main import app

# Initialize database for tests
from app.database import init_db
init_db()


@pytest.fixture(scope="module")
def client():
    """Create a test client that reuses the same in-memory database."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    """Return authentication headers for tests."""
    return {"Authorization": "Bearer coffee-addict-secret-key-2025"}
