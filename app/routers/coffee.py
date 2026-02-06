"""Coffee endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.core import CoffeeLog, settings

router = APIRouter()


class CoffeeIn(BaseModel):
    caffeine_mg: float = Field(..., ge=0, le=1000)
    coffee_type: Optional[str] = Field(None, max_length=100)


class CoffeeOut(BaseModel):
    id: int
    timestamp: datetime
    caffeine_mg: float
    coffee_type: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=CoffeeOut)
def create(data: CoffeeIn, db: Session = Depends(get_db)):
    coffee = CoffeeLog(caffeine_mg=data.caffeine_mg, coffee_type=data.coffee_type)
    db.add(coffee)
    db.commit()
    db.refresh(coffee)
    return coffee


@router.get("/", response_model=List[CoffeeOut])
def list_all(limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    return db.query(CoffeeLog).order_by(CoffeeLog.timestamp.desc()).limit(limit).all()


@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    coffee = db.query(CoffeeLog).filter(CoffeeLog.id == id).first()
    if not coffee:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(coffee)
    db.commit()
    return {"deleted": id}


@router.get("/today")
def today(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
    
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= start).all()
    total = sum(log.caffeine_mg for log in logs)
    
    # Calcular cafeína activa (half-life 5 horas)
    active = 0.0
    for log in logs:
        hours = (now - log.timestamp.replace(tzinfo=timezone.utc)).total_seconds() / 3600
        active += log.caffeine_mg * (0.5 ** (hours / 5))
    
    limit = settings.recommended_daily_caffeine_mg
    
    return {
        "date": str(now.date()),
        "total_mg": round(total, 1),
        "active_mg": round(active, 1),
        "limit_mg": limit,
        "percent": round((total / limit) * 100, 1) if limit else 0,
        "count": len(logs)
    }


@router.get("/stats")
def stats(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= cutoff).all()

    if not logs:
        return {"message": "No data", "days": days}

    amounts = [log.caffeine_mg for log in logs]
    types = [log.coffee_type for log in logs if log.coffee_type]

    return {
        "days": days,
        "count": len(logs),
        "total_mg": round(sum(amounts), 1),
        "avg_per_day": round(sum(amounts) / days, 1),
        "avg_per_coffee": round(sum(amounts) / len(logs), 1),
        "max_mg": max(amounts),
        "min_mg": min(amounts),
        "top_type": max(set(types), key=types.count) if types else None
    }
