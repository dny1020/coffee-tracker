from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class CoffeeLog(Base):
    __tablename__ = "coffee_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    caffeine_mg = Column(Float, nullable=False, index=True)
    coffee_type = Column(String(100), index=True)
    
    __table_args__ = (
        Index('idx_coffee_timestamp_desc', timestamp.desc()),
        Index('idx_coffee_type_timestamp', 'coffee_type', 'timestamp'),
    )

