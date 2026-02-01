from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time
import os
import logging
import sys

# Import database lazily inside functions to avoid SQLAlchemy import at module import time under Python 3.13
import uuid
from app.routers import coffee
from app.auth import verify_api_key
from app.settings import settings
from app.limiter import limiter

"""Application instance and middleware wiring."""

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("☕ Coffee Tracker API starting up...")
    logger.info(f"📊 Database: {os.getenv('DATABASE_URL', 'sqlite:///data/coffee.db')}")
    logger.info(f"🔐 Authentication: {'Enabled' if os.getenv('API_KEY') else 'Default key'}")
    logger.info(f"📝 Log level: {settings.log_level.upper()}")
    logger.info("🚀 Ready to track your caffeine addiction!")
    if not os.getenv("SKIP_DB_INIT"):
        try:
            from app.database import init_db as _init_db
            _init_db()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.warning(f"DB init skipped/failed: {e}", exc_info=True)
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("💤 Coffee Tracker API shutting down...")
    logger.info("☕ Hope you enjoyed tracking your addiction!")


app = FastAPI(
    title="Coffee Tracker API",
    version="1.0.0",
    description="Track your caffeine addiction with scientific precision ☕",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# Add rate limiting middleware (skip in tests to avoid threading deadlocks with TestClient)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
if not os.getenv("PYTEST_CURRENT_TEST"):
    app.add_middleware(SlowAPIMiddleware)

# CORS middleware for web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware for security
# Note: Traefik/reverse proxy needs to be in allowed hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.parsed_allowed_hosts() + [
        # Legacy / additional hosts that may still be used in deployment
        "testserver", "*.coffee-tracker.local",
        # Docker internal networking
        "coffee-tracker", "coffee-tracker:8000"
    ]
)

@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.time()

    # Enforce max body size for POST/PUT/PATCH requests
    # Note: We can't read the body here without consuming it, so we'll check
    # Content-Length header instead
    if request.method in ("POST", "PUT", "PATCH"):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_request_body_bytes:
            raise HTTPException(status_code=413, detail="Request body too large")

    response = await call_next(request)
    duration = time.time() - start

    # Structured logging
    logger.info(
        "Request processed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 1)
        }
    )

    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.6f}"
    if settings.security_headers:
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "0")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        
        # CSP: Allow Swagger UI and ReDoc to load from CDN while maintaining security
        # Note: /docs and /redoc paths will have relaxed CSP, API endpoints remain strict
        if request.url.path in ["/api/v1/docs", "/api/v1/redoc", "/docs", "/redoc"]:
            # Relaxed CSP for documentation pages that need external resources
            response.headers.setdefault("Content-Security-Policy", 
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        else:
            # Strict CSP for API endpoints
            response.headers.setdefault("Content-Security-Policy", 
                "default-src 'none'; "
                "frame-ancestors 'none'; "
                "base-uri 'none'; "
                "form-action 'self'"
            )
    return response

# Database will be initialized on startup; set SKIP_DB_INIT to skip.
# Include routers with auth dependency and rate limiting
app.include_router(
    coffee.router,
    prefix="/api/v1/coffee",
    tags=["coffee"],
    dependencies=[Depends(verify_api_key)]
)


@app.get("/api/v1/")
@limiter.limit("30/minute")
def root(request: Request):
    """Root endpoint with basic info"""
    return {
        "message": "Coffee addiction tracker running",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health",
        "api_endpoints": {
            "coffee": "/api/v1/coffee/",
            "heartrate": "/api/v1/heartrate/"
        }
    }


@app.get("/api/v1/health")
@limiter.limit("60/minute")
def health_check(request: Request):
    """Enhanced health check endpoint for monitoring"""
    health_status = {
        "status": "alive",
        "timestamp": time.time(),
        "probably": "overcaffeinated"
    }
    
    # Check database connection
    try:
        from app.database import SessionLocal
        from app.models import CoffeeLog
        db = SessionLocal() if SessionLocal is not None else None
        if db is not None:
            # Try a simple query to verify database is working
            db.query(CoffeeLog).count()
            db.close()
            health_status["database"] = {
                "status": "healthy",
                "type": "postgresql" if "postgresql" in os.getenv("DATABASE_URL", "") else "sqlite"
            }
        else:
            health_status["database"] = {"status": "not-initialized"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        health_status["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Overall status
    if health_status.get("database", {}).get("status") == "unhealthy":
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/api/v1/info")
@limiter.limit("10/minute")
def api_info(request: Request):
    """API information and usage guidelines"""
    return {
        "api_name": "Coffee Tracker",
        "version": "1.0.0",
        "description": "Track caffeine consumption and heart rate correlation",
        "authentication": "Bearer token required",
        "rate_limits": {
            "general": "30 requests per minute",
            "health": "60 requests per minute",
            "coffee_logging": "100 requests per hour",
            "heartrate_logging": "200 requests per hour"
        },
        "validation_rules": {
            "caffeine_mg": "0-1000 mg range",
            "heart_rate": "30-250 BPM range",
            "notes_max_length": "1000 characters"
        },
        "endpoints": {
            "coffee": {
                "POST /api/v1/coffee/": "Log coffee consumption",
                "GET /api/v1/coffee/today": "Today's caffeine total",
                "GET /api/v1/coffee/week": "Weekly breakdown",
                "GET /api/v1/coffee/stats": "Consumption statistics"
            },
            "heartrate": {
                "POST /api/v1/heartrate/": "Log heart rate reading",
                "GET /api/v1/heartrate/current": "Latest heart rate",
                "GET /api/v1/heartrate/correlation": "Caffeine correlation analysis",
                "GET /api/v1/heartrate/stats": "Heart rate statistics"
            }
        }
    }


@app.get("/metrics")
@app.get("/api/v1/metrics")
def metrics(request: Request):
    """Prometheus metrics endpoint"""
    if not settings.metrics_public:
        # If metrics are not public, require authentication
        verify_api_key(request)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
