import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_url():
    """Get database URL, checking environment variables dynamically"""
    return os.getenv("DATABASE_URL", "sqlite:///data/coffee.db")


def create_database_engine():
    """Create database engine using current DATABASE_URL (lazy import).

    Adds SQLite-specific connect args and enables pool_pre_ping for Postgres reliability.
    Configures explicit connection pooling for production use.
    """
    from sqlalchemy import create_engine
    database_url = get_database_url()
    is_sqlite = database_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    
    # Configure connection pooling for non-SQLite databases
    if is_sqlite:
        engine = create_engine(
            database_url,
            connect_args=connect_args,
        )
    else:
        engine = create_engine(
            database_url,
            connect_args=connect_args,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
        )
    return engine


# Lazy globals
engine = None
SessionLocal = None


def init_db():
    """Create all tables"""
    # Recreate engine in case DATABASE_URL changed
    from sqlalchemy.orm import sessionmaker as _sessionmaker
    # Import models lazily to avoid importing SQLAlchemy at module import time
    from app.models import Base
    global engine, SessionLocal
    engine = create_database_engine()
    SessionLocal = _sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    global SessionLocal
    if SessionLocal is None:
        # Fallback lazy init if not initialized yet
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
