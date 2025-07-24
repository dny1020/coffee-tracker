from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import statistics

from app.database import get_db
from app.models import HeartRateLog, CoffeeLog

router = APIRouter()

# Pydantic models with validation
class HeartRateCreate(BaseModel):
    bpm: int = Field(..., ge=30, le=250, description="Heart rate in BPM (30-250)")
    context: Optional[str] = Field("resting", max_length=50, description="Context: resting, active, post-coffee, etc")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @field_validator('bpm')
    @classmethod
    def validate_bpm(cls, v):
        if v < 30:
            raise ValueError('Heart rate below 30 BPM indicates you are probably dead')
        if v > 250:
            raise ValueError('Heart rate over 250 BPM is medically impossible for sustained periods')
        return v
    
    @field_validator('context')
    @classmethod
    def validate_context(cls, v):
        valid_contexts = ['resting', 'active', 'post-coffee', 'exercise', 'sleeping', 'panic', 'stressed']
        if v and v.lower() not in valid_contexts:
            # Allow custom contexts but warn about standardized ones
            pass
        return v

class HeartRateUpdate(BaseModel):
    bpm: Optional[int] = Field(None, ge=30, le=250)
    context: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('bpm')
    @classmethod
    def validate_bpm(cls, v):
        if v is not None:
            if v < 30:
                raise ValueError('Heart rate below 30 BPM indicates you are probably dead')
            if v > 250:
                raise ValueError('Heart rate over 250 BPM is medically impossible')
        return v

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
    
    # More detailed status classifications
    bpm = latest.bpm
    if bpm < 50:
        status = "bradycardia (dangerously low)"
    elif bpm < 60:
        status = "bradycardia (athlete or dead)"
    elif bpm <= 100:
        status = "normal"
    elif bpm <= 120:
        status = "elevated"
    elif bpm <= 150:
        status = "tachycardia"
    elif bpm <= 180:
        status = "severe tachycardia"
    else:
        status = "call 911"
    
    # Calculate time since reading
    time_diff = datetime.now(timezone.utc) - latest.timestamp.replace(tzinfo=timezone.utc)
    minutes_ago = int(time_diff.total_seconds() / 60)
    
    return {
        "bpm": latest.bpm,
        "timestamp": latest.timestamp,
        "context": latest.context,
        "status": status,
        "minutes_ago": minutes_ago,
        "is_recent": minutes_ago < 30
    }

@router.get("/range")
def get_heartrate_range(start: datetime, end: datetime, db: Session = Depends(get_db)):
    """Get heart rate data for time period"""
    readings = db.query(HeartRateLog).filter(
        and_(HeartRateLog.timestamp >= start, HeartRateLog.timestamp <= end)
    ).order_by(HeartRateLog.timestamp).all()
    
    if not readings:
        return {"message": "No data in that range", "start": start, "end": end}
    
    bpm_values = [r.bpm for r in readings]
    
    return {
        "period": {"start": start, "end": end},
        "readings_count": len(readings),
        "stats": {
            "min_bpm": min(bpm_values),
            "max_bpm": max(bpm_values),
            "avg_bpm": round(statistics.mean(bpm_values), 1),
            "median_bpm": round(statistics.median(bpm_values), 1),
            "std_dev": round(statistics.stdev(bpm_values) if len(bpm_values) > 1 else 0, 1)
        },
        "readings": readings[:100]  # Limit to first 100 for response size
    }

@router.get("/", response_model=List[HeartRateResponse])
def get_heartrate_logs(limit: int = Query(50, ge=1, le=1000), db: Session = Depends(get_db)):
    """Get recent heart rate logs"""
    logs = db.query(HeartRateLog).order_by(HeartRateLog.timestamp.desc()).limit(limit).all()
    return logs

