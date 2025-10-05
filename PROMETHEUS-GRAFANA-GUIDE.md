# Prometheus & Grafana Monitoring Setup

Complete monitoring stack for Coffee Tracker API with Prometheus metrics and Grafana dashboards.

---

## 🚀 Quick Start

### 1. Start Monitoring Stack

```bash
# Start main services + monitoring
docker-compose -f docker-compose.yml -f docker-compose.prometheus.yml up -d

# Or if using production
docker-compose -f docker-compose.prod.yml -f docker-compose.prometheus.yml up -d
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin` (change on first login)
  
- **Prometheus**: http://localhost:9090
  - No authentication by default

### 3. View Metrics

- **API Metrics**: http://localhost:8000/metrics
- **Grafana Dashboard**: Pre-configured "Coffee Tracker - Health & Performance"

---

## 📊 Architecture

```
┌─────────────────┐
│  Coffee Tracker │ ──┐
│   FastAPI :8000 │   │
└─────────────────┘   │
                      │ /metrics
                      ▼
                ┌─────────────┐
                │ Prometheus  │
                │    :9090    │
                └─────────────┘
                      │
                      │ datasource
                      ▼
                ┌─────────────┐
                │   Grafana   │
                │    :3000    │
                └─────────────┘
```

---

## 📈 Available Metrics

### Coffee Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `coffee_logged_total` | Counter | Total coffee entries (by type) |
| `caffeine_mg_total` | Counter | Total caffeine consumed (mg) |
| `caffeine_last_mg` | Gauge | Last coffee caffeine amount |
| `coffee_last_timestamp_seconds` | Gauge | Timestamp of last coffee |

### Heart Rate Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `heartrate_logged_total` | Counter | Total HR readings (by context) |
| `heartrate_bpm_current` | Gauge | Current heart rate (BPM) |
| `heartrate_last_timestamp_seconds` | Gauge | Timestamp of last reading |

### API Performance Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests (by method, path, status) |
| `http_request_duration_seconds` | Histogram | Request latency distribution |

---

## 📊 Grafana Dashboard

### Pre-configured Panels

1. **Total Caffeine Today** - Gauge showing daily caffeine intake
2. **Current Heart Rate** - Real-time heart rate display
3. **Coffee Logs per Minute** - Time series by coffee type
4. **Caffeine Intake Over Time** - Trending caffeine consumption
5. **Heart Rate Over Time** - HR trending with thresholds
6. **Coffee Types Distribution** - Pie chart of coffee preferences
7. **Heart Rate by Context** - Bar chart showing HR contexts
8. **Daily Activity Summary** - Total logs summary
9. **API Request Rate** - Requests per second by endpoint
10. **API Response Time** - p95 and p99 latency

### Customize Dashboard

1. Open Grafana: http://localhost:3000
2. Navigate to **Dashboards** → **Coffee Tracker**
3. Click **Edit** on any panel
4. Modify queries, visualization, or thresholds
5. **Save** dashboard

---

## 🔧 Configuration Files

### `prometheus.yml`

Prometheus scrape configuration:

```yaml
scrape_configs:
  - job_name: 'coffee-tracker-api'
    scrape_interval: 10s
    metrics_path: '/metrics'
    static_configs:
      - targets: ['coffee-tracker:8000']
```

**Key Settings**:
- Scrape interval: 10 seconds
- Metrics endpoint: `/metrics`
- Target: `coffee-tracker:8000` (Docker service name)

### `docker-compose.prometheus.yml`

Monitoring services configuration:

**Services**:
- `prometheus` - Metrics storage and querying
- `grafana` - Visualization and dashboards

**Volumes**:
- `prometheus_data` - Time series data persistence
- `grafana_data` - Dashboard and config persistence

**Networks**:
- `monitoring` - Internal network for Prometheus/Grafana
- `internal` - Connects to Coffee Tracker API

---

## 🔐 Security Configuration

### Protect Metrics Endpoint

By default, metrics are public. To secure:

**Option 1: Disable Public Access**

In `.env`:
```bash
METRICS_PUBLIC=false
```

This requires API key authentication:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/metrics
```

**Option 2: Configure Prometheus Authentication**

Edit `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'coffee-tracker-api'
    bearer_token: 'your-api-key-here'
    # OR
    basic_auth:
      username: 'prometheus'
      password: 'secure-password'
```

### Change Grafana Password

1. Login: http://localhost:3000 (admin/admin)
2. Skip or set new password on first login
3. Or set via environment variable:

Edit `docker-compose.prometheus.yml`:
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=your-secure-password
```

---

## 📊 PromQL Query Examples

### Coffee Queries

**Total caffeine today**:
```promql
increase(caffeine_mg_total[24h])
```

**Coffee logs per hour**:
```promql
rate(coffee_logged_total[1h]) * 3600
```

**Coffee types breakdown**:
```promql
sum by(type) (increase(coffee_logged_total[24h]))
```

**Last coffee time**:
```promql
coffee_last_timestamp_seconds
```

### Heart Rate Queries

**Current heart rate**:
```promql
heartrate_bpm_current
```

**Average HR over 1 hour**:
```promql
avg_over_time(heartrate_bpm_current[1h])
```

