# Coffee Tracker API

Track your caffeine consumption and heart rate with statistical analysis.

## Quick Start

```bash
# 1. Clone and configure
git clone <repo-url>
cd coffee-tracker
cp .env.example .env
# Edit .env and set your API_KEY and POSTGRES_PASSWORD

# 2. Start services
docker-compose up -d

# 3. Test
curl http://localhost:8000/api/v1/health
```

## API Documentation

- **Base URL**: `http://localhost:8000/api/v1/`
- **Swagger UI**: `/api/v1/docs`
- **ReDoc**: `/api/v1/redoc`

### Authentication

All endpoints require Bearer token authentication:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/v1/coffee/today
```

## Main Endpoints

### Coffee
- `POST /coffee/` - Log coffee consumption
- `GET /coffee/today` - Today's caffeine total
- `GET /coffee/week` - Weekly breakdown
- `GET /coffee/stats` - Statistics

### Heart Rate
- `POST /heartrate/` - Log heart rate reading
- `GET /heartrate/current` - Latest reading
- `GET /heartrate/correlation` - Caffeine correlation
- `GET /heartrate/stats` - Statistics

## Configuration

Key environment variables:
```env
DATABASE_URL=postgresql+psycopg2://coffee:PASSWORD@postgres:5432/coffee_db
API_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests
pytest tests/ -v

# Stop services
docker-compose down
```

## Deployment

1. Change `API_KEY` and `POSTGRES_PASSWORD` in `.env`
2. Configure `CORS_ORIGINS` and `ALLOWED_HOSTS`
3. Set up HTTPS with reverse proxy
4. Configure automated backups

See [SECURITY.md](SECURITY.md) for security checklist.

## Tech Stack

- Python 3.11+ / FastAPI
- PostgreSQL / SQLite
- Docker Compose

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.