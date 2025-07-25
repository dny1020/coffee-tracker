# tests/test_config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def setup_test_db(app):
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides = {}
    from app.dependencies import get_db  # donde defines `get_db`
    app.dependency_overrides[get_db] = override_get_db
