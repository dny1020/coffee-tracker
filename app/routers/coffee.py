from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import logging

from app.database import get_db
from app.models import CoffeeLog
from app.core import limiter, settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models with validation


class CoffeeCreate(BaseModel):
    caffeine_mg: float = Field(..., ge=0, le=1000, description="Caffeine in mg (0-1000)")
    coffee_type: Optional[str] = Field(None, max_length=100, description="Type of coffee")

    @field_validator('caffeine_mg')
    @classmethod
    def validate_caffeine(cls, v):
        if v > settings.max_caffeine_mg:
            raise ValueError(f'Caffeine amount over {settings.max_caffeine_mg}mg is dangerous')
        return v

    @field_validator('coffee_type')
    @classmethod
    def validate_coffee_type(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class CoffeeResponse(BaseModel):
    id: int
    timestamp: datetime
    caffeine_mg: float
    coffee_type: Optional[str]

    model_config = {"from_attributes": True}


@router.post("/", response_model=CoffeeResponse)
@limiter.limit("100/hour")
def log_coffee(coffee: CoffeeCreate, request: Request, db: Session = Depends(get_db)):
    """Log coffee consumption"""
    db_coffee = CoffeeLog(**coffee.dict())
    db.add(db_coffee)
    db.commit()
    db.refresh(db_coffee)
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


@router.get("/active")
def get_active_caffeine(db: Session = Depends(get_db)):
    """
    Calculate current active caffeine in the system.
    Uses a 5-hour half-life decay model.
    """
    now = datetime.now(timezone.utc)
    # Get logs from the last 24 hours (caffeine older than 24h is negligible)
    from datetime import timedelta
    cutoff = now - timedelta(hours=24)
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= cutoff).all()
    
    total_active = 0.0
    HALF_LIFE_HOURS = 5.0
    
    for log in logs:
        # hours_passed = (now - log.timestamp.replace(tzinfo=timezone.utc)).total_seconds() / 3600
        # Correctly handle potential naive/aware datetimes
        log_time = log.timestamp
        if log_time.tzinfo is None:
            log_time = log_time.replace(tzinfo=timezone.utc)
        
        hours_passed = (now - log_time).total_seconds() / 3600
        # Decay formula: N(t) = N0 * (0.5)^(t/h)
        active = log.caffeine_mg * (0.5 ** (hours_passed / HALF_LIFE_HOURS))
        total_active += active
    
    return {
        "active_caffeine_mg": round(total_active, 2),
        "timestamp": now,
        "unit": "mg",
        "formula": "5-hour half-life exponential decay"
    }


@router.get("/summary")
def get_daily_summary(db: Session = Depends(get_db)):
    """
    Get a summary of today's consumption and health insights.
    """
    now = datetime.now(timezone.utc)
    start_of_day = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
    
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= start_of_day).all()
    total_mg = sum(log.caffeine_mg for log in logs)
    
    limit = settings.recommended_daily_caffeine_mg
    percent = (total_mg / limit) * 100 if limit > 0 else 0
    
    # Simple sleep insight
    # If more than 100mg active and it's late, sleep might be affected
    active_data = get_active_caffeine(db)
    active_mg = active_data["active_caffeine_mg"]
    
    status = "Good"
    insight = "You are within recommended limits."
    if total_mg > limit:
        status = "Warning"
        insight = f"You have exceeded the recommended daily limit of {limit}mg!"
    elif active_mg > 100 and now.hour >= 20:
        status = "Caution"
        insight = "High active caffeine levels late in the day might affect your sleep quality."

    return {
        "date": now.date(),
        "total_caffeine_mg": round(total_mg, 2),
        "daily_limit_mg": limit,
        "limit_reached_percent": round(percent, 1),
        "active_caffeine_mg": active_mg,
        "status": status,
        "insight": insight,
        "logs_count": len(logs)
    }

