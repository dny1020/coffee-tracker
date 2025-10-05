# Coffee Tracker - Complete Setup Summary

## ✅ What's Been Completed

### 1. Core Application
- ✅ FastAPI application with coffee and heart rate logging
- ✅ PostgreSQL database with proper migrations
- ✅ Redis for rate limiting
- ✅ Input validation (caffeine: 0-1000mg, BPM: 30-250)
- ✅ API authentication via Bearer token
- ✅ Comprehensive test suite (11 tests passing)
- ✅ Health monitoring endpoints

### 2. CI/CD Pipeline
- ✅ GitHub Actions workflow configured
- ✅ Automated testing on push/PR
- ✅ Security scanning (Trivy, Trufflehog)
- ✅ Docker image build and push to GHCR
- ✅ Multi-architecture support (amd64, arm64)

### 3. Production Deployment
- ✅ Unified `docker-compose.yml` with 5 services:
  - PostgreSQL (database)
  - Redis (rate limiting)
  - Coffee Tracker API (main app)
  - Prometheus (metrics collection)
  - Grafana (visualization)
- ✅ Traefik integration for SSL/HTTPS
- ✅ Proper networking (internal, traefik_net, monitoring)
- ✅ Health checks for all services
- ✅ Resource limits configured

### 4. Monitoring & Observability
- ✅ Prometheus metrics at `/metrics`
- ✅ Grafana dashboards configured
- ✅ Auto-provisioned Prometheus datasource
- ✅ Custom Coffee Tracker dashboard
- ✅ Request/response metrics
- ✅ Structured logging

### 5. Documentation
- ✅ API documentation (`/docs`, `/redoc`)
- ✅ Apple Shortcuts integration guide
- ✅ Security guidelines
- ✅ Deployment guide
- ✅ Contributing guide
- ✅ Runbook for operations

## 🚀 Deployment Instructions

### Prerequisites
```bash
# On your production server
- Docker & Docker Compose installed
- Traefik reverse proxy running
- Domain configured: coffee.danilocloud.me
```

### Step 1: Clone Repository
```bash
git clone https://github.com/dny1020/coffee-tracker.git
cd coffee-tracker
```

### Step 2: Configure Environment
```bash
# Copy and edit .env file
cp .env.example .env
nano .env

# Required variables:
POSTGRES_PASSWORD=your-secure-password
API_KEY=your-api-key
DOMAIN=coffee.danilocloud.me
```

### Step 3: Create Traefik Network (if not exists)
```bash
docker network create traefik_net
```

### Step 4: Deploy
```bash
# Pull latest image and start all services
docker-compose pull
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify all services are running
docker-compose ps
```

### Step 5: Verify Deployment
```bash
# Check API health
curl https://coffee.danilocloud.me/health

# Check API info
curl https://coffee.danilocloud.me/

# Check Prometheus
curl https://prometheus.danilocloud.me/-/healthy

# Check Grafana
curl https://grafana.danilocloud.me/api/health
```

## 🔧 Configuration Details

### Environment Variables (.env)
```bash
# Database
POSTGRES_USER=coffee
POSTGRES_PASSWORD=89hjKK**
POSTGRES_DB=coffee_db
DATABASE_URL=postgresql+psycopg2://coffee:89hjKK**@postgres:5432/coffee_db

# API
API_KEY=coffee-addict-secret-key-2025
FASTAPI_ENV=production
DEBUG=false
LOG_LEVEL=info

# Docker Image
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:latest

# Domain
DOMAIN=coffee.danilocloud.me
ALLOWED_HOSTS=localhost,127.0.0.1,coffee.danilocloud.me
CORS_ORIGINS=https://danilocloud.me

# Security
METRICS_PUBLIC=false  # Prometheus has API key in prometheus.yml
SECURITY_HEADERS=true

# Timezone
TZ=UTC

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin  # CHANGE THIS!
```

### Prometheus Configuration (prometheus.yml)
```yaml
scrape_configs:
  - job_name: 'coffee-tracker-api'
    authorization:
      type: Bearer
      credentials: 'coffee-addict-secret-key-2025'  # Matches API_KEY
    static_configs:
      - targets: ['coffee-tracker:8000']
```

## 🔐 Security Checklist

- ✅ API key authentication enabled
- ✅ HTTPS via Traefik
- ✅ Security headers enabled
- ✅ Rate limiting configured
- ✅ Trusted host middleware
- ✅ CORS properly configured
- ✅ Database credentials secured
- ✅ No secrets in git repository
- ✅ Container resource limits set
- ✅ Internal network isolation

## 🏗️ Architecture

