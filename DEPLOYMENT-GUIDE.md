# Coffee Tracker - Complete Deployment Guide

## Overview

This guide covers deploying the Coffee Tracker API with PostgreSQL, Redis, Prometheus, and Grafana using Docker Compose and Traefik reverse proxy.

## Prerequisites

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Traefik** reverse proxy with `traefik_net` network
- **Domain names** configured (DNS A records pointing to your server):
  - `coffee.danilocloud.me`
  - `prometheus.danilocloud.me` (optional)
  - `grafana.danilocloud.me` (optional)

## Quick Start

### 1. Clone and Configure

```bash
# Navigate to project directory
cd /opt/coffee-tracker

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. Configure Environment Variables

Edit `.env` with **your production values**:

```bash
# Database (CRITICAL: Change password!)
POSTGRES_USER=coffee
POSTGRES_PASSWORD=your-strong-password-here
POSTGRES_DB=coffee_db

# API Authentication (CRITICAL: Change this!)
API_KEY=your-secret-api-key-here

# Domain
DOMAIN=coffee.danilocloud.me

# Docker Image (use GHCR for production)
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:latest
# Or build locally: comment out DOCKER_IMAGE

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,coffee.danilocloud.me
CORS_ORIGINS=https://danilocloud.me

# Metrics
METRICS_PUBLIC=true

# Grafana (optional)
GRAFANA_ADMIN_PASSWORD=your-grafana-password
```

### 3. Deploy

#### Option A: Full Stack (API + Monitoring)

```bash
docker-compose -f docker-compose.unified.yml up -d
```

#### Option B: API Only

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Deployment

```bash
# Check all containers are running
docker ps

# Check API health
curl https://coffee.danilocloud.me/health

# Check logs
docker-compose -f docker-compose.unified.yml logs -f coffee-tracker
```

## Architecture

```
                          ┌─────────────┐
                          │   Traefik   │
                          │(Reverse Proxy)│
                          └──────┬──────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
          ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
          │Coffee Tracker│ │ Prometheus │ │  Grafana   │
          │     API      │ │            │ │            │
          └──────┬───────┘ └─────┬──────┘ └─────┬──────┘
                 │               │               │
        ┌────────┴────────┐      │               │
        │                 │      │               │
   ┌────▼────┐      ┌────▼────┐ │               │
   │PostgreSQL│      │  Redis  │ │               │
   └─────────┘      └─────────┘ │               │
        │                 │      │               │
        └─────────────────┴──────┴───────────────┘
                   internal network
```

## Services

### Coffee Tracker API (Port 8000)
- **URL**: https://coffee.danilocloud.me
- **Endpoints**: `/docs`, `/health`, `/coffee/`, `/heartrate/`
- **Metrics**: `/metrics` (for Prometheus)

### PostgreSQL (Port 5432 - internal only)
- **Database**: `coffee_db`
- **User**: `coffee`
- **Volume**: `pg_data` (persistent)

### Redis (Port 6379 - internal only)
- **Purpose**: Rate limiting
- **Volume**: `redis_data` (persistent)

### Prometheus (Port 9090)
- **URL**: https://prometheus.danilocloud.me or http://localhost:9090
- **Purpose**: Metrics collection
- **Retention**: 30 days
- **Volume**: `prometheus_data`

### Grafana (Port 3000)
- **URL**: https://grafana.danilocloud.me or http://localhost:3000
- **Default Login**: admin/admin (change on first login!)
- **Volume**: `grafana_data`

## Network Architecture

### Networks

1. **traefik_net** (external)
   - Connects services to Traefik reverse proxy
   - Must exist before deployment

2. **internal** (bridge)
   - PostgreSQL, Redis, API communication
   - Not exposed externally

3. **monitoring** (bridge)
   - Prometheus, Grafana, API metrics
   - Internal monitoring communication

### Create Traefik Network (if needed)

```bash
docker network create traefik_net
```

## Troubleshooting

### Issue: Database "coffee" does not exist

**Cause**: Mismatch between `POSTGRES_DB` and connection string

**Fix**:
```bash
# Check .env file
grep POSTGRES /opt/coffee-tracker/.env

# Should be:
POSTGRES_DB=coffee_db
DATABASE_URL=postgresql+psycopg2://coffee:PASSWORD@postgres:5432/coffee_db
```

**Restart services**:
```bash
docker-compose -f docker-compose.unified.yml down
docker-compose -f docker-compose.unified.yml up -d
```

### Issue: /docs and /redoc not loading

**Cause 1**: JavaScript/CSS blocked by browser  
**Fix**: Check browser console, disable ad blockers

**Cause 2**: Database connection issue  
**Fix**: Check health endpoint
```bash
curl https://coffee.danilocloud.me/health
```

**Cause 3**: Container still starting  
**Fix**: Wait 30 seconds, check logs
```bash
docker logs coffee-tracker
```

### Issue: Prometheus shows "DOWN" for coffee-tracker-api

**Cause**: Host header rejection or network issue

**Fix**:
1. **Check ALLOWED_HOSTS** in `.env`:
   ```bash
   ALLOWED_HOSTS=localhost,127.0.0.1,coffee.danilocloud.me,prometheus,coffee-tracker
   ```

2. **Set METRICS_PUBLIC=true**:
   ```bash
   METRICS_PUBLIC=true
   ```

3. **Restart services**:
   ```bash
   docker-compose -f docker-compose.unified.yml restart coffee-tracker
   ```

4. **Test metrics endpoint**:
   ```bash
   docker exec coffee-tracker curl -s http://localhost:8000/metrics | head -20
   ```

### Issue: Network "traefik_net" not found

**Fix**:
```bash
docker network create traefik_net
```

### Issue: Network has active endpoints error

**Cause**: Trying to use multiple compose files simultaneously

**Fix**: Use unified compose file only
```bash
# Stop all services
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prometheus.yml down

