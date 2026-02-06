"""Database."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = None
SessionLocal = None


def init_db():
    from app.core import Base
    global engine, SessionLocal
    
    database_url = os.getenv("DATABASE_URL", "sqlite:///data/coffee.db")
    connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}
    
    engine = create_engine(database_url, connect_args=connect_args)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    global SessionLocal
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