```
Internet
   ↓
Traefik (HTTPS/SSL)
   ↓
┌──────────────────────────────────────────┐
│  Coffee Tracker Ecosystem                │
│                                          │
│  ┌─────────────┐    ┌──────────────┐   │
│  │  Coffee API │←→  │  PostgreSQL  │   │
│  │  (FastAPI)  │    │              │   │
│  └──────┬──────┘    └──────────────┘   │
│         │                               │
│         ↓                               │
│  ┌─────────────┐                       │
│  │    Redis    │  (Rate Limiting)      │
│  └─────────────┘                       │
│                                          │
│  ┌──────────────┐   ┌──────────────┐   │
│  │  Prometheus  │←→ │   Grafana    │   │
│  │  (Metrics)   │   │ (Dashboard)  │   │
│  └──────────────┘   └──────────────┘   │
└──────────────────────────────────────────┘
```

## 📊 Metrics & Monitoring

### Prometheus Targets
- **coffee-tracker-api**: http://coffee-tracker:8000/metrics
  - Authentication: Bearer token
  - Scrape interval: 10s

### Grafana Access
- **URL**: https://grafana.danilocloud.me
- **Default Login**: admin/admin (CHANGE THIS!)
- **Datasource**: Prometheus (auto-configured)
- **Dashboard**: Coffee Tracker Overview

### Key Metrics
- `coffee_total_caffeine_mg` - Total caffeine logged
- `heartrate_latest_bpm` - Latest heart rate reading
- `coffee_logs_today_count` - Number of coffee logs today
- `heartrate_logs_today_count` - Number of heart rate logs today
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram

## 📱 Apple Shortcuts Integration

See detailed guide in `SHORTCUTS.md`

### Quick Example
```bash
# Log coffee via curl (same as Shortcuts uses)
curl -X POST https://coffee.danilocloud.me/coffee/ \
  -H "Authorization: Bearer coffee-addict-secret-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "caffeine_mg": 120,
    "coffee_type": "americano",
    "notes": "morning coffee"
  }'

# Log heart rate
curl -X POST https://coffee.danilocloud.me/heartrate/ \
  -H "Authorization: Bearer coffee-addict-secret-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "bpm": 75,
    "context": "resting",
    "notes": "before coffee"
  }'
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if database is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify database exists
docker-compose exec postgres psql -U coffee -d coffee_db -c "\l"
```

### Prometheus Not Scraping Metrics
```bash
# Check if API is accessible from Prometheus
docker-compose exec prometheus wget -O- http://coffee-tracker:8000/metrics

# Verify API key in prometheus.yml matches .env
grep "credentials" prometheus.yml
grep "API_KEY" .env
```

### Can't Access /docs or /redoc
```bash
# Check if app is running
docker-compose logs coffee-tracker

# Test direct access
curl -v http://localhost:8000/docs

# Check Traefik routing
curl -H "Host: coffee.danilocloud.me" http://localhost/docs
```

### Database "coffee" Does Not Exist
This was a previous issue. Fixed by ensuring `POSTGRES_DB=coffee_db` in `.env` and healthcheck uses correct DB name.

## 🔄 Updates & Maintenance

### Update to Latest Version
```bash
# Pull latest image
docker-compose pull coffee-tracker

# Recreate container
docker-compose up -d coffee-tracker

# Check logs
docker-compose logs -f coffee-tracker
```

### Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U coffee coffee_db > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20251004.sql | docker-compose exec -T postgres psql -U coffee coffee_db
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f coffee-tracker
docker-compose logs -f postgres
docker-compose logs -f prometheus
```

## 📋 Next Steps

1. **Change default passwords** in `.env` (Grafana, Postgres)
2. **Set up alerts** in Prometheus for high caffeine/heart rate
3. **Create custom Grafana dashboards** for your use case
4. **Configure backups** for PostgreSQL data
5. **Set up log aggregation** (optional: ELK stack)
6. **Enable GitHub Actions secrets** for automated deployments
7. **Create Apple Shortcuts** on your iPhone

## 📚 Additional Resources

- **API Docs**: https://coffee.danilocloud.me/docs
- **ReDoc**: https://coffee.danilocloud.me/redoc
- **Prometheus**: https://prometheus.danilocloud.me
- **Grafana**: https://grafana.danilocloud.me
- **GitHub Repo**: https://github.com/dny1020/coffee-tracker
- **Issues**: https://github.com/dny1020/coffee-tracker/issues

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Review this guide and `TROUBLESHOOTING.md`
3. Check GitHub Issues
4. Create new issue with logs and error details

---

**Last Updated**: 2025-10-04
**Version**: 1.0.0
**Status**: ✅ Production Ready