**HR readings by context**:
```promql
sum by(context) (increase(heartrate_logged_total[1h]))
```

### API Performance Queries

**Request rate (requests/sec)**:
```promql
rate(http_requests_total[5m])
```

**95th percentile latency**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Error rate**:
```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

---

## 🎯 Common Use Cases

### Monitor Daily Caffeine Intake

**Alert when over 400mg**:
```promql
increase(caffeine_mg_total[24h]) > 400
```

### Track Heart Rate Correlation

**Compare HR before/after coffee**:
```promql
heartrate_bpm_current offset 30m
```

### API Health Monitoring

**High latency alert**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
```

**High error rate**:
```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m])) > 0.01
```

---

## 🔍 Troubleshooting

### Prometheus Not Scraping

**Check target status**:
1. Open http://localhost:9090/targets
2. Look for `coffee-tracker-api` target
3. Status should be "UP"

**If DOWN**:
- Check Coffee Tracker is running: `docker ps | grep coffee-tracker`
- Verify network connectivity: `docker network inspect internal`
- Check metrics endpoint: `curl http://localhost:8000/metrics`

### Grafana No Data

**Check datasource**:
1. Grafana → Configuration → Data Sources
2. Click "Prometheus"
3. Click "Test" button
4. Should show "Data source is working"

**If failing**:
- Check Prometheus is running: `docker ps | grep prometheus`
- Verify URL: `http://prometheus:9090`
- Check network: Both services in `monitoring` network

### Metrics Endpoint 403 Forbidden

**If METRICS_PUBLIC=false**:

Update `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'coffee-tracker-api'
    bearer_token: 'your-api-key-from-env'
```

Restart Prometheus:
```bash
docker-compose -f docker-compose.prometheus.yml restart prometheus
```

---

## 📈 Advanced Configuration

### Add Alerting

**1. Create alerts.yml**:
```yaml
groups:
  - name: coffee_tracker_alerts
    interval: 30s
    rules:
      - alert: HighCaffeineIntake
        expr: increase(caffeine_mg_total[24h]) > 400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High caffeine intake detected"
          description: "Daily caffeine > 400mg"
```

**2. Update prometheus.yml**:
```yaml
rule_files:
  - "alerts.yml"
```

### Add More Exporters

**PostgreSQL Exporter**:
```yaml
postgres-exporter:
  image: prometheuscommunity/postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://coffee:password@postgres:5432/coffee_db?sslmode=disable"
  networks:
    - internal
    - monitoring
```

**Redis Exporter**:
```yaml
redis-exporter:
  image: oliver006/redis_exporter
  command: ["--redis.addr=redis:6379"]
  networks:
    - internal
    - monitoring
```

---

## 📊 Data Retention

### Prometheus

**Default**: 15 days

**Change retention**:

Edit `docker-compose.prometheus.yml`:
```yaml
command:
  - '--storage.tsdb.retention.time=30d'
  - '--storage.tsdb.retention.size=10GB'
```

### Grafana

**Data stored in**: `grafana_data` volume

**Backup**:
```bash
docker run --rm \
  -v coffee-tracker_grafana_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/grafana-backup-$(date +%Y%m%d).tar.gz /data
```

---

## 🎨 Creating Custom Dashboards

### 1. Create New Dashboard

1. Grafana → Create → Dashboard
2. Add Panel
3. Select **Prometheus** datasource
4. Enter PromQL query
5. Configure visualization
6. Save

### 2. Example Panel: Today's Coffee Count

**Query**:
```promql
sum(increase(coffee_logged_total[24h]))
```

**Visualization**: Stat  
**Title**: "Coffees Today"  
**Unit**: short (number)

### 3. Export Dashboard

1. Dashboard → Settings (gear icon)
2. JSON Model
3. Copy JSON
4. Save to `grafana/dashboards/my-dashboard.json`
5. Reload Grafana to auto-import

---

## 🚀 Production Best Practices

1. **Secure Endpoints**:
   - Set `METRICS_PUBLIC=false`
   - Use authentication for Prometheus scraping
   - Change Grafana admin password

2. **Resource Limits**:
   - Already configured in compose file
   - Adjust based on your load

3. **Data Retention**:
   - Balance between retention and storage
   - Archive old data if needed

4. **Backups**:
   - Regularly backup Grafana dashboards
   - Export important dashboards as JSON

5. **Monitoring the Monitoring**:
   - Check Prometheus targets regularly
   - Set up alerts for scrape failures

---

## 📚 Resources

- **Prometheus Docs**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/
- **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Dashboard Examples**: https://grafana.com/grafana/dashboards/

---

## 🎯 Quick Commands

```bash
# Start monitoring
docker-compose -f docker-compose.yml -f docker-compose.prometheus.yml up -d

# View logs
docker-compose -f docker-compose.prometheus.yml logs -f

# Stop monitoring
docker-compose -f docker-compose.prometheus.yml down

# Restart Prometheus (after config change)
docker-compose -f docker-compose.prometheus.yml restart prometheus

# Backup Grafana
docker run --rm -v coffee-tracker_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Test metrics endpoint
curl http://localhost:8000/metrics
```

---

**Status**: ✅ Ready for Production  
**Last Updated**: October 2025  
**Version**: 1.0
