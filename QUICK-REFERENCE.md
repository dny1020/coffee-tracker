# Coffee Tracker - Quick Reference Card

## 🚀 Quick Start

```bash
# Deploy everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f coffee-tracker

# Restart after changes
docker-compose restart coffee-tracker
```

## 🔗 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| API | https://coffee.danilocloud.me | API Key in .env |
| Docs | https://coffee.danilocloud.me/docs | - |
| ReDoc | https://coffee.danilocloud.me/redoc | - |
| Health | https://coffee.danilocloud.me/health | - |
| Prometheus | https://prometheus.danilocloud.me | - |
| Grafana | https://grafana.danilocloud.me | admin/admin |

## 📱 Apple Shortcuts Quick Example

**Log Coffee:**
1. POST to `https://coffee.danilocloud.me/coffee/`
2. Header: `Authorization: Bearer coffee-addict-secret-key-2025`
3. Body: `{"caffeine_mg": 120, "coffee_type": "americano"}`

**Log Heart Rate:**
1. POST to `https://coffee.danilocloud.me/heartrate/`
2. Header: `Authorization: Bearer coffee-addict-secret-key-2025`
3. Body: `{"bpm": 75, "context": "resting"}`

See `SHORTCUTS.md` for detailed step-by-step instructions.

## 🔧 Common Commands

```bash
# Update to latest
docker-compose pull
docker-compose up -d

# Check logs (specific service)
docker-compose logs -f postgres
docker-compose logs -f prometheus
docker-compose logs -f grafana

# Backup database
docker-compose exec postgres pg_dump -U coffee coffee_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U coffee coffee_db

# Restart single service
docker-compose restart coffee-tracker

# Stop everything
docker-compose down

# Stop and remove volumes (CAUTION: deletes data!)
docker-compose down -v
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Database "coffee" not found | Verify `.env` has `POSTGRES_DB=coffee_db` |
| Prometheus 401 error | Check API key in `prometheus.yml` matches `.env` |
| Can't access /docs | Check Traefik routing, verify domain DNS |
| Metrics not showing | Verify `METRICS_PUBLIC=false` and prometheus has API key |

## 📊 Key Environment Variables

```bash
# Database
POSTGRES_DB=coffee_db
POSTGRES_USER=coffee
POSTGRES_PASSWORD=your-password

# API
API_KEY=your-api-key

# Docker
DOCKER_IMAGE=ghcr.io/dny1020/coffee-tracker:latest

# Domain
DOMAIN=coffee.danilocloud.me
```

## 📚 Documentation Files

- `README.md` - Project overview
- `SETUP.md` - **Complete deployment guide** ⭐
- `SHORTCUTS.md` - **Apple Shortcuts integration** ⭐
- `FINAL-SUMMARY.md` - **Resolution summary** ⭐
- `TROUBLESHOOTING.md` - Common issues
- `RUNBOOK.md` - Operations guide
- `SECURITY.md` - Security policies
- `CONTRIBUTING.md` - How to contribute

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test
pytest tests/test_coffee.py -v
```

## 🔐 Security Checklist

- [ ] Change default Grafana password (`admin/admin`)
- [ ] Update API_KEY to secure random value
- [ ] Verify POSTGRES_PASSWORD is strong
- [ ] Enable HTTPS via Traefik
- [ ] Review ALLOWED_HOSTS in .env
- [ ] Check CORS_ORIGINS in .env
- [ ] Keep .env out of git

## 📈 Metrics to Monitor

| Metric | Description |
|--------|-------------|
| `coffee_total_caffeine_mg` | Total caffeine consumed |
| `heartrate_latest_bpm` | Most recent heart rate |
| `coffee_logs_today_count` | Coffee entries today |
| `heartrate_logs_today_count` | Heart rate entries today |
| `http_requests_total` | Total API requests |
| `http_request_duration_seconds` | API response time |

## 🎯 Production Checklist

- [x] All tests passing (11/11)
- [x] Docker compose configured
- [x] Database connection working
- [x] Prometheus metrics scraping
- [x] Grafana dashboards created
- [x] CI/CD pipeline ready
- [x] Documentation complete
- [ ] Change default passwords
- [ ] Configure backups
- [ ] Set up alerts

## 🆘 Support

- Check logs: `docker-compose logs -f`
- Health check: `curl https://coffee.danilocloud.me/health`
- Review docs: `TROUBLESHOOTING.md`
- GitHub: https://github.com/dny1020/coffee-tracker/issues

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2025-10-05
