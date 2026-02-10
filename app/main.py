"""Coffee Tracker API."""
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import logging
import os

from app.routers import coffee
from app.core import verify_api_key, settings

# Crear directorio de logs
os.makedirs("logs", exist_ok=True)

# Configurar logger
logger = logging.getLogger("coffee_tracker")
logger.setLevel(getattr(logging, settings.log_level.upper()))

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Handler para archivo
file_handler = logging.FileHandler("logs/app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


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
