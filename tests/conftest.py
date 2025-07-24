import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

from app.main import app
from app.database import get_db
from app.models import Base

# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
   """Create test database engine"""
   engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
   Base.metadata.create_all(bind=engine)
   yield engine
   # Cleanup
   Base.metadata.drop_all(bind=engine)
   if os.path.exists("./test.db"):
       os.remove("./test.db")

@pytest.fixture(scope="function")
def test_db(test_engine):
   """Create test database session"""
   TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
   db = TestingSessionLocal()
   try:
       yield db
   finally:
       db.rollback()
       db.close()

@pytest.fixture(scope="function")
def client(test_db):
   """Create test client with test database"""
   def override_get_db():
       try:
           yield test_db
       finally:
           pass
   
   app.dependency_overrides[get_db] = override_get_db
   with TestClient(app) as test_client:
       yield test_client
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