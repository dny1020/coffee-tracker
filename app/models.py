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
    
    # Add indexes for performance
    __table_args__ = (
        Index('ix_coffee_logs_timestamp', 'timestamp'),
        Index('ix_coffee_logs_caffeine_mg', 'caffeine_mg'),
    )

class HeartRateLog(Base):
    __tablename__ = "heart_rate_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    bpm = Column(Integer, nullable=False)
    context = Column(String(50))  # resting, active, post-coffee, etc
    notes = Column(Text)
    
    # Add indexes for performance
    __table_args__ = (
        Index('ix_heart_rate_logs_timestamp', 'timestamp'),
        Index('ix_heart_rate_logs_bpm', 'bpm'),
        Index('ix_heart_rate_logs_context', 'context'),
    )