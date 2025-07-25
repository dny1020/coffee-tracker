import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base
from app.auth import verify_api_key

# Test API key
TEST_API_KEY = "test-api-key-for-tests"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    # Create in-memory SQLite database
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up tables
        Base.metadata.drop_all(bind=test_engine)


def mock_verify_api_key():
    """Mock authentication for tests"""
    return True


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with overridden dependencies"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Override the dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = mock_verify_api_key

    with TestClient(app=app) as test_client:
        test_client.headers.update({"Authorization": f"Bearer {TEST_API_KEY}"})
        yield test_client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_coffee_data():
    """Sample coffee data for testing"""
    return {
        "caffeine_mg": 95.0,
        "coffee_type": "espresso",
        "notes": "test coffee"
    }


@pytest.fixture
def sample_heartrate_data():
    """Sample heart rate data for testing"""
    return {
        "bpm": 80,
        "context": "resting",
        "notes": "test heartrate"
    }
