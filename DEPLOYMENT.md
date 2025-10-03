# Production Deployment Guide

## Overview

This guide covers deploying the Coffee Tracker API to production using Docker Compose with pre-built images from GitHub Container Registry (GHCR).

## Prerequisites

- Docker & Docker Compose installed
- Access to GitHub Container Registry images
- Domain configured (if using Traefik)
- SSL certificate (if using HTTPS)

---

## Deployment Options

### Option 1: Development (Build Locally)

Use the standard `docker-compose.yml`:

```bash
# Build and run locally
docker-compose up -d
```

### Option 2: Production (Use Pre-built Images)

Use `docker-compose.prod.yml` with images from GHCR:

```bash
# Pull and run pre-built images
docker-compose -f docker-compose.prod.yml up -d
```

---

## Production Deployment Steps

### 1. Prepare Environment File

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit with your production values
nano .env.production
```

**Required Changes**:
- ✅ `POSTGRES_PASSWORD` - Strong database password
- ✅ `API_KEY` - Secure random API key (use `openssl rand -hex 32`)
- ✅ `ALLOWED_HOSTS` - Your production domain(s)
- ✅ `CORS_ORIGINS` - Your frontend domain(s)
- ✅ `DOMAIN` - Your production domain for Traefik

### 2. Choose Docker Image

The CI/CD pipeline publishes images to GHCR with these tags:

| Branch/Event | Image Tag | Example |
|--------------|-----------|---------|
| Main (latest) | `latest` | `ghcr.io/dny1020/coffee-tracker:latest` |
| Main (commit) | `main-<sha>` | `ghcr.io/dny1020/coffee-tracker:main-abc1234` |
| Develop | `develop` | `ghcr.io/dny1020/coffee-tracker:develop` |
| Specific commit | `<branch>-<sha>` | `ghcr.io/dny1020/coffee-tracker:feature-xyz-abc1234` |

**Set in `.env.production`**:

```bash
# Use latest from main branch
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:latest

# OR use specific commit for rollback capability
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:main-abc1234

# OR use IMAGE_TAG variable
IMAGE_TAG=latest
```

### 3. Authenticate with GitHub Container Registry

If your image is **private**, authenticate first:

```bash
# Create GitHub Personal Access Token with read:packages scope
export GITHUB_TOKEN=your_github_token

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u dny1020 --password-stdin
```

If your image is **public**, no authentication needed!

### 4. Pull and Run

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Verify Deployment

```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f coffee-tracker

# Test health endpoint
curl http://localhost:8000/health

# Test with domain (if configured)
curl https://coffee.yourdomain.com/health
```

---

## Environment Variables Reference

### Required Variables

```bash
# Database
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql+psycopg2://coffee:<password>@postgres:5432/coffee_db

# Authentication
API_KEY=<secure-random-key>

# Docker Image
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:latest
# OR
IMAGE_TAG=latest
```

### Optional Variables

```bash
# Application
FASTAPI_ENV=production
DEBUG=false
LOG_LEVEL=info

# Security
ALLOWED_HOSTS=coffee.yourdomain.com
CORS_ORIGINS=https://yourdomain.com
METRICS_PUBLIC=false

# Domain (for Traefik)
DOMAIN=coffee.yourdomain.com
```

---

## Image Management

### Pull Specific Version

```bash
# Set image tag
export IMAGE_TAG=main-abc1234

# Pull image
docker-compose -f docker-compose.prod.yml pull

# Restart with new image
docker-compose -f docker-compose.prod.yml up -d
```

### Rollback to Previous Version

```bash
# Find previous working version
docker images | grep coffee-tracker

# Update .env.production with previous tag
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:main-previous-sha

# Redeploy
docker-compose -f docker-compose.prod.yml up -d
```

### View Available Images

```bash
# List all pulled images
docker images ghcr.io/dny1020/coffee-tracker

# Check image details
docker inspect ghcr.io/dny1020/coffee-tracker:latest
```

---

## Traefik Integration

The production compose file includes Traefik labels for automatic HTTPS:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.coffee-tracker.rule=Host(`coffee.yourdomain.com`)"
  - "traefik.http.routers.coffee-tracker.entrypoints=websecure"
  - "traefik.http.routers.coffee-tracker.tls.certresolver=myresolver"
```

**Requirements**:
1. Traefik running with network `traefik_net`
2. Domain DNS pointing to your server
3. Cert resolver configured in Traefik

**Setup Traefik Network** (if not exists):

```bash
docker network create traefik_net
```

---

## Database Management

### Backup Database

```bash
# Create backup
docker exec coffee-tracker-postgres pg_dump -U coffee coffee_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Or use make command
make backup
```

### Restore Database

```bash
# Restore from backup
docker exec -i coffee-tracker-postgres psql -U coffee coffee_db < backup_file.sql
```

