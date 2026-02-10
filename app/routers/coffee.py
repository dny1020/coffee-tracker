"""Coffee endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

BOGOTA_TZ = ZoneInfo("America/Bogota")
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
    now = datetime.now(BOGOTA_TZ)
    start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=BOGOTA_TZ)
    
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= start.astimezone(timezone.utc)).all()
    total = sum(log.caffeine_mg for log in logs)
    
    # Tipos de café consumidos hoy
    types = [log.coffee_type for log in logs if log.coffee_type]
    
    # Horas de consumo (en hora local)
    hours = [log.timestamp.replace(tzinfo=timezone.utc).astimezone(BOGOTA_TZ).hour for log in logs]
    peak_hour = max(set(hours), key=hours.count) if hours else None
    
    return {
        "total_caffeine_mg": round(total, 1),
        "coffee_types": list(set(types)) if types else [],
        "peak_hour": peak_hour,
        "coffees": [
            {
                "time": log.timestamp.replace(tzinfo=timezone.utc).astimezone(BOGOTA_TZ).strftime("%H:%M"),
                "type": log.coffee_type,
                "caffeine_mg": log.caffeine_mg
            }
            for log in logs
        ]
    }


@router.get("/stats")
def stats(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    from collections import Counter
    
    cutoff = datetime.now(BOGOTA_TZ) - timedelta(days=days)
    logs = db.query(CoffeeLog).filter(CoffeeLog.timestamp >= cutoff.astimezone(timezone.utc)).all()

    if not logs:
        return {"total_caffeine_mg": 0, "coffee_types": [], "peak_hours": []}

    total = sum(log.caffeine_mg for log in logs)
    types = [log.coffee_type for log in logs if log.coffee_type]
    hours = [log.timestamp.replace(tzinfo=timezone.utc).astimezone(BOGOTA_TZ).hour for log in logs]
    
    # Top 3 horas con más consumo
    hour_counts = Counter(hours).most_common(3)
    peak_hours = [{"hour": h, "count": c} for h, c in hour_counts]
    
    # Tipos de café con cantidad
    type_counts = Counter(types).most_common()
    coffee_types = [{"type": t, "count": c} for t, c in type_counts]

    return {
        "total_caffeine_mg": round(total, 1),
        "coffee_types": coffee_types,
        "peak_hours": peak_hours
    }