@router.get("/stats")
def get_heartrate_stats(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get heart rate statistics"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    logs = db.query(HeartRateLog).filter(HeartRateLog.timestamp >= cutoff).all()
    
    if not logs:
        return {"message": f"No heart rate data in last {days} days", "days": days}
    
    bpm_values = [log.bpm for log in logs]
    contexts = [log.context for log in logs if log.context]
    
    # Group by context for analysis
    context_stats = {}
    for context in set(contexts):
        context_bpm = [log.bpm for log in logs if log.context == context]
        if context_bpm:
            context_stats[context] = {
                "count": len(context_bpm),
                "avg_bpm": round(statistics.mean(context_bpm), 1),
                "min_bpm": min(context_bpm),
                "max_bpm": max(context_bpm)
            }
    
    return {
        "period_days": days,
        "total_readings": len(logs),
        "overall_stats": {
            "min_bpm": min(bpm_values),
            "max_bpm": max(bpm_values),
            "avg_bpm": round(statistics.mean(bpm_values), 1),
            "median_bpm": round(statistics.median(bpm_values), 1),
            "std_dev": round(statistics.stdev(bpm_values) if len(bpm_values) > 1 else 0, 1)
        },
        "by_context": context_stats,
        "health_assessment": assess_heart_health(bpm_values)
    }

def assess_heart_health(bpm_values):
    """Basic heart health assessment based on readings"""
    avg_bpm = statistics.mean(bpm_values)
    
    if avg_bpm < 50:
        return "Consistently low - see a doctor or you're an elite athlete"
    elif avg_bpm < 60:
        return "Low but possibly normal for athletes"
    elif avg_bpm <= 80:
        return "Excellent resting heart rate"
    elif avg_bpm <= 100:
        return "Normal range"
    elif avg_bpm <= 120:
        return "Elevated - consider lifestyle changes"
    else:
        return "Consistently high - medical consultation recommended"

@router.get("/correlation")
def get_caffeine_correlation(hours_after: int = Query(2, ge=1, le=24), db: Session = Depends(get_db)):
    """Analyze caffeine vs heart rate correlation with improved statistics"""
    correlations = []
    
    # Get coffee logs from last 30 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    coffee_logs = db.query(CoffeeLog).filter(
        CoffeeLog.timestamp >= cutoff
    ).order_by(CoffeeLog.timestamp.desc()).limit(50).all()
    
    for coffee in coffee_logs:
        # Find heart rate readings within specified hours after coffee
        start_time = coffee.timestamp + timedelta(minutes=15)  # Give 15 min for absorption
        end_time = coffee.timestamp + timedelta(hours=hours_after)
        
        hr_readings = db.query(HeartRateLog).filter(
            and_(
                HeartRateLog.timestamp >= start_time, 
                HeartRateLog.timestamp <= end_time
            )
        ).all()
        
        # Also get baseline (before coffee)
        baseline_start = coffee.timestamp - timedelta(hours=2)
        baseline_end = coffee.timestamp - timedelta(minutes=15)
        
        baseline_readings = db.query(HeartRateLog).filter(
            and_(
                HeartRateLog.timestamp >= baseline_start,
                HeartRateLog.timestamp <= baseline_end
            )
        ).all()
        
        if hr_readings:
            avg_hr_after = statistics.mean([r.bpm for r in hr_readings])
            baseline_hr = statistics.mean([r.bpm for r in baseline_readings]) if baseline_readings else None
            
            correlation_data = {
                "coffee_time": coffee.timestamp,
                "caffeine_mg": coffee.caffeine_mg,
                "coffee_type": coffee.coffee_type,
                "avg_heartrate_after": round(avg_hr_after, 1),
                "baseline_heartrate": round(baseline_hr, 1) if baseline_hr else None,
                "hr_increase": round(avg_hr_after - baseline_hr, 1) if baseline_hr else None,
                "readings_count": len(hr_readings),
                "time_window_hours": hours_after
            }
            correlations.append(correlation_data)
    
    if not correlations:
        return {
            "correlations": [],
            "summary": "Not enough data to crush your dreams of health",
            "recommendations": ["Log more coffee and heart rate data", "Try again in a few days"]
        }
    
    # Calculate overall correlation statistics
    caffeine_doses = [c["caffeine_mg"] for c in correlations]
    hr_increases = [c["hr_increase"] for c in correlations if c["hr_increase"] is not None]
    
    analysis = {
        "correlations": correlations,
        "analysis": {
            "total_correlations": len(correlations),
            "avg_caffeine_dose": round(statistics.mean(caffeine_doses), 1),
            "avg_hr_increase": round(statistics.mean(hr_increases), 1) if hr_increases else None,
            "max_hr_increase": max(hr_increases) if hr_increases else None,
            "time_window_analyzed": f"{hours_after} hours after coffee"
        }
    }
    
    # Generate summary based on data
    if hr_increases:
        avg_increase = statistics.mean(hr_increases)
        if avg_increase < 5:
            summary = "Caffeine barely affects your heart rate - impressive tolerance"
        elif avg_increase < 15:
            summary = "Moderate heart rate response to caffeine"
        elif avg_increase < 25:
            summary = "Significant heart rate increase from caffeine"
        else:
            summary = "Your heart really doesn't like caffeine"
    else:
        summary = "Not enough baseline data for proper correlation"
    
    analysis["summary"] = summary
    
    return analysis

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
    return {"message": "Heart rate log deleted", "id": heartrate_id}