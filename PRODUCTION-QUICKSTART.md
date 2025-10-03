# Production Quick Start

## 🚀 Deploy in 5 Minutes

### 1. Prepare Environment
```bash
# Copy production config
cp .env.production.example .env.production

# Generate secure API key
openssl rand -hex 32

# Edit .env.production and set:
nano .env.production
```

**Required changes**:
- `POSTGRES_PASSWORD` → Strong password
- `API_KEY` → Output from openssl command above
- `DOMAIN` → Your production domain
- `ALLOWED_HOSTS` → Your domain
- `CORS_ORIGINS` → Your frontend URLs

### 2. Login to GitHub Container Registry

**If public image** (skip this step):
```bash
# No login needed!
```

**If private image**:
```bash
# Create GitHub token with read:packages scope
export GITHUB_TOKEN=your_token_here

# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u dny1020 --password-stdin
```

### 3. Deploy

```bash
# Pull and start production services
make prod-up

# Or manually:
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### 4. Verify

```bash
# Check status
make prod-status

# Check health
curl http://localhost:8000/health

# Check logs
make prod-logs
```

---

## 📦 Available Images

CI/CD automatically builds and pushes to GHCR:

| Image | Description | Use Case |
|-------|-------------|----------|
| `ghcr.io/dny1020/coffee-tracker:latest` | Latest main branch | Production |
| `ghcr.io/dny1020/coffee-tracker:main-<sha>` | Specific commit | Pinned version |
| `ghcr.io/dny1020/coffee-tracker:develop` | Develop branch | Staging |

---

## 🔄 Common Operations

### Update to Latest
```bash
make prod-update
```

### Rollback to Previous Version
```bash
# Option 1: Interactive
make prod-rollback
# Enter: main-abc1234

# Option 2: Direct
IMAGE_TAG=main-abc1234 make prod-update
```

### View Logs
```bash
make prod-logs
```

### Backup Database
```bash
make prod-backup
```

### Restart Services
```bash
make prod-restart
```

### Check Production Readiness
```bash
make prod-check
```

---

## 🛠️ Makefile Commands

### Production Commands
```bash
make prod-up          # Start production services
make prod-down        # Stop production services
make prod-logs        # View logs
make prod-pull        # Pull latest images
make prod-update      # Update to latest and restart
make prod-rollback    # Rollback to previous version
make prod-status      # Check status and health
make prod-backup      # Backup database
make prod-shell       # Access container shell
make prod-restart     # Restart services
make prod-check       # Check production readiness
```

### Development Commands
```bash
make dev              # Start dev environment
make up               # Start services
make down             # Stop services
make logs             # View logs
make test             # Run tests
make health           # Check health
make backup           # Backup database
```

---

## 📁 Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Development (builds locally) |
| `docker-compose.prod.yml` | Production (uses GHCR images) |
| `.env.example` | Development environment template |
| `.env.production.example` | Production environment template |
| `.env.production` | Your production config (not in git) |

---

## 🔐 Security Checklist

Before production:

- [ ] Changed `POSTGRES_PASSWORD` from default
- [ ] Changed `API_KEY` from default (use `openssl rand -hex 32`)
- [ ] Set `DEBUG=false`
- [ ] Set `FASTAPI_ENV=production`
- [ ] Updated `ALLOWED_HOSTS` with your domain
- [ ] Updated `CORS_ORIGINS` with your frontend
- [ ] Set `METRICS_PUBLIC=false`
- [ ] Configured `DOMAIN` for Traefik
- [ ] SSL certificate configured
- [ ] Backups scheduled

---

## 🌐 Networking

### Create Traefik Network (if needed)
```bash
docker network create traefik_net
```

### Port Mappings
- `8000` → Coffee Tracker API
- `5432` → PostgreSQL (internal only)
- `6379` → Redis (internal only)

---

## 🐛 Troubleshooting

### Cannot pull image
```bash
# Check authentication
docker login ghcr.io -u dny1020

# Verify image exists
docker pull ghcr.io/dny1020/coffee-tracker:latest
```

### Container won't start
```bash
# Check logs
make prod-logs

# Check environment
docker exec coffee-tracker env | grep -E "API_KEY|DATABASE"

# Verify database
docker exec coffee-tracker-postgres pg_isready -U coffee
```

### Health check fails
```bash
# Check API directly
curl http://localhost:8000/health

# Check from inside container
docker exec coffee-tracker curl http://localhost:8000/health

# Check database connection
docker exec coffee-tracker-postgres psql -U coffee -c "SELECT 1"
```

---

## 📚 Documentation

- Full deployment guide: `DEPLOYMENT.md`
- CI/CD pipeline: `.github/CI-CD-GUIDE.md`
- Test documentation: `QUICK-START-TESTS.md`
- API documentation: `http://localhost:8000/docs`

---

## 🆘 Support

```bash
# View all commands
make help

# Check system status
make prod-status

# View recent logs
make prod-logs | tail -100
```

---

**Quick Deploy Command**:
```bash
cp .env.production.example .env.production && \
nano .env.production && \
make prod-up
```

✅ That's it! Your Coffee Tracker API is production-ready!
