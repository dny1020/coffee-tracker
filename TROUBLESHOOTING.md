# Coffee Tracker - Troubleshooting Guide

This guide covers common issues and their solutions for the Coffee Tracker API in production.

---

## Table of Contents

1. [Database Issues](#database-issues)
2. [Prometheus Metrics Issues](#prometheus-metrics-issues)
3. [Docker Compose Network Issues](#docker-compose-network-issues)
4. [API Documentation Not Loading](#api-documentation-not-loading)
5. [Apple Shortcuts Integration](#apple-shortcuts-integration)

---

## Database Issues

### Issue: `FATAL: database "coffee" does not exist`

**Symptoms:**
- PostgreSQL logs show: `FATAL: database "coffee" does not exist`
- API can't connect to database
- `/health` endpoint shows database unhealthy

**Root Cause:**
The environment variable configuration has a mismatch between `POSTGRES_DB` and the database name in `DATABASE_URL`.

**Solution:**

Check your `.env` file has matching database names:

```bash
# These MUST match:
POSTGRES_DB=coffee_db
DATABASE_URL=postgresql+psycopg2://coffee:${POSTGRES_PASSWORD}@postgres:5432/coffee_db
#                                                                           ^^^^^^^^^ 
#                                                                           Must match POSTGRES_DB
```

**Fix Steps:**

1. Update your `.env` file:
```bash
POSTGRES_USER=coffee
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=coffee_db
DATABASE_URL=postgresql+psycopg2://coffee:your-secure-password@postgres:5432/coffee_db
```

2. Restart the containers:
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

3. Verify the database is created:
```bash
docker exec -it coffee-tracker-postgres psql -U coffee -d coffee_db -c "\l"
```

---

## Prometheus Metrics Issues

### Issue: `Error scraping target: server returned HTTP status 400 Bad Request`

**Symptoms:**
- Prometheus shows target as DOWN
- Error message: "server returned HTTP status 400 Bad Request"
- Metrics endpoint returns 400 when accessed via Prometheus

**Root Cause:**
FastAPI's `TrustedHostMiddleware` is blocking requests from Prometheus because the Host header (`coffee-tracker:8000`) is not in the allowed hosts list.

**Solution:**

The issue has been fixed in the latest code. The `app/main.py` now includes Docker internal hostnames in the allowed hosts:

```python
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.parsed_allowed_hosts() + [
        "testserver", 
        "*.coffee-tracker.local",
        "coffee-tracker",      # ✅ Added
        "coffee-tracker:8000"  # ✅ Added
    ]
)
```

**Verification Steps:**

1. Pull the latest code:
```bash
git pull origin main
```

2. Rebuild and restart:
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

3. Test metrics endpoint manually:
```bash
# From host
curl -H "Host: coffee-tracker:8000" http://localhost:8000/metrics

# From inside Prometheus container
docker exec -it coffee-tracker-prometheus wget -O- http://coffee-tracker:8000/metrics
```

4. Check Prometheus targets:
```bash
# Open http://prometheus.danilocloud.me/targets
# Or http://localhost:9090/targets
```

---

## Docker Compose Network Issues

### Issue: `network internal declared as external, but could not be found`

**Symptoms:**
- Docker Compose fails to start with network error
- Error: "network internal declared as external, but could not be found"

**Root Cause:**
The `docker-compose.prometheus.yml` file declares `internal` network as external, but it's actually created by the production compose file.

**Solution:**

The `docker-compose.prometheus.yml` has been fixed to properly reference the network:

```yaml
networks:
  monitoring:
    driver: bridge
  traefik_net:
    external: true
  internal:
    external: false                    # ✅ Changed from true
    name: coffee-tracker_internal      # ✅ Proper name
```

**How to Use:**

1. Start production stack first:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. Then start monitoring stack:
```bash
docker-compose -f docker-compose.prometheus.yml up -d
```

3. Or combine them:
```bash
docker-compose -f docker-compose.prod.yml -f docker-compose.prometheus.yml up -d
```

---

## API Documentation Not Loading

### Issue: `/docs` and `/redoc` endpoints show blank page or 500 error

**Symptoms:**
- Navigating to `/docs` shows blank page
- `/redoc` doesn't load properly
- Console shows JavaScript errors or 500 responses

**Common Causes & Solutions:**

### Cause 1: Database Not Connected

If the database isn't properly initialized, OpenAPI schema generation might fail.

**Check:**
```bash
# Check health endpoint
curl http://coffee.danilocloud.me/health

# Should show database status: healthy
```

**Fix:**
See [Database Issues](#database-issues) section above.

### Cause 2: Reverse Proxy Configuration

If using Traefik or nginx, ensure WebSocket and static file serving is properly configured.

**Traefik labels should include:**
```yaml
labels:
  - "traefik.http.services.coffee-tracker.loadbalancer.server.port=8000"
  - "traefik.http.routers.coffee-tracker.rule=Host(`coffee.danilocloud.me`)"
```

### Cause 3: CORS Issues

Check browser console for CORS errors.

**Fix in `.env`:**
```bash
CORS_ORIGINS=https://coffee.danilocloud.me,https://danilocloud.me
```

---

## Apple Shortcuts Integration

### Issue: Shortcut returns "Unauthorized" or 401 error

**Solution:**

1. Verify your API key is correct:
```bash
# Check .env file
grep API_KEY /path/to/.env
```

2. Test with curl first:
```bash
curl -H "Authorization: Bearer your-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"caffeine_mg": 120, "coffee_type": "americano"}' \
     https://coffee.danilocloud.me/coffee/
```

3. In Apple Shortcuts, ensure:
   - Header name is exactly: `Authorization`
   - Header value is exactly: `Bearer your-api-key-here` (with space after Bearer)
   - URL has `https://` prefix
   - Content-Type is set to `application/json`

### Issue: Shortcut returns 422 Validation Error

**Common validation errors:**

1. **Caffeine out of range** (must be 0-1000mg):
```json
{"caffeine_mg": 120}  // ✅ Valid
{"caffeine_mg": 1500} // ❌ Invalid: exceeds 1000mg
```

2. **Heart rate out of range** (must be 30-250 BPM):
```json
{"bpm": 88}  // ✅ Valid
{"bpm": 25}  // ❌ Invalid: below 30
{"bpm": 300} // ❌ Invalid: above 250
```

3. **Missing required fields:**
```json
// Coffee endpoint requires:
{"caffeine_mg": 120}  // minimum

// Heart rate endpoint requires:
{"bpm": 88}  // minimum
```

### Complete Apple Shortcuts Setup

See [APPLE-SHORTCUTS-GUIDE.md](./APPLE-SHORTCUTS-GUIDE.md) for detailed step-by-step instructions.

**Quick Test Shortcut:**

1. Create new shortcut
2. Add "Get Contents of URL" action:
   - URL: `https://coffee.danilocloud.me/coffee/`
   - Method: POST
   - Headers:
     - `Authorization`: `Bearer your-api-key`
     - `Content-Type`: `application/json`
   - Request Body: JSON
     ```json
     {
       "caffeine_mg": 120,
       "coffee_type": "test"
     }
     ```
3. Add "Show Result" action
4. Run shortcut

---

## Health Monitoring

### Check Overall System Health

```bash
# API health
curl https://coffee.danilocloud.me/health | jq

# Expected healthy response:
{
  "status": "alive",
  "timestamp": 1696291200.123,
  "probably": "overcaffeinated",
  "database": {
    "status": "healthy",
    "type": "postgresql"
  },
  "redis": {
    "status": "healthy"
  }
}
```

### Check Prometheus Metrics

```bash
# Raw metrics
curl http://localhost:9090/api/v1/query?query=up

# Specific metrics
curl http://localhost:9090/api/v1/query?query=coffee_requests_total
```

### Check Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f coffee-tracker

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 coffee-tracker
```

---

## Production Deployment Checklist

Before deploying to production, verify:

- [ ] `.env` file has all required variables set
- [ ] `POSTGRES_DB` matches database name in `DATABASE_URL`
- [ ] `API_KEY` is set to a secure random value (not the default)
- [ ] `POSTGRES_PASSWORD` is set to a secure password
- [ ] `DOMAIN` is set to your production domain
- [ ] `ALLOWED_HOSTS` includes your production domain
- [ ] `CORS_ORIGINS` includes your frontend domain(s)
- [ ] `METRICS_PUBLIC` is set appropriately (true for Prometheus access)
- [ ] SSL/TLS certificates are configured in Traefik
- [ ] Docker images are pulled from GHCR: `ghcr.io/dny1020/coffee-tracker:latest`
- [ ] Database volume `pg_data` is persisted
- [ ] Redis volume `redis_data` is persisted
- [ ] Backups are configured (see Makefile)

### Quick Deploy Commands

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# With monitoring
docker-compose -f docker-compose.prod.yml -f docker-compose.prometheus.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Getting Help

If you encounter issues not covered here:

1. Check the logs: `docker-compose logs -f coffee-tracker`
2. Verify environment variables: `docker-compose config`
3. Check database connection: `docker exec -it coffee-tracker-postgres psql -U coffee -d coffee_db`
4. Test API directly: `curl http://localhost:8000/health`
5. Review [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions
6. Check [SECURITY.md](./SECURITY.md) for security best practices

---

## Emergency Procedures

### Complete Reset (Nuclear Option)

⚠️ **WARNING**: This will delete all data!

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prometheus.yml down

# Remove volumes (DELETES ALL DATA!)
docker volume rm coffee-tracker_pg_data
docker volume rm coffee-tracker_redis_data
docker volume rm coffee-tracker_prometheus_data
docker volume rm coffee-tracker_grafana_data

# Restart fresh
docker-compose -f docker-compose.prod.yml up -d
```

### Backup Before Reset

```bash
# Backup database
docker exec coffee-tracker-postgres pg_dump -U coffee coffee_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Or use Make command
make backup
```

### Restore Database

```bash
# Restore from backup
docker exec -i coffee-tracker-postgres psql -U coffee coffee_db < backup_20231003_120000.sql
```

---

**Last Updated**: 2024-10-05  
**Version**: 1.0.0