# Start unified
docker-compose -f docker-compose.unified.yml up -d
```

## Database Management

### Backup Database

```bash
# Manual backup
docker exec coffee-tracker-postgres pg_dump -U coffee coffee_db > backup_$(date +%Y%m%d).sql

# Automated backup (add to crontab)
0 2 * * * docker exec coffee-tracker-postgres pg_dump -U coffee coffee_db | gzip > /backups/coffee_$(date +\%Y\%m\%d).sql.gz
```

### Restore Database

```bash
# Stop API
docker-compose -f docker-compose.unified.yml stop coffee-tracker

# Restore
cat backup.sql | docker exec -i coffee-tracker-postgres psql -U coffee -d coffee_db

# Restart
docker-compose -f docker-compose.unified.yml start coffee-tracker
```

### Access Database

```bash
docker exec -it coffee-tracker-postgres psql -U coffee -d coffee_db
```

## Monitoring Setup

### Configure Prometheus Data Source in Grafana

1. Open Grafana: https://grafana.danilocloud.me
2. Login (admin/admin)
3. Go to: Configuration → Data Sources → Add data source
4. Select: **Prometheus**
5. Configure:
   - **URL**: `http://prometheus:9090`
   - **Access**: Server (default)
6. Click: **Save & Test**

### Import Dashboard

1. Go to: Dashboards → Import
2. Upload: `./grafana/dashboards/coffee-tracker.json` (if exists)
3. Or create custom dashboard with metrics:
   - `http_requests_total`
   - `coffee_logged_total`
   - `caffeine_mg_total`
   - `heartrate_bpm_current`

## Security Checklist

- [ ] Changed `API_KEY` from default
- [ ] Changed `POSTGRES_PASSWORD` from default
- [ ] Changed Grafana admin password
- [ ] Configured `ALLOWED_HOSTS` correctly
- [ ] Configured `CORS_ORIGINS` correctly
- [ ] HTTPS enabled via Traefik
- [ ] Firewall rules configured (ports 80, 443 only)
- [ ] Database not exposed externally
- [ ] Redis not exposed externally
- [ ] Regular backups configured

## Maintenance

### Update to Latest Image

```bash
# Pull latest
docker pull ghcr.io/dny1020/coffee-tracker:latest

# Restart with new image
docker-compose -f docker-compose.unified.yml up -d --force-recreate coffee-tracker
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.unified.yml logs -f

# Specific service
docker logs -f coffee-tracker
docker logs -f coffee-tracker-postgres
docker logs -f coffee-tracker-prometheus
```

### Restart Services

```bash
# All
docker-compose -f docker-compose.unified.yml restart

# Specific service
docker-compose -f docker-compose.unified.yml restart coffee-tracker
```

### Stop/Start

```bash
# Stop all
docker-compose -f docker-compose.unified.yml down

# Start all
docker-compose -f docker-compose.unified.yml up -d
```

## CI/CD Integration

### GitHub Actions Auto-Deploy

Images are automatically built and pushed to GitHub Container Registry on push to `main` branch.

**Image naming**:
- `ghcr.io/dny1020/coffee-tracker:latest` - Latest main branch
- `ghcr.io/dny1020/coffee-tracker:main-<sha>` - Specific commit

**To use specific commit**:
```bash
# In .env
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:main-abc1234
```

## Performance Tuning

### Resource Limits

See `deploy.resources` in docker-compose files.

Current limits:
- **API**: 1 CPU, 512MB RAM
- **PostgreSQL**: 1 CPU, 512MB RAM
- **Redis**: 0.5 CPU, 256MB RAM
- **Prometheus**: 0.5 CPU, 512MB RAM
- **Grafana**: 0.5 CPU, 512MB RAM

### Scaling

```bash
# Scale API (if load balancer configured)
docker-compose -f docker-compose.unified.yml up -d --scale coffee-tracker=3
```

## Support

- **Documentation**: `/docs` on API
- **Health Check**: `https://coffee.danilocloud.me/health`
- **Logs**: `docker logs coffee-tracker`
- **Metrics**: `https://coffee.danilocloud.me/metrics`

## References

- [README.md](./README.md) - Project overview
- [RUNBOOK.md](./RUNBOOK.md) - Operations guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [APPLE-SHORTCUTS-GUIDE.md](./APPLE-SHORTCUTS-GUIDE.md) - Mobile integration

---

**Last Updated**: 2024-10-05  
**Version**: 1.0.0
