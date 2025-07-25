from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_url():
    """Get database URL, checking environment variables dynamically"""
    return os.getenv("DATABASE_URL", "sqlite:///data/coffee.db")


def create_database_engine():
    """Create database engine using current DATABASE_URL"""
    database_url = get_database_url()
    return create_engine(
        database_url, connect_args={"check_same_thread": False}
    )


# Create engine
engine = create_database_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables"""
    # Recreate engine in case DATABASE_URL changed
    global engine, SessionLocal
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
