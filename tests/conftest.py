import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.database import get_db

# Set API key for auth (default for tests)
os.environ["API_KEY"] = os.getenv("API_KEY", "coffee-addict-secret-key-2025")

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override for tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fixture for test client with in-memory DB
@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    headers = {"Authorization": f"Bearer {os.environ['API_KEY']}"}
    with TestClient(app, headers=headers) as c:
        yield c
