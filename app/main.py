from fastapi import FastAPI
from app.database import init_db
from app.routers import coffee, heartrate

app = FastAPI(title="Coffee Tracker", version="1.0.0")

# Initialize database
init_db()

# Include routers
app.include_router(coffee.router, prefix="/coffee", tags=["coffee"])
app.include_router(heartrate.router, prefix="/heartrate", tags=["heartrate"])

@app.get("/")
def root():
   return {"message": "Coffee addiction tracker running"}

@app.get("/health")
def health_check():
   return {"status": "alive", "probably": "overcaffeinated"}

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8000)