### View Database

```bash
# Connect to PostgreSQL
docker exec -it coffee-tracker-postgres psql -U coffee coffee_db

# In psql:
\dt              # List tables
\d coffee_logs   # Describe table
SELECT COUNT(*) FROM coffee_logs;
```

---

## Monitoring & Health Checks

### Health Check Endpoints

```bash
# Application health
curl http://localhost:8000/health

# Check response
{
  "status": "alive",
  "database": {"status": "healthy"},
  "probably": "overcaffeinated"
}
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f coffee-tracker

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 coffee-tracker
```

### Metrics (Prometheus)

```bash
# Access metrics endpoint (if METRICS_PUBLIC=true)
curl http://localhost:8000/metrics

# Or with authentication
curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/metrics
```

---

## Scaling & Updates

### Update to Latest Image

```bash
# Pull latest
docker-compose -f docker-compose.prod.yml pull coffee-tracker

# Restart with zero downtime (if using multiple replicas)
docker-compose -f docker-compose.prod.yml up -d --no-deps coffee-tracker
```

### Scale Application

```bash
# Scale to multiple instances (requires load balancer)
docker-compose -f docker-compose.prod.yml up -d --scale coffee-tracker=3
```

---

## Troubleshooting

### Issue: Cannot Pull Image

**Problem**: `Error response from daemon: unauthorized`

**Solution**:
```bash
# Re-authenticate with GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u dny1020 --password-stdin
```

### Issue: Container Keeps Restarting

**Problem**: Container in restart loop

**Solution**:
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs coffee-tracker

# Check health
docker inspect coffee-tracker | grep -A 20 "Health"

# Common causes:
# - Database connection failed (check POSTGRES_PASSWORD)
# - Missing API_KEY
# - Port already in use
```

### Issue: Database Connection Error

**Problem**: `could not connect to server`

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check PostgreSQL health
docker exec coffee-tracker-postgres pg_isready -U coffee

# Check connection string
docker exec coffee-tracker env | grep DATABASE_URL
```

### Issue: 403 Forbidden on API

**Problem**: Authentication required

**Solution**:
```bash
# Use API key in header
curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/coffee/today

# Verify API_KEY is set correctly
docker exec coffee-tracker env | grep API_KEY
```

---

## Production Checklist

Before deploying to production:

- [ ] **Security**
  - [ ] Changed default `POSTGRES_PASSWORD`
  - [ ] Changed default `API_KEY` (use `openssl rand -hex 32`)
  - [ ] Updated `ALLOWED_HOSTS` with production domain
  - [ ] Updated `CORS_ORIGINS` with frontend domain
  - [ ] Set `DEBUG=false`
  - [ ] Set `METRICS_PUBLIC=false` (unless needed)

- [ ] **Configuration**
  - [ ] Set correct `DOCKER_IMAGE` or `IMAGE_TAG`
  - [ ] Configured `DOMAIN` for Traefik
  - [ ] Set appropriate `LOG_LEVEL` (info or warning)
  - [ ] Verified `DATABASE_URL` is correct

- [ ] **Infrastructure**
  - [ ] Docker and Docker Compose installed
  - [ ] Authenticated with GHCR (if private image)
  - [ ] Traefik network created (`traefik_net`)
  - [ ] Domain DNS configured
  - [ ] SSL certificate available (via Traefik)

- [ ] **Monitoring**
  - [ ] Health checks responding
  - [ ] Logs are clean
  - [ ] Metrics accessible (if enabled)
  - [ ] Database backup configured

- [ ] **Testing**
  - [ ] `/health` endpoint returns 200
  - [ ] Can authenticate with API key
  - [ ] Can log coffee/heart rate data
  - [ ] Database persists data across restarts

---

## Quick Commands Reference

```bash
# Deploy production
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down

# Update to latest image
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Restart single service
docker-compose -f docker-compose.prod.yml restart coffee-tracker

# Backup database
docker exec coffee-tracker-postgres pg_dump -U coffee coffee_db > backup.sql

# Check health
curl http://localhost:8000/health
```

---

## CI/CD Integration

The GitHub Actions workflow automatically:

1. Builds Docker image on push to `main` or `develop`
2. Pushes to `ghcr.io/dny1020/coffee-tracker` with tags:
   - `latest` (main branch)
   - `main-<commit-sha>`
   - `develop` (develop branch)

To deploy after CI/CD:

```bash
# On your server
export IMAGE_TAG=main-abc1234  # Use specific commit from CI/CD

# Pull and deploy
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## Support

For issues:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review health: `curl http://localhost:8000/health`
- Consult: `.github/CI-CD-GUIDE.md`
- Test locally: `docker-compose up -d`

---

**Last Updated**: October 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
