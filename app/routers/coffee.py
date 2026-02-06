"""Coffee endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.core import CoffeeLog, limiter, settings

router = APIRouter()


class CoffeeCreate(BaseModel):
    caffeine_mg: float = Field(..., ge=0, le=1000)
    coffee_type: Optional[str] = Field(None, max_length=100)


class CoffeeResponse(BaseModel):
    id: int
    timestamp: datetime
    caffeine_mg: float
    coffee_type: Optional[str]

    model_config = {"from_attributes": True}


@router.post("/", response_model=CoffeeResponse)
@limiter.limit("100/hour")
def log_coffee(coffee: CoffeeCreate, request: Request, db: Session = Depends(get_db)):
    db_coffee = CoffeeLog(**coffee.dict())
    db.add(db_coffee)
    db.commit()
    db.refresh(db_coffee)
    return db_coffee


@router.get("/", response_model=List[CoffeeResponse])
def get_coffee_logs(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return db.query(CoffeeLog).order_by(CoffeeLog.timestamp.desc()).limit(limit).offset(offset).all()


@router.get("/stats")
def get_coffee_stats(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= cutoff).all()

    if not logs:
        return {"message": f"No data in last {days} days"}

    amounts = [log.caffeine_mg for log in logs]
    types = [log.coffee_type for log in logs if log.coffee_type]

    return {
        "period_days": days,
        "total_coffees": len(logs),
        "total_caffeine_mg": round(sum(amounts), 2),
        "average_per_day": round(sum(amounts) / days, 2),
        "average_per_coffee": round(sum(amounts) / len(logs), 2),
        "max_single_dose": max(amounts),
        "min_single_dose": min(amounts),
        "most_common_type": max(set(types), key=types.count) if types else None
    }


@router.delete("/{coffee_id}")
@limiter.limit("60/hour")
def delete_coffee(coffee_id: int, request: Request, db: Session = Depends(get_db)):
    db_coffee = db.query(CoffeeLog).filter(CoffeeLog.id == coffee_id).first()
    if not db_coffee:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_coffee)
    db.commit()
    return {"message": "Deleted", "id": coffee_id}


@router.get("/active")
def get_active_caffeine(db: Session = Depends(get_db)):
    """Calculate active caffeine using 5-hour half-life decay."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= cutoff).all()
    
    total_active = 0.0
    half_life = 5.0
    
    for log in logs:
        log_time = log.timestamp
        if log_time.tzinfo is None:
            log_time = log_time.replace(tzinfo=timezone.utc)
        hours_passed = (now - log_time).total_seconds() / 3600
        active = log.caffeine_mg * (0.5 ** (hours_passed / half_life))
        total_active += active
    
    return {"active_caffeine_mg": round(total_active, 2)}


@router.get("/summary")
def get_daily_summary(db: Session = Depends(get_db)):
    """Today's consumption summary."""
    now = datetime.now(timezone.utc)
    start_of_day = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
    
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= start_of_day).all()
    total_mg = sum(log.caffeine_mg for log in logs)
    
    limit = settings.recommended_daily_caffeine_mg
    percent = (total_mg / limit) * 100 if limit > 0 else 0
    
    active_data = get_active_caffeine(db)
    
    status = "Good"
    if total_mg > limit:
        status = "Warning - exceeded daily limit"
    elif active_data["active_caffeine_mg"] > 100 and now.hour >= 20:
        status = "Caution - high caffeine late"

    return {
        "date": str(now.date()),
        "total_caffeine_mg": round(total_mg, 2),
        "daily_limit_mg": limit,
        "percent_of_limit": round(percent, 1),
        "active_caffeine_mg": active_data["active_caffeine_mg"],
        "status": status,
        "logs_count": len(logs)
    }
