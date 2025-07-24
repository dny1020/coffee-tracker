import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.database import get_db
from app.models import Base
from app.auth import verify_api_key

# Create test database with unique name
TEST_DATABASE_URL = "sqlite:///test_coffee_tracker.db"
# Test API key
TEST_API_KEY = "test-api-key-for-tests"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    # Remove test database if it exists
    test_db_path = "./test_coffee_tracker.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session with transaction rollback"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    # Use a single connection for the entire test
    connection = test_engine.connect()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        connection.close()


def mock_verify_api_key():
    """Mock authentication for tests"""
    return True


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with test database and mocked auth"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Override dependencies for testing
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = mock_verify_api_key

    with TestClient(app) as test_client:
        # Set default headers for authentication
        test_client.headers.update({"Authorization": f"Bearer {TEST_API_KEY}"})
        yield test_client

    # Clear overrides after test
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
