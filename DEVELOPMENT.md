# Development Setup Guide

This guide will help you set up the Coffee Tracker API for local development.

## Prerequisites

- **Docker & Docker Compose** (v20.10+ recommended)
- **Python 3.12+** (for local development without Docker)
- **Make** (optional, for using Makefile commands)
- **Git** (for version control)
- **curl** or **HTTPie** (for testing API endpoints)

## Quick Start (Docker)

The fastest way to get started is using Docker:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/coffee-tracker.git
cd coffee-tracker

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
make up
# or: docker-compose up -d

# 4. Check health
make health
# or: curl http://localhost:8000/health

# 5. View logs
make logs
# or: docker-compose logs -f

# 6. Test the API
curl http://localhost:8000/
```

That's it! The API is now running at http://localhost:8000

## Local Development (Without Docker)

For local development with faster iteration:

### 1. Set Up Python Environment

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest-watch black ruff alembic
```

### 2. Set Up Local Database

**Option A: Use SQLite (Easiest)**

```bash
# Create data directory
mkdir -p data

# Update .env to use SQLite
echo "DATABASE_URL=sqlite:///data/coffee.db" >> .env
```

**Option B: Use PostgreSQL (Recommended)**

```bash
# Start only PostgreSQL with Docker
docker-compose up -d postgres

# Update .env
echo "DATABASE_URL=postgresql+psycopg2://coffee:coffee_password@localhost:5432/coffee_db" >> .env
```

### 3. Set Up Redis (Optional)

```bash
# Start Redis with Docker
docker-compose up -d redis

# Update .env
echo "REDIS_URL=redis://localhost:6379/0" >> .env

# Or use in-memory rate limiting
echo "REDIS_URL=memory://" >> .env
```

### 4. Run the Application

```bash
# Set Python path
export PYTHONPATH=$PWD

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Application will auto-reload on code changes
```

### 5. Access the API

- **API Root**: http://localhost:8000/
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## Development Workflow

### Making Changes

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# Edit files in app/ directory

# 3. Format code
black app/ tests/
# or: make format

# 4. Lint code
ruff check app/ tests/
# or: make lint

# 5. Run tests
pytest tests/ -v
# or: make test

# 6. Test with Docker
make test-docker

# 7. Commit changes
git add .
git commit -m "Description of changes"

# 8. Push and create PR
git push origin feature/your-feature-name
```

### Hot Reloading

With `uvicorn --reload`, the server automatically restarts when you change code:

```bash
# Start with auto-reload
uvicorn app.main:app --reload

# Make changes to any .py file
# Server automatically restarts
```

### Database Changes

When you modify `app/models.py`:

```bash
# Option 1: Auto-recreate (Development)
# Just restart the app - tables auto-create

# Option 2: Use migrations (Recommended)
# Create a migration
alembic revision --autogenerate -m "Description"

# Review the migration in migrations/versions/

# Apply the migration
alembic upgrade head
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_coffee.py -v

# Run specific test
pytest tests/test_coffee.py::TestCoffeeValidation::test_negative_caffeine -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Watch mode (auto-run on changes)
pytest-watch tests/
```

### Writing Tests

```python
# tests/test_your_feature.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer coffee-addict-secret-key-2025"}

def test_your_feature():
    response = client.get("/your-endpoint", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### Manual API Testing

```bash
# Using curl
curl -X POST http://localhost:8000/coffee/ \
  -H "Authorization: Bearer coffee-addict-secret-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"caffeine_mg": 95, "coffee_type": "espresso"}'

# Using HTTPie (prettier output)
http POST http://localhost:8000/coffee/ \
  Authorization:"Bearer coffee-addict-secret-key-2025" \
  caffeine_mg:=95 \
  coffee_type="espresso"
```

## Project Structure

```
coffee-tracker/
├── app/                    # Application code
│   ├── __init__.py
│   ├── main.py            # FastAPI app & middleware
│   ├── models.py          # SQLAlchemy models
│   ├── database.py        # Database connection
│   ├── settings.py        # Configuration
│   ├── auth.py            # Authentication
│   ├── limiter.py         # Rate limiting
│   ├── metrics.py         # Prometheus metrics
│   └── routers/           # API endpoints
│       ├── coffee.py      # Coffee endpoints
│       └── heartrate.py   # Heartrate endpoints
├── tests/                 # Test suite
│   ├── test_smoke.py
│   ├── test_coffee.py
│   ├── test_heartrate.py
│   └── test_auth.py
├── data/                  # SQLite database (gitignored)
├── migrations/            # Alembic migrations (after init)
├── docker-compose.yml     # Docker services
├── Dockerfile             # Container image
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── Makefile              # Build automation
└── README.md             # Main documentation
```

## Common Development Tasks

### Reset Database

```bash
# Docker
docker-compose down -v
docker-compose up -d

# Local SQLite
rm -f data/coffee.db
# Restart app to recreate
```

### View Database Contents

```bash
# PostgreSQL (Docker)
docker-compose exec postgres psql -U coffee coffee_db

# SQLite
sqlite3 data/coffee.db
sqlite> .tables
sqlite> SELECT * FROM coffee_logs;
```

### Check Logs

```bash
# Docker
docker-compose logs -f coffee-tracker

# Local
# Logs print to console where you ran uvicorn
```

### Clear Redis Cache

```bash
# Docker
docker-compose exec redis redis-cli FLUSHALL

# Local
redis-cli FLUSHALL
```

### Generate Test Data

```bash
# Create a script to generate test data
cat > generate_data.py << 'EOF'
import requests
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer coffee-addict-secret-key-2025"}

# Generate coffee logs
for i in range(50):
    data = {
        "caffeine_mg": random.randint(50, 200),
        "coffee_type": random.choice(["espresso", "latte", "americano", "cappuccino"]),
        "notes": f"Coffee #{i+1}"
    }
    response = requests.post(f"{BASE_URL}/coffee/", json=data, headers=HEADERS)
    print(f"Created coffee log: {response.status_code}")

# Generate heart rate logs
for i in range(100):
    data = {
        "bpm": random.randint(60, 120),
        "context": random.choice(["resting", "active", "post-coffee"]),
        "notes": f"Reading #{i+1}"
    }
    response = requests.post(f"{BASE_URL}/heartrate/", json=data, headers=HEADERS)
    print(f"Created heartrate log: {response.status_code}")

print("Test data generated!")
EOF

python generate_data.py
```

## Debugging

### Enable Debug Mode

```bash
# In .env
DEBUG=true
LOG_LEVEL=debug

# Restart the application
```

### Debug with VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### Debug with Pdb

```python
# Add to any file
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/coffee.db` | Database connection string |
| `API_KEY` | `coffee-addict-secret-key-2025` | API authentication key |
| `REDIS_URL` | `memory://` | Redis connection string |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `info` | Logging level |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |
| `MAX_CAFFEINE_MG` | `1000` | Maximum caffeine per entry |
| `RECOMMENDED_DAILY_CAFFEINE_MG` | `400` | Daily caffeine recommendation |

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### Module Not Found

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=$PWD

# Or install in editable mode
pip install -e .
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres pg_isready -U coffee

# View PostgreSQL logs
docker-compose logs postgres
```

### Redis Connection Error

```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Should return: PONG
```

## Getting Help

- **Documentation**: See README.md for API usage
- **Security**: See SECURITY.md for security info
- **Migrations**: See MIGRATIONS.md for database migrations
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

See CONTRIBUTING.md for detailed guidelines.
