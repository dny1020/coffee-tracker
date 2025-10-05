# Coffee Tracker - Quick Start Guide

## 🚀 Deploy in 3 Steps

### 1. Configure Environment
```bash
cd /opt/coffee-tracker
cp .env.example .env
nano .env
```

**Update these critical values**:
```bash
POSTGRES_PASSWORD=your-strong-password
API_KEY=your-secret-key
DOMAIN=coffee.danilocloud.me
```

### 2. Deploy
```bash
docker-compose -f docker-compose.unified.yml up -d
```

### 3. Verify
```bash
curl https://coffee.danilocloud.me/health
```

---

## 📋 Common Commands

```bash
# View logs
docker logs -f coffee-tracker

# Restart services
docker-compose -f docker-compose.unified.yml restart

# Stop everything
docker-compose -f docker-compose.unified.yml down

# Update to latest image
docker pull ghcr.io/dny1020/coffee-tracker:latest
docker-compose -f docker-compose.unified.yml up -d --force-recreate coffee-tracker
```

---

## 🔍 Troubleshooting

### Database Error
```bash
# Check .env has POSTGRES_DB=coffee_db
grep POSTGRES_DB .env

# Restart
docker-compose -f docker-compose.unified.yml restart
```

### Prometheus Shows DOWN
```bash
# Update .env
ALLOWED_HOSTS=localhost,127.0.0.1,coffee.danilocloud.me,prometheus,coffee-tracker
METRICS_PUBLIC=true

# Restart
docker-compose -f docker-compose.unified.yml restart coffee-tracker
```

### Network Error
```bash
docker network create traefik_net
```

---

## 📱 Apple Shortcuts - Quick Setup

**Endpoint**: `https://coffee.danilocloud.me/coffee/`

**Headers**:
- `Authorization: Bearer YOUR_API_KEY`
- `Content-Type: application/json`

**Body**:
```json
{
  "caffeine_mg": 120,
  "coffee_type": "espresso"
}
```

See [APPLE-SHORTCUTS-GUIDE.md](./APPLE-SHORTCUTS-GUIDE.md) for full guide.

---

## 📚 Full Documentation

- [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) - Complete deployment
- [PRODUCTION-READY-CHECKLIST.md](./PRODUCTION-READY-CHECKLIST.md) - Verification
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [RUNBOOK.md](./RUNBOOK.md) - Operations guide

---

## ✅ Health Checks

| Check | Command |
|-------|---------|
| API | `curl https://coffee.danilocloud.me/health` |
| Docs | `curl https://coffee.danilocloud.me/docs` |
| Metrics | `curl https://coffee.danilocloud.me/metrics` |
| Prometheus | http://localhost:9090/targets |
| Grafana | http://localhost:3000 |

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0
