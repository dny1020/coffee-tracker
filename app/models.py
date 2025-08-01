from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class CoffeeLog(Base):
    __tablename__ = "coffee_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    caffeine_mg = Column(Float, nullable=False)
    coffee_type = Column(String(100))
    notes = Column(Text)
    


class HeartRateLog(Base):
    __tablename__ = "heart_rate_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    bpm = Column(Integer, nullable=False)
    context = Column(String(50))  # resting, active, post-coffee, etc
    notes = Column(Text)
    
