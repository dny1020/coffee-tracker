from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import hashlib
import hmac
from dotenv import load_dotenv
from starlette.status import HTTP_401_UNAUTHORIZED

load_dotenv()

RAW_API_KEY = os.getenv("API_KEY", "coffee-addict-secret-key-2025")
API_KEY_HASH = hashlib.sha256(RAW_API_KEY.encode()).hexdigest()

security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header using constant-time hash comparison."""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    provided = credentials.credentials
    provided_hash = hashlib.sha256(provided.encode()).hexdigest()
    if not hmac.compare_digest(provided_hash, API_KEY_HASH):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True