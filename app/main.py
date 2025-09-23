from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import os

# Import database lazily inside functions to avoid SQLAlchemy import at module import time under Python 3.13
from app.metrics import observe_request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from app.routers import coffee, heartrate
from app.auth import verify_api_key

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Coffee Tracker API",
    version="1.0.0",
    description="Track your caffeine addiction and cardiovascular deterioration with scientific precision",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware for web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://127.0.0.1:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.coffee-tracker.local", "testserver",
                   "coffee.newsbot.lat", "*.newsbot.lat", "coffee.danilocloud.me", "*.danilocloud.me"]
)

# Custom middleware for request logging


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Basic logging (in production, use proper logging)
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    # Add process time header
    response.headers["X-Process-Time"] = str(process_time)
    try:
        observe_request(request.method, request.url.path,
                        response.status_code, process_time)
    except Exception:
        # Never let metrics break requests
        pass
    return response

# Database will be initialized on startup; set SKIP_DB_INIT to skip.
# Include routers with auth dependency and rate limiting
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


@app.get("/metrics")
def metrics() -> Response:
    """Prometheus metrics endpoint."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/")
@limiter.limit("30/minute")
def root(request: Request):
    """Root endpoint with basic info"""
    return {
        "message": "Coffee addiction tracker running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_endpoints": {
            "coffee": "/coffee/",
            "heartrate": "/heartrate/"
        }
    }


@app.get("/health")
@limiter.limit("60/minute")
def health_check(request: Request):
    """Health check endpoint for monitoring"""
    try:
        # Test database connection by opening/closing a session
        from app.database import SessionLocal
        db = SessionLocal() if SessionLocal is not None else None
        if db is not None:
            db.close()
            db_status = "healthy"
        else:
            db_status = "not-initialized"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "alive",
        "database": db_status,
        "probably": "overcaffeinated",
        "timestamp": time.time()
    }


@app.get("/info")
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
                "POST /coffee/": "Log coffee consumption",
                "GET /coffee/today": "Today's caffeine total",
                "GET /coffee/week": "Weekly breakdown",
                "GET /coffee/stats": "Consumption statistics"
            },
            "heartrate": {
                "POST /heartrate/": "Log heart rate reading",
                "GET /heartrate/current": "Latest heart rate",
                "GET /heartrate/correlation": "Caffeine correlation analysis",
                "GET /heartrate/stats": "Heart rate statistics"
            }
        }
    }

# Add startup event for logging


@app.on_event("startup")
async def startup_event():
    print("☕ Coffee Tracker API starting up...")
    print(
        f"📊 Database: {os.getenv('DATABASE_URL', 'sqlite:///data/coffee.db')}")
    print(
        f"🔐 Authentication: {'Enabled' if os.getenv('API_KEY') else 'Default key'}")
    print("🚀 Ready to track your caffeine addiction!")
    if not os.getenv("SKIP_DB_INIT"):
        try:
            from app.database import init_db as _init_db
            _init_db()
        except Exception as e:
            print(f"⚠️  DB init skipped/failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    print("💤 Coffee Tracker API shutting down...")
    print("☕ Hope you enjoyed tracking your addiction!")
