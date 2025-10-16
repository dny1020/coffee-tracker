# Coffee Tracker API

Track your caffeine consumption and heart rate to quantify your addiction and watch your cardiovascular system slowly deteriorate with scientific precision.

## What it does

- Logs coffee consumption with caffeine content validation (0-1000mg)
- Tracks heart rate readings with medical context (30-250 BPM)
- Correlates caffeine intake with heart rate spikes using statistical analysis
- Provides detailed analytics on your slow descent into caffeine dependency
- Rate limits your API abuse (because even APIs need boundaries)
- Validates input so you can't log impossible vital signs



## Features

### Input Validation
- **Caffeine**: 0-1000mg range (because 1000mg+ is basically poison)
- **Heart Rate**: 30-250 BPM range (below 30 = probably dead, above 250 = physically impossible)
- **Text Fields**: Length limits to prevent essay submissions
- **Timezone Aware**: All timestamps include proper timezone information

### Rate Limiting
- **General Endpoints**: 30 requests/minute
- **Health Check**: 60 requests/minute  
- **Data Logging**: Higher limits for actual usage
- **Redis Backend**: Persistent rate limiting across container restarts

### Analytics & Correlation
- **Statistical Analysis**: Mean, median, standard deviation
- **Baseline Comparison**: Heart rate before vs after caffeine
- **Time Windows**: Configurable correlation analysis periods
- **Health Assessment**: Automated interpretation of your vital signs

### Security
- **API Key Authentication**: Bearer token required for all data endpoints
- **CORS Protection**: Configurable allowed origins
- **Trusted Hosts**: Prevents host header attacks
- **Request Logging**: Track API usage and performance

## Installation & Setup

### Prerequisites
- Docker and docker-compose
- Basic understanding that you have a caffeine problem

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd coffee-tracker
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   # Edit .env and change the default API_KEY
   ```

3. **Build and run**
   ```bash
   make up
   # or manually:
   docker-compose up --build -d
   ```

4. **Verify it's working**
   ```bash
   make health
   # or manually:
   curl http://localhost:8000/health
   ```

### Development Setup

```bash
# Start services
make up

# View logs
make logs

# Run tests
make test

# Validate API
make validate

# Check status
make status

# Stop everything
make down
```

## API Usage

### Base URL
`https://coffee.danilocloud.me/api/v1/` (production) or `http://localhost:8000/api/v1/` (local)

### Authentication
All endpoints except `/api/v1/health` and `/api/v1/` require authentication:

```bash
# Set your API key (change the default in .env)
export API_KEY="your-secret-api-key-here"

# Use in requests
curl -H "Authorization: Bearer $API_KEY" \
     https://coffee.danilocloud.me/api/v1/coffee/today
```

### Documentation
- **Swagger UI**: `https://coffee.danilocloud.me/api/v1/docs` or `http://localhost:8000/api/v1/docs`
- **ReDoc**: `https://coffee.danilocloud.me/api/v1/redoc` or `http://localhost:8000/api/v1/redoc`
- **API Info**: `https://coffee.danilocloud.me/api/v1/info` or `http://localhost:8000/api/v1/info`

### Coffee Endpoints

**Log coffee consumption:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     -X POST https://coffee.danilocloud.me/api/v1/coffee/ \
     -H "Content-Type: application/json" \
     -d '{
       "caffeine_mg": 95,
       "coffee_type": "espresso",
       "notes": "why did I drink this at 11pm"
     }'
```

**Get today's caffeine total:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     https://coffee.danilocloud.me/api/v1/coffee/today
```

**Response:**
```json
{
  "date": "2025-07-23",
  "total_caffeine_mg": 285.0,
  "addiction_level": "moderate addict",
  "recommended_max": 400,
  "over_limit": false
}
```

**Get weekly breakdown:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     https://coffee.danilocloud.me/api/v1/coffee/week
```

**Get detailed statistics:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     "https://coffee.danilocloud.me/api/v1/coffee/stats?days=30"
```

**Update coffee log:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     -X PUT https://coffee.danilocloud.me/api/v1/coffee/1 \
     -H "Content-Type: application/json" \
     -d '{"caffeine_mg": 120}'
```

### Heart Rate Endpoints

**Log heart rate:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     -X POST https://coffee.danilocloud.me/api/v1/heartrate/ \
     -H "Content-Type: application/json" \
     -d '{
       "bpm": 85,
       "context": "resting",
       "notes": "surprisingly normal"
     }'
```

**Get current heart rate:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     https://coffee.danilocloud.me/api/v1/heartrate/current
```

**Response:**
```json
{
  "bpm": 85,
  "timestamp": "2025-07-23T22:30:00Z",
  "context": "resting",
  "status": "normal",
  "minutes_ago": 2,
  "is_recent": true
}
```

**Get heart rate statistics:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     "https://coffee.danilocloud.me/api/v1/heartrate/stats?days=7"
```

