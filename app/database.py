from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/coffee.db")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
   """Create all tables"""
   Base.metadata.create_all(bind=engine)

def get_db():
   """Dependency for getting database session"""
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()
