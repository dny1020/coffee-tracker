# Coffee Tracker API - Operations Runbook

This runbook provides operational procedures for running and maintaining the Coffee Tracker API in production.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Daily Operations](#daily-operations)
- [Monitoring](#monitoring)
- [Common Issues](#common-issues)
- [Backup and Recovery](#backup-and-recovery)
- [Deployment](#deployment)
- [Scaling](#scaling)
- [Incident Response](#incident-response)

---

## Quick Reference

### Service Status

```bash
# Check all services
make status

# Check health endpoint
make health

# View logs
make logs

# Restart services
make restart
```

### Key URLs

- **API**: `http://localhost:8000` (or your domain)
- **Health**: `http://localhost:8000/health`
- **Docs**: `http://localhost:8000/docs`
- **Metrics**: `http://localhost:8000/metrics`

### Emergency Contacts

- **On-call Engineer**: [Your contact info]
- **Escalation**: [Team lead contact]

---

## Daily Operations

### Starting Services

```bash
# Start all services
make up

# Verify they're running
make status

# Check health
curl http://localhost:8000/health | jq
```

Expected health response:
```json
{
  "status": "alive",
  "database": {"status": "healthy"},
  "redis": {"status": "healthy"}
}
```

### Stopping Services

```bash
# Stop all services (keeps data)
make down

# Stop and remove volumes (destroys data!)
docker-compose down -v  # ⚠️ DANGER: Only for development
```

### Viewing Logs

```bash
# All services
make logs

# Specific service
docker-compose logs -f coffee-tracker
docker-compose logs -f postgres
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 coffee-tracker

# Logs since specific time
docker-compose logs --since="2025-10-02T10:00:00" coffee-tracker
```

### Log Levels

Application logs at these levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: Normal operations (default)
- `WARNING`: Potential issues
- `ERROR`: Errors that need attention
- `CRITICAL`: Critical failures

Change log level via `.env`:
```env
LOG_LEVEL=info  # Change to debug, warning, error, or critical
```

---

## Monitoring

### Health Checks

**Automated Health Check** (every 30 seconds by Docker):
```bash
docker-compose ps
```

**Manual Health Check**:
```bash
curl http://localhost:8000/health | jq
```

**What to Check**:
- `status`: Should be "alive"
- `database.status`: Should be "healthy"
- `redis.status`: Should be "healthy"

### Prometheus Metrics

**Access Metrics**:
```bash
# View metrics (requires API key if METRICS_PUBLIC=false)
curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/metrics

# Key metrics to monitor
curl -s http://localhost:8000/metrics | grep http_requests_total
curl -s http://localhost:8000/metrics | grep http_request_duration
curl -s http://localhost:8000/metrics | grep coffee_logged_total
```

**Important Metrics**:
- `http_requests_total`: Total request count (by method, path, status)
- `http_request_duration_seconds`: Request latency distribution
- `coffee_logged_total`: Number of coffee logs (by type)
- `caffeine_mg_total`: Total caffeine logged
- `heartrate_logged_total`: Number of heart rate readings

### Alerting Thresholds

Set up alerts for:
- **Error rate > 5%**: Too many 4xx/5xx responses
- **Response time > 1s (p95)**: Slow API responses
- **Database connection failures**: Indicates DB issues
- **Redis connection failures**: Rate limiting may fail
- **Disk usage > 80%**: Need to clean up or expand storage

---

## Common Issues

### Issue: API Returns 503 Service Unavailable

**Symptoms**: Health check fails, API unresponsive

**Diagnosis**:
```bash
# Check if services are running
make status

# Check logs
make logs

# Check database connection
docker-compose exec postgres pg_isready -U coffee
```

**Resolution**:
1. Check if PostgreSQL is running: `docker-compose ps postgres`
2. Restart services: `make restart`
3. Check database logs: `docker-compose logs postgres`
4. If needed, restart just database: `docker-compose restart postgres`

---

### Issue: Database Connection Errors

**Symptoms**: 
```
Error: could not connect to server: Connection refused
health["database"]["status"] = "unhealthy"
```

**Diagnosis**:
```bash
# Check PostgreSQL status
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres | tail -50

# Test connection from app container
docker-compose exec coffee-tracker nc -zv postgres 5432
```

**Resolution**:
1. Verify PostgreSQL container is running
2. Check DATABASE_URL in .env
3. Restart PostgreSQL: `docker-compose restart postgres`
4. Wait 30 seconds for health check
5. If still failing, check PostgreSQL password

---

### Issue: Redis Connection Errors

**Symptoms**:
```
Error: Error connecting to Redis
health["redis"]["status"] = "unhealthy"
```

**Diagnosis**:
```bash
# Check Redis status
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

**Resolution**:
1. Restart Redis: `docker-compose restart redis`
2. Verify REDIS_URL in .env: `redis://redis:6379/0`
3. Check if port 6379 is blocked

**Note**: If Redis fails, rate limiting falls back to in-memory mode (resets on restart)

---

### Issue: Rate Limiting Not Working

**Symptoms**: Users can exceed rate limits

**Diagnosis**:
```bash
# Check Redis connection
curl http://localhost:8000/health | jq .redis

# Check rate limiter config
grep REDIS_URL .env
```

**Resolution**:
1. Verify Redis is healthy
2. Check REDIS_URL configuration
3. Restart app to reconnect to Redis
4. In-memory fallback will work temporarily

---

### Issue: High Memory Usage

**Symptoms**: Container using >512MB RAM

**Diagnosis**:
```bash
# Check memory usage
docker stats coffee-tracker

# Check connection pool
docker-compose exec coffee-tracker ps aux
```

**Resolution**:
1. Check for connection leaks in logs
2. Restart application: `docker-compose restart coffee-tracker`
3. Consider reducing connection pool size in database.py
4. Add memory limits to docker-compose.yml

---

### Issue: Disk Space Full

**Symptoms**: Database writes fail, logs indicate no space

**Diagnosis**:
```bash
# Check disk usage
df -h

# Check Docker volumes
docker system df

# Check database size
docker-compose exec postgres psql -U coffee -d coffee_db -c "SELECT pg_size_pretty(pg_database_size('coffee_db'));"
```

**Resolution**:
1. Clean old Docker images: `docker image prune -a`
2. Remove old logs
3. Archive old backups
4. Consider database cleanup of old records

---

### Issue: Slow API Responses

**Symptoms**: Response times >1 second

**Diagnosis**:
```bash
# Check metrics
curl -s http://localhost:8000/metrics | grep http_request_duration

# Test specific endpoint
time curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/coffee/stats?days=365

# Check database performance
docker-compose exec postgres psql -U coffee -d coffee_db -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

**Resolution**:
1. Check if querying too much data (reduce days parameter)
2. Verify indexes exist on frequently queried fields
3. Consider adding Redis caching for expensive queries
4. Restart services to clear any cached issues

---

## Backup and Recovery

### Creating Backups

**Automated** (set up cron job):
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/coffee-tracker && make backup
```

**Manual Backup**:
```bash
# Backup both PostgreSQL and SQLite (if present)
make backup

# Backups saved to ./backups/ with timestamp
ls -lh backups/
```

### Restoring from Backup

**PostgreSQL Restore**:
```bash
# Stop the application
make down

# Start only PostgreSQL
docker-compose up -d postgres

# Restore from backup
docker-compose exec -T postgres psql -U coffee coffee_db < backups/postgres_YYYYMMDD_HHMMSS.sql

# Start all services
make up
```

**SQLite Restore** (if using SQLite):
```bash
# Stop services
make down

# Replace database file
cp backups/coffee_YYYYMMDD_HHMMSS.db data/coffee.db

# Start services
make up
```

### Backup Verification

**Monthly Task**: Test restore procedure
```bash
# Create test backup
make backup

# Note the timestamp
TIMESTAMP=$(ls -t backups/ | head -1 | sed 's/postgres_//;s/.sql//')

# In a test environment, restore and verify
```

---

## Deployment

### Deploying Updates

**Pre-Deployment Checklist**:
- [ ] All tests pass: `make test`
- [ ] No linting errors
- [ ] CHANGELOG.md updated
- [ ] Backup created: `make backup`
- [ ] Maintenance window scheduled (if needed)

**Deployment Steps**:

1. **Pull latest code**:
   ```bash
   git pull origin main
   ```

2. **Rebuild containers**:
   ```bash
   make build
   ```

3. **Stop services**:
   ```bash
   make down
   ```

4. **Start with new images**:
   ```bash
   make up
   ```

5. **Verify health**:
   ```bash
   make health
   make validate
   ```

6. **Monitor logs**:
   ```bash
   make logs
   ```

### Rollback Procedure

If deployment fails:

1. **Stop new version**:
   ```bash
   make down
   ```

2. **Checkout previous version**:
   ```bash
   git checkout <previous-tag>
   ```

3. **Rebuild and restart**:
   ```bash
   make build
   make up
   ```

4. **Restore database if needed**:
   ```bash
   # See Backup and Recovery section
   ```

---

## Scaling

### Vertical Scaling (Increase Resources)

**Increase Container Resources**:

Add to `docker-compose.yml`:
```yaml
services:
  coffee-tracker:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '1.0'
          memory: 512M
```

### Horizontal Scaling (Multiple Instances)

**Requirements**:
- Load balancer (nginx, HAProxy, Traefik)
- Shared Redis instance
- Shared PostgreSQL instance

**Load Balancer Example** (nginx):
```nginx
upstream coffee_tracker {
    server coffee-tracker-1:8000;
    server coffee-tracker-2:8000;
    server coffee-tracker-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://coffee_tracker;
    }
}
```

### Database Scaling

**For high load**:
- Add read replicas
- Connection pooling (already configured)
- Query optimization
- Add indexes for slow queries

---

## Incident Response

### Severity Levels

**P0 - Critical** (API completely down):
- Response time: Immediate
- Escalation: Immediate to team lead
- Example: Database corruption, container crash loop

**P1 - High** (Degraded service):
- Response time: 15 minutes
- Escalation: After 30 minutes
- Example: Slow responses, high error rate

**P2 - Medium** (Minor issues):
- Response time: 1 hour
- Escalation: After 4 hours
- Example: Single endpoint failing, rate limit issues

**P3 - Low** (No impact):
- Response time: Next business day
- Example: Cosmetic issues, documentation errors

### Incident Response Steps

1. **Acknowledge**: Confirm you're responding
2. **Assess**: Determine severity level
3. **Mitigate**: Take immediate action to restore service
4. **Communicate**: Update stakeholders
5. **Resolve**: Fix root cause
6. **Document**: Write post-mortem

### Communication Template

```
INCIDENT REPORT - [Timestamp]

Status: [INVESTIGATING/MITIGATING/RESOLVED]
Severity: [P0/P1/P2/P3]
Impact: [Description]
Current Actions: [What's being done]
ETA: [Expected resolution time]
Next Update: [When you'll provide update]
```

### Post-Mortem Template

After resolving an incident, document:
- What happened
- Root cause
- Detection time
- Resolution time
- What went well
- What could be improved
- Action items to prevent recurrence

---

## Maintenance Tasks

### Daily
- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor metrics dashboard

### Weekly
- [ ] Review backup status
- [ ] Check disk space
- [ ] Review slow query logs

### Monthly
- [ ] Test backup restore procedure
- [ ] Review and rotate logs
- [ ] Update dependencies (security patches)
- [ ] Review access logs for anomalies

### Quarterly
- [ ] Review and update this runbook
- [ ] Conduct disaster recovery drill
- [ ] Performance optimization review
- [ ] Security audit

---

## Useful Commands Reference

```bash
# Service Management
make up              # Start all services
make down            # Stop all services
make restart         # Restart all services
make status          # Check service status
make logs            # Follow all logs

# Health & Validation
make health          # Check health endpoint
make validate        # Test all public endpoints

# Database
make backup          # Backup databases
docker-compose exec postgres psql -U coffee coffee_db  # PostgreSQL shell

# Testing
make test            # Run tests locally
make test-docker     # Run tests in container

# Cleanup
make clean           # Remove containers and cache
docker system prune  # Clean Docker system

# Debugging
docker-compose exec coffee-tracker sh  # Shell into app container
docker-compose logs --tail=100 coffee-tracker  # Last 100 log lines
```

---

## Emergency Procedures

### Complete System Failure

1. **Immediate**:
   ```bash
   make down
   make backup  # If possible
   ```

2. **Restore**:
   ```bash
   git pull origin main
   make build
   make up
   ```

3. **Verify**:
   ```bash
   make health
   make validate
   ```

### Data Corruption

1. Stop services immediately
2. Do NOT restart before diagnosis
3. Contact database expert
4. Restore from last known good backup
5. Document what happened

---

## Additional Resources

- **README.md**: Setup and usage instructions
- **SECURITY.md**: Security best practices
- **CONTRIBUTING.md**: Development guidelines
- **API Docs**: http://localhost:8000/docs

---

**Remember**: When in doubt, check the logs first. Most issues leave traces there.

For questions or issues not covered here, create a GitHub issue or contact the team.
