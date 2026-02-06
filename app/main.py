"""Coffee Tracker API."""
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import logging

from app.routers import coffee
from app.core import verify_api_key, settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    from app.database import init_db
    init_db()
    logger.info("Database ready")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Coffee Tracker",
    docs_url="/api/v1/docs",
    redoc_url=None,
    lifespan=lifespan
)

app.include_router(
    coffee.router,
    prefix="/api/v1/coffee",
    dependencies=[Depends(verify_api_key)]
)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
