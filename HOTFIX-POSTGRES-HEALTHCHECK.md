# PostgreSQL Health Check Fix

## Issue

PostgreSQL health check was failing with:
```
FATAL: database "coffee" does not exist
```

## Root Cause

The health check command was:
```yaml
test: ["CMD", "pg_isready", "-U", "coffee"]
```

This command tries to connect to a database named after the user (`coffee`), but the actual database is named `coffee_db` (set by `POSTGRES_DB` environment variable).

## Fix Applied

Updated health check in both `docker-compose.yml` and `docker-compose.prod.yml`:

```yaml
# Before
test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-coffee}"]

# After
test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-coffee}", "-d", "${POSTGRES_DB:-coffee_db}"]
```

Added `-d` flag to specify the correct database name.

## Impact

- **Application**: ✅ Working fine (health check error was cosmetic)
- **Health Checks**: ✅ Will now pass correctly
- **Deployment**: No data loss, just need to restart

## How to Apply Fix

### Option 1: Restart Production (Recommended)

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Pull latest changes (includes fix)
git pull

# Restart
make prod-up

# Verify
make prod-status
```

### Option 2: Manual Fix (Without Code Update)

Edit your local `docker-compose.prod.yml` and add `-d` flag to health check:

```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-coffee}", "-d", "${POSTGRES_DB:-coffee_db}"]
```

Then restart:
```bash
docker-compose -f docker-compose.prod.yml restart postgres
```

### Option 3: Continue Running (If Working)

Your application is working! The logs show:
```
coffee-tracker | INFO: "GET /health HTTP/1.1" 200 OK
coffee-tracker | INFO: "GET /docs HTTP/1.1" 200 OK
```

The health check errors are just noise. You can:
- Keep running as-is
- Apply fix during next maintenance window

## Verification

After applying fix, verify:

```bash
# Check logs (should see no database errors)
make prod-logs

# Check status (should show healthy)
make prod-status

# Test API
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "alive",
  "database": {
    "status": "healthy",
    "type": "postgresql"
  },
  "probably": "overcaffeinated"
}
```

## Prevention

This has been fixed in:
- ✅ `docker-compose.yml` (development)
- ✅ `docker-compose.prod.yml` (production)

Future deployments will not have this issue.

---

**Status**: ✅ Fixed  
**Severity**: Low (cosmetic health check error)  
**Application Impact**: None (app works fine)  
**Date**: October 2025
