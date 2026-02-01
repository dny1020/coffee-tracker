from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import logging

from app.database import get_db
from app.metrics import (
    COFFEE_LOGGED_TOTAL,
    CAFFEINE_MG_TOTAL,
    COFFEE_LAST_TIMESTAMP_SECONDS,
    CAFFEINE_LAST_MG,
)
from app.models import CoffeeLog
from app.limiter import limiter
from app.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models with validation


class CoffeeCreate(BaseModel):
    caffeine_mg: float = Field(..., ge=0, le=1000,
                               description="Caffeine in mg (0-1000)")
    coffee_type: Optional[str] = Field(
        None, max_length=100, description="Type of coffee")
    notes: Optional[str] = Field(
        None, max_length=1000, description="Additional notes")

    @field_validator('caffeine_mg')
    @classmethod
    def validate_caffeine(cls, v):
        if v < 0:
            raise ValueError('Caffeine amount cannot be negative')
        if v > settings.max_caffeine_mg:
            raise ValueError(f'Caffeine amount over {settings.max_caffeine_mg}mg is dangerous')
        return v

    @field_validator('coffee_type')
    @classmethod
    def validate_coffee_type(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None:
            # Basic sanitization: strip leading/trailing whitespace
            v = v.strip()
            # Remove null bytes and other control characters
            v = ''.join(char for char in v if ord(char) >= 32 or char in '\n\r\t')
        return v if v else None


class CoffeeResponse(BaseModel):
    id: int
    timestamp: datetime
    caffeine_mg: float
    coffee_type: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=CoffeeResponse)
@limiter.limit("100/hour")
def log_coffee(coffee: CoffeeCreate, request: Request, db: Session = Depends(get_db)):
    """Log coffee consumption"""
    db_coffee = CoffeeLog(**coffee.dict())
    db.add(db_coffee)
    db.commit()
    db.refresh(db_coffee)
    # Metrics
    try:
        COFFEE_LOGGED_TOTAL.labels(
            type=(db_coffee.coffee_type or "unknown")
        ).inc()
        CAFFEINE_MG_TOTAL.inc(float(db_coffee.caffeine_mg))
        CAFFEINE_LAST_MG.set(float(db_coffee.caffeine_mg))
        COFFEE_LAST_TIMESTAMP_SECONDS.set(db_coffee.timestamp.timestamp())
    except Exception as e:
        logger.error(f"Coffee metrics error: {e}", exc_info=True)
    return db_coffee


@router.get("/", response_model=List[CoffeeResponse])
def get_coffee_logs(
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get recent coffee logs with pagination"""
    logs = db.query(CoffeeLog).order_by(
        CoffeeLog.timestamp.desc()).limit(limit).offset(offset).all()
    return logs


@router.get("/stats")
def get_coffee_stats(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get caffeine consumption statistics"""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= cutoff).all()

    if not logs:
        return {"message": f"No coffee data in last {days} days", "days": days}

    caffeine_amounts = [log.caffeine_mg for log in logs]

    return {
        "period_days": days,
        "total_coffees": len(logs),
        "total_caffeine_mg": round(sum(caffeine_amounts), 2),
        "average_per_day": round(sum(caffeine_amounts) / days, 2),
        "average_per_coffee": round(sum(caffeine_amounts) / len(logs), 2),
        "max_single_dose": max(caffeine_amounts),
        "min_single_dose": min(caffeine_amounts),
        "most_common_type": get_most_common_coffee_type(logs),
        "days_with_caffeine": len(set(log.timestamp.date() for log in logs))
    }


def get_most_common_coffee_type(logs):
    """Get most common coffee type from logs"""
    types = [log.coffee_type for log in logs if log.coffee_type]
    if not types:
        return None
    return max(set(types), key=types.count)


@router.delete("/{coffee_id}")
@limiter.limit("60/hour")
def delete_coffee(coffee_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete coffee log (for when you lied about consumption)"""
    db_coffee = db.query(CoffeeLog).filter(CoffeeLog.id == coffee_id).first()
    if not db_coffee:
        raise HTTPException(status_code=404, detail="Coffee log not found")

    db.delete(db_coffee)
    db.commit()
    return {"message": "Coffee log deleted", "id": coffee_id}
