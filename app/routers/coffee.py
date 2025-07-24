from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import CoffeeLog

router = APIRouter()

# Pydantic models
class CoffeeCreate(BaseModel):
   caffeine_mg: float
   coffee_type: Optional[str] = None
   notes: Optional[str] = None

class CoffeeUpdate(BaseModel):
   caffeine_mg: Optional[float] = None
   coffee_type: Optional[str] = None
   notes: Optional[str] = None

class CoffeeResponse(BaseModel):
   id: int
   timestamp: datetime
   caffeine_mg: float
   coffee_type: Optional[str]
   notes: Optional[str]

   class Config:
       from_attributes = True

@router.post("/", response_model=CoffeeResponse)
def log_coffee(coffee: CoffeeCreate, db: Session = Depends(get_db)):
   """Log coffee consumption"""
   db_coffee = CoffeeLog(**coffee.dict())
   db.add(db_coffee)
   db.commit()
   db.refresh(db_coffee)
   return db_coffee

@router.get("/today")
def get_today_caffeine(db: Session = Depends(get_db)):
   """Get total caffeine consumed today"""
   today = date.today()
   total = db.query(func.sum(CoffeeLog.caffeine_mg)).filter(
       func.date(CoffeeLog.timestamp) == today
   ).scalar() or 0
   
   return {
       "date": today,
       "total_caffeine_mg": total,
       "addiction_level": "severe" if total > 400 else "moderate" if total > 200 else "amateur"
   }

@router.get("/week")
def get_week_caffeine(db: Session = Depends(get_db)):
   """Get daily caffeine totals for last 7 days"""
   result = db.query(
       func.date(CoffeeLog.timestamp).label('date'),
       func.sum(CoffeeLog.caffeine_mg).label('total_mg')
   ).group_by(func.date(CoffeeLog.timestamp)).limit(7).all()
   
   return [{"date": r.date, "total_mg": r.total_mg} for r in result]

@router.get("/", response_model=List[CoffeeResponse])
def get_coffee_logs(limit: int = 50, db: Session = Depends(get_db)):
   """Get recent coffee logs"""
   logs = db.query(CoffeeLog).order_by(CoffeeLog.timestamp.desc()).limit(limit).all()
   return logs

@router.put("/{coffee_id}", response_model=CoffeeResponse)
def update_coffee(coffee_id: int, coffee: CoffeeUpdate, db: Session = Depends(get_db)):
   """Fix wrong caffeine entry"""
   db_coffee = db.query(CoffeeLog).filter(CoffeeLog.id == coffee_id).first()
   if not db_coffee:
       raise HTTPException(status_code=404, detail="Coffee log not found")
   
   for field, value in coffee.dict(exclude_unset=True).items():
       setattr(db_coffee, field, value)
   
   db.commit()
   db.refresh(db_coffee)
   return db_coffee

@router.delete("/{coffee_id}")
def delete_coffee(coffee_id: int, db: Session = Depends(get_db)):
   """Delete coffee log (for when you lied about consumption)"""
   db_coffee = db.query(CoffeeLog).filter(CoffeeLog.id == coffee_id).first()
   if not db_coffee:
       raise HTTPException(status_code=404, detail="Coffee log not found")
   
   db.delete(db_coffee)
   db.commit()
   return {"message": "Coffee log deleted"}
