from fastapi import FastAPI, Depends
from app.database import init_db
from app.routers import coffee, heartrate
from app.auth import verify_api_key

app = FastAPI(title="Coffee Tracker", version="1.0.0")

# Initialize database
init_db()

# Include routers with auth dependency
app.include_router(
    coffee.router, 
    prefix="/coffee", 
    tags=["coffee"],
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    heartrate.router, 
    prefix="/heartrate", 
    tags=["heartrate"],
    dependencies=[Depends(verify_api_key)]
)

@app.get("/")
def root():
    return {"message": "Coffee addiction tracker running"}

@app.get("/health")
def health_check():
    return {"status": "alive", "probably": "overcaffeinated"}