**Get caffeine correlation analysis:**
```bash
curl -H "Authorization: Bearer $API_KEY" \
     "https://coffee.danilocloud.me/api/v1/heartrate/correlation?hours_after=3"
```

## Database

- **Primary Type**: PostgreSQL (Docker container)
- **Fallback / Dev Option**: SQLite (commented in `.env.example`)
- **Postgres Connection**: `postgresql+psycopg2://coffee:coffee_password@postgres:5432/coffee_db`
- **Persistence**: Docker volume `pg_data` (see `docker-compose.yml`)
- **Backup**: Use `pg_dump` (add a script or Make target) or volume snapshot
- **Performance**: Indexed via implicit PK + timestamp; consider adding composite indexes for analytics later

### Database Schema (applies to both Postgres & SQLite)

**coffee_logs table:**
- `id` - Primary key
- `timestamp` - When you consumed caffeine (timezone-aware)
- `caffeine_mg` - How much you poisoned yourself (0-1000mg)
- `coffee_type` - What type of coffee (max 100 chars)
- `notes` - Your regrets (max 1000 chars)

**heart_rate_logs table:**
- `id` - Primary key  
- `timestamp` - When measured (timezone-aware)
- `bpm` - Beats per minute (30-250 range)
- `context` - resting/active/post-coffee/panic/etc (max 50 chars)
- `notes` - How you're feeling (max 1000 chars)

## Configuration

### Environment Variables (.env)
```env
# Database
DATABASE_URL=sqlite:///data/coffee.db

# Authentication - CHANGE THIS IN PRODUCTION
API_KEY=coffee-addict-secret-key-2025

# Rate Limiting
REDIS_URL=redis://redis:6379/0

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Application
APP_NAME="Coffee Tracker"
FASTAPI_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

### Validation Rules
- **Caffeine**: 0-1000mg (over 1000mg triggers danger warning)
- **Heart Rate**: 30-250 BPM (outside range triggers medical warnings)
- **Text Fields**: Various length limits to prevent abuse
- **Rate Limits**: Configurable per endpoint type

## Deployment

### Local Development
```bash
# Quick start
make dev

# Manual steps
make build
make up
make logs
```

### Production Deployment

1. **Prepare environment:**
   ```bash
   # Copy and configure
   cp .env.example .env
   # Change API_KEY to something secure
   # Configure CORS_ORIGINS for your frontend
   ```

2. **Deploy with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

3. **Verify deployment:**
   ```bash
   make validate
   make health
   ```

## Production Deployment Checklist
- [ ] Change default API_KEY in .env
- [ ] Configure CORS_ORIGINS for your frontend
- [ ] Set up HTTPS/TLS termination (nginx reverse proxy)
- [ ] Configure log aggregation
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy (`make backup` in cron)
- [ ] Review rate limits for your usage
- [ ] Create GitHub environments for CI/CD (staging, production)
- [ ] Verify container runs as non-root user
- [ ] Test backup and restore procedures

See [PRODUCTION_READY.md](PRODUCTION_READY.md) for complete deployment guide.

### Production Improvements (October 2025)

✅ **Critical fixes applied**:
- Implemented structured logging (replaced all print() statements)
- Added non-root user to Docker container for security
- Fixed CI/CD GitHub Actions environment configuration
- Added resource limits to all containers
- Created comprehensive documentation (LICENSE, CHANGELOG, CONTRIBUTING, SECURITY, RUNBOOK)
- Added .dockerignore for optimized builds
- Added test coverage reporting with pytest-cov

See [CHANGELOG.md](CHANGELOG.md) for version history.

### Reverse Proxy (nginx example)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Development

### Make Commands
```bash
make help          # Show all available commands
make up             # Start services  
make down           # Stop services
make logs           # Show service logs
make test           # Run tests with coverage locally
make test-docker    # Run tests with coverage in Docker
make validate       # Validate API endpoints
make backup         # Backup database
make clean          # Clean up containers
make prod-check     # Production readiness check
```

### Adding New Features

1. **Add endpoint to router:**
   ```python
   # In app/routers/coffee.py or heartrate.py
   @router.get("/new-endpoint")
   def new_endpoint(db: Session = Depends(get_db)):
       return {"status": "working"}
   ```

2. **Add validation:**
   ```python
   # Use Pydantic models with field_validator
   @field_validator('field_name')
   @classmethod
   def validate_field(cls, v):
       # validation logic
       return v
   ```

3. **Test the feature:**
   ```bash
   make test
   make validate
   ```

4. **Restart services:**
   ```bash
   make restart
   ```

### Database Changes
1. Modify `models.py`
2. Rebuild container: `make build`
3. Database tables auto-update on startup

### Running Tests
```bash
# Local testing (requires Python environment)
make test                    # Run with coverage

