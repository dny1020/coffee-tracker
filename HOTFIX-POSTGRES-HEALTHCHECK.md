# PostgreSQL Health Check Fix - UPDATED

## Issue

PostgreSQL health check was failing with:
```
FATAL: database "coffee" does not exist
```

## Root Cause

**First attempt (INCORRECT)**:
```yaml
test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-coffee}", "-d", "${POSTGRES_DB:-coffee_db}"]
```

Problem: Docker Compose doesn't expand environment variables (`${...}`) in the `CMD` form of healthcheck!

## Correct Fix

**Updated fix (CORRECT)**:
```yaml
test: ["CMD-SHELL", "pg_isready -U coffee -d coffee_db"]
```

Using `CMD-SHELL` instead of `CMD` allows:
- Shell execution
- Direct string commands (no array parsing)
- Works with hardcoded values

## Files Updated

- ✅ `docker-compose.yml` - Updated to use CMD-SHELL
- ✅ `docker-compose.prod.yml` - Updated to use CMD-SHELL

## How to Apply

### Quick Fix (Restart)

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Pull latest changes
git pull

# Restart
docker-compose -f docker-compose.prod.yml up -d

# Verify (should see no database errors)
docker-compose -f docker-compose.prod.yml logs postgres | tail -20
```

## Verification

After fix, check:
```bash
docker exec coffee-tracker-postgres pg_isready -U coffee -d coffee_db
# Should output: accepting connections
```

## /docs and /redoc Not Loading

If pages don't load in browser, run these diagnostics:

```bash
# Test if endpoint returns HTML
curl -I http://localhost:8000/docs
curl -s http://localhost:8000/docs | head -30

# Test OpenAPI JSON
curl http://localhost:8000/openapi.json | jq . | head -20

# Check logs
docker logs coffee-tracker --tail 50
```

Check browser console (F12) for JavaScript/CORS errors.

## Workaround for /docs

If Swagger UI doesn't load, use:
- External Swagger: https://petstore.swagger.io/
- Paste: `http://localhost:8000/openapi.json`

---

**Updated**: October 2025  
**Status**: Health check fixed with CMD-SHELL
