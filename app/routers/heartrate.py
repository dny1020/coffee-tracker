from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import HeartRateLog, CoffeeLog

router = APIRouter()

# Pydantic models
class HeartRateCreate(BaseModel):
   bpm: int
   context: Optional[str] = "resting"
   notes: Optional[str] = None

class HeartRateUpdate(BaseModel):
   bpm: Optional[int] = None
   context: Optional[str] = None
   notes: Optional[str] = None

class HeartRateResponse(BaseModel):
   id: int
   timestamp: datetime
   bpm: int
   context: Optional[str]
   notes: Optional[str]

   class Config:
       from_attributes = True

@router.post("/", response_model=HeartRateResponse)
def log_heartrate(heartrate: HeartRateCreate, db: Session = Depends(get_db)):
   """Log heart rate reading"""
   db_heartrate = HeartRateLog(**heartrate.dict())
   db.add(db_heartrate)
   db.commit()
   db.refresh(db_heartrate)
   return db_heartrate

@router.get("/current")
def get_current_heartrate(db: Session = Depends(get_db)):
   """Get latest heart rate reading"""
   latest = db.query(HeartRateLog).order_by(HeartRateLog.timestamp.desc()).first()
   if not latest:
       return {"message": "No heart rate data yet"}
   
   status = "dead" if latest.bpm < 60 else "tachycardia" if latest.bpm > 100 else "normal"
   
   return {
       "bpm": latest.bpm,
       "timestamp": latest.timestamp,
       "context": latest.context,
       "status": status
   }

@router.get("/range")
def get_heartrate_range(start: datetime, end: datetime, db: Session = Depends(get_db)):
   """Get heart rate data for time period"""
   readings = db.query(HeartRateLog).filter(
       and_(HeartRateLog.timestamp >= start, HeartRateLog.timestamp <= end)
   ).order_by(HeartRateLog.timestamp).all()
   
   if not readings:
       return {"message": "No data in that range"}
   
   bpm_values = [r.bpm for r in readings]
   
   return {
       "readings": readings,
       "stats": {
           "min_bpm": min(bpm_values),
           "max_bpm": max(bpm_values),
           "avg_bpm": sum(bpm_values) / len(bpm_values),
           "count": len(readings)
       }
   }

@router.get("/", response_model=List[HeartRateResponse])
def get_heartrate_logs(limit: int = 50, db: Session = Depends(get_db)):
   """Get recent heart rate logs"""
   logs = db.query(HeartRateLog).order_by(HeartRateLog.timestamp.desc()).limit(limit).all()
   return logs

@router.get("/correlation")
def get_caffeine_correlation(db: Session = Depends(get_db)):
   """Analyze caffeine vs heart rate correlation"""
   # Get heart rate readings from last hour after coffee consumption
   correlations = []
   
   coffee_logs = db.query(CoffeeLog).order_by(CoffeeLog.timestamp.desc()).limit(20).all()
   
   for coffee in coffee_logs:
       # Find heart rate readings 30-90 minutes after coffee
       start_time = coffee.timestamp + timedelta(minutes=30)
       end_time = coffee.timestamp + timedelta(minutes=90)
       
       hr_readings = db.query(HeartRateLog).filter(
           and_(HeartRateLog.timestamp >= start_time, HeartRateLog.timestamp <= end_time)
       ).all()
       
       if hr_readings:
           avg_hr = sum(r.bpm for r in hr_readings) / len(hr_readings)
           correlations.append({
               "coffee_time": coffee.timestamp,
               "caffeine_mg": coffee.caffeine_mg,
               "avg_heartrate_after": avg_hr,
               "readings_count": len(hr_readings)
           })
   
   return {
       "correlations": correlations,
       "summary": "Your heart probably hates you" if correlations else "Not enough data to ruin your day"
   }

@router.put("/{heartrate_id}", response_model=HeartRateResponse)
def update_heartrate(heartrate_id: int, heartrate: HeartRateUpdate, db: Session = Depends(get_db)):
   """Fix wrong heart rate entry"""
   db_heartrate = db.query(HeartRateLog).filter(HeartRateLog.id == heartrate_id).first()
   if not db_heartrate:
       raise HTTPException(status_code=404, detail="Heart rate log not found")
   
   for field, value in heartrate.dict(exclude_unset=True).items():
       setattr(db_heartrate, field, value)
   
   db.commit()
   db.refresh(db_heartrate)
   return db_heartrate

@router.delete("/{heartrate_id}")
def delete_heartrate(heartrate_id: int, db: Session = Depends(get_db)):
   """Delete heart rate log"""
   db_heartrate = db.query(HeartRateLog).filter(HeartRateLog.id == heartrate_id).first()
   if not db_heartrate:
       raise HTTPException(status_code=404, detail="Heart rate log not found")
   
   db.delete(db_heartrate)
   db.commit()
   return {"message": "Heart rate log deleted"}