# Docker testing (isolated environment)  
make test-docker            # Run in container with coverage

# View coverage report
open htmlcov/index.html     # After running make test

# Watch mode for development
make test-watch
```

## API Response Examples

### Coffee Today Response
```json
{
  "date": "2025-07-23",
  "total_caffeine_mg": 285.0,
  "addiction_level": "moderate addict",
  "recommended_max": 400,
  "over_limit": false
}
```

### Coffee Statistics Response
```json
{
  "period_days": 30,
  "total_coffees": 45,
  "total_caffeine_mg": 4275.0,
  "average_per_day": 142.5,
  "average_per_coffee": 95.0,
  "max_single_dose": 200.0,
  "min_single_dose": 50.0,
  "most_common_type": "espresso",
  "days_with_caffeine": 28
}
```

### Heart Rate Correlation Response
```json
{
  "correlations": [
    {
      "coffee_time": "2025-07-23T14:30:00+00:00",
      "caffeine_mg": 95.0,
      "coffee_type": "espresso",
      "avg_heartrate_after": 88.5,
      "baseline_heartrate": 72.0,
      "hr_increase": 16.5,
      "readings_count": 3,
      "time_window_hours": 2
    }
  ],
  "analysis": {
    "total_correlations": 15,
    "avg_caffeine_dose": 98.3,
    "avg_hr_increase": 14.2,
    "max_hr_increase": 28.0,
    "time_window_analyzed": "2 hours after coffee"
  },
  "summary": "Moderate heart rate response to caffeine"
}
```

## Troubleshooting

### Container won't start
```bash
# Check logs
make logs

# Common issues:
# - Port 8000 already in use: change port in docker-compose.yml
# - Redis connection failed: ensure Redis container is running
# - Permission issues: check ./data folder permissions
```

### Database issues
```bash
# Check database file
ls -la ./data/

# Recreate database
make down
rm -f ./data/coffee.db
make up
```

### API not responding
```bash
# Check container status
make status

# Test container internally
docker-compose exec coffee-tracker curl localhost:8000/health

# Check rate limiting
# If you hit rate limits, wait or restart Redis:
docker-compose restart redis
```

### Authentication errors
```bash
# Verify API key in .env
cat .env | grep API_KEY

# Test with correct header
curl -H "Authorization: Bearer your-api-key" \
     http://localhost:8000/coffee/today
```

### Performance issues
```bash
# Check database size
ls -lh ./data/coffee.db

# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Review rate limiting
curl http://localhost:8000/info
```

## Monitoring & Maintenance

### Health Monitoring
```bash
# API health
make health

# Container status  
make status

# Service logs
make logs
```

### Backup Strategy
```bash
# Manual backup
make backup

# Automated backup (add to crontab)
0 2 * * * cd /path/to/coffee-tracker && make backup
```

### Log Monitoring
The application logs requests with timing information. For production, consider:
- Log aggregation (ELK stack, Fluentd)
- Error monitoring (Sentry)
- Metrics collection (Prometheus)

## Rate Limits

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| General | 30/minute | Prevent API abuse |
| Health | 60/minute | Allow monitoring |
| Coffee Logging | 100/hour | Normal usage |
| Heart Rate | 200/hour | Frequent measurements |

Rate limits are enforced per IP address and persist across container restarts via Redis.

## Security Features

- **API Key Authentication**: Required for all data endpoints
- **Input Validation**: Prevents injection and invalid data
- **Rate Limiting**: Protects against abuse
- **CORS Protection**: Configurable allowed origins
- **Host Validation**: Prevents host header attacks
- **Request Logging**: Audit trail for debugging

## License

Do whatever you want with this. It's just tracking your slow descent into caffeine dependency.

## Contributing

1. Make it work better
2. Add more ways to shame users about their habits  
3. Don't break existing functionality
4. Keep the sarcasm
5. Add tests for new features
6. Update this README if you add endpoints

## Changelog

### v1.0.0 (Current)
- ✅ Input validation with medical ranges
- ✅ Timezone-aware timestamps
- ✅ Rate limiting with Redis
- ✅ Statistical correlation analysis
- ✅ Enhanced API documentation
- ✅ Comprehensive test suite
- ✅ Production-ready deployment
- ✅ Database performance optimizations

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributio
n guidelines.

## Documentation

- **[README.md](README.md)** - This file, setup and usage
- **[PRODUCTION_READY.md](PRODUCTION_READY.md)** - Production deployment guide
- **[RUNBOOK.md](RUNBOOK.md)** - Operations and maintenance procedures
- **[SECURITY.md](SECURITY.md)** - Security best practices and vulnerability reporting
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute to this project
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[LICENSE](LICENSE)** - MIT License

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This API will accurately track your caffeine consumption and heart rate. It will not judge you (much), but the data definitely will. The correlation analysis may reveal uncomfortable truths about your relationship with caffeine.