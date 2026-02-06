"""Coffee Tracker API."""
from fastapi import FastAPI, Depends
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
import os
import logging

from app.routers import coffee
from app.core import verify_api_key, settings, limiter

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Coffee Tracker API...")
    if not os.getenv("SKIP_DB_INIT"):
        try:
            from app.database import init_db
            init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init failed: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Coffee Tracker API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
if not os.getenv("PYTEST_CURRENT_TEST"):
    app.add_middleware(SlowAPIMiddleware)

# Routes
app.include_router(
    coffee.router,
    prefix="/api/v1/coffee",
    tags=["coffee"],
    dependencies=[Depends(verify_api_key)]
)


@app.get("/api/v1/")
def root():
    return {
        "message": "Coffee Tracker API",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health"
    }


@app.get("/api/v1/health")
def health_check():
    try:
        from app.database import SessionLocal
        from app.core import CoffeeLog
        if SessionLocal:
            db = SessionLocal()
            db.query(CoffeeLog).first()
            db.close()
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
    return {"status": "healthy"}
