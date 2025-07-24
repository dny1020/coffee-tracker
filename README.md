# Coffee Tracker API

Track your caffeine consumption and heart rate to quantify your addiction and watch your cardiovascular system slowly deteriorate.

## What it does

- Logs coffee consumption with caffeine content
- Tracks heart rate readings
- Correlates caffeine intake with heart rate spikes
- Tells you how badly you're poisoning yourself

## Project Structure

```
coffee-tracker/
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Docker orchestration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .dockerignore            # Files excluded from Docker build
├── .gitignore               # Files excluded from git
├── README.md                # This file
├── app/
│   ├── __init__.py          # Python package marker
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database connection and setup
│   └── routers/
│       ├── __init__.py      # Router package marker
│       ├── coffee.py        # Coffee tracking endpoints
│       └── heartrate.py     # Heart rate tracking endpoints
└── data/                    # SQLite database storage (created on first run)
```

## Installation & Setup

### Prerequisites
- Docker
- docker-compose
- Basic understanding that you have a caffeine problem

### Quick Start

1. **Clone or create the project structure**
   ```bash
   mkdir coffee-tracker
   cd coffee-tracker
   # Copy all files from this repo
   ```

2. **Build and run**
   ```bash
   docker-compose up --build
   ```

3. **Verify it's working**
   ```bash
   curl http://localhost:8000/health
   ```

### Development Mode

Run in detached mode:
```bash
docker-compose up -d --build
```

View logs:
```bash
docker-compose logs -f
```

Stop everything:
```bash
docker-compose down
```

## API Usage

### Base URL
`http://localhost:8000`

### Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Coffee Endpoints

**⚠️ All endpoints require authentication with API key**

**Log coffee consumption:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     -X POST http://localhost:8000/coffee/ \
     -H "Content-Type: application/json" \
     -d '{
       "caffeine_mg": 95,
       "coffee_type": "espresso",
       "notes": "why did I drink this at 11pm"
     }'
```

**Get today's caffeine total:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     http://localhost:8000/coffee/today
```

**Get weekly summary:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     http://localhost:8000/coffee/week
```

**Update coffee log:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     -X PUT http://localhost:8000/coffee/1 \
     -H "Content-Type: application/json" \
     -d '{"caffeine_mg": 120}'
```

### Heart Rate Endpoints

**Log heart rate:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     -X POST http://localhost:8000/heartrate/ \
     -H "Content-Type: application/json" \
     -d '{
       "bpm": 85,
       "context": "resting",
       "notes": "surprisingly normal"
     }'
```

**Get current heart rate:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     http://localhost:8000/heartrate/current
```

**Get caffeine correlation analysis:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     http://localhost:8000/heartrate/correlation
```

## Database

- **Type**: SQLite
- **Location**: `./data/coffee.db`
- **Persistence**: Data survives container restarts
- **Backup**: Just copy the `./data/coffee.db` file

### Database Schema

**coffee_logs table:**
- `id` - Primary key
- `timestamp` - When you consumed caffeine
- `caffeine_mg` - How much you poisoned yourself
- `coffee_type` - What type of coffee
- `notes` - Your regrets

**heart_rate_logs table:**
- `id` - Primary key
- `timestamp` - When measured
- `bpm` - Beats per minute
- `context` - resting/active/post-coffee/panic
- `notes` - How you're feeling

## Configuration

### Environment Variables (.env)
```env
DATABASE_URL=sqlite:///data/coffee.db
FASTAPI_ENV=production
DEBUG=false
APP_NAME="Coffee Tracker"
HOST=0.0.0.0
PORT=8000
```

### Docker Configuration
- **Port**: 8000 (mapped to host 8000)
- **Volume**: `./data` mounted to `/app/data`
- **Restart**: unless-stopped
- **Health check**: `/health` endpoint

## Deployment

### Local Development
```bash
# Standard run
docker-compose up --build

# Background run
docker-compose up -d --build

# Rebuild after changes
docker-compose down
docker-compose up --build
```

### Production Deployment

**Option 1: Direct Docker**
```bash
# Build image
docker build -t coffee-tracker .

# Run container
docker run -d \
  --name coffee-tracker \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  coffee-tracker
```

**Option 2: Docker Compose (recommended)**
```bash
# Production run
docker-compose -f docker-compose.yml up -d --build
```

### Remote Server Deployment
1. Copy project to server
2. Ensure Docker/docker-compose installed
3. Run `docker-compose up -d --build`
4. Set up reverse proxy (nginx) if needed
5. Configure firewall to allow port 8000

### Data Backup
```bash
# Backup database
cp ./data/coffee.db ./backup/coffee-backup-$(date +%Y%m%d).db

# Restore database
cp ./backup/coffee-backup-20250723.db ./data/coffee.db
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Container Status
```bash
docker-compose ps
docker-compose logs coffee-tracker
```

### Database Check
```bash
# Connect to container
docker-compose exec coffee-tracker sh

# Check if database exists
ls -la /app/data/
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Common issues:
# - Port 8000 already in use
# - Missing requirements.txt dependencies
# - Permission issues with ./data folder
```

### Database issues
```bash
# Recreate database
rm -rf ./data/coffee.db
docker-compose restart
```

### API not responding
```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs -f coffee-tracker

# Test container internally
docker-compose exec coffee-tracker curl localhost:8000/health
```

### Permission errors
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data
chmod 755 ./data
```

## Development

### Adding new endpoints
1. Add route to appropriate router file
2. Update models if needed
3. Restart container: `docker-compose restart`

### Database changes
1. Modify `models.py`
2. Rebuild container: `docker-compose up --build`
3. Database tables auto-update on startup

### Dependencies
Add to `requirements.txt` and rebuild:
```bash
echo "new-package==1.0.0" >> requirements.txt
docker-compose up --build
```

## API Response Examples

### Coffee today response
```json
{
  "date": "2025-07-23",
  "total_caffeine_mg": 285,
  "addiction_level": "moderate"
}
```

### Heart rate correlation response
```json
{
  "correlations": [
    {
      "coffee_time": "2025-07-23T14:30:00",
      "caffeine_mg": 95,
      "avg_heartrate_after": 88,
      "readings_count": 3
    }
  ],
  "summary": "Your heart probably hates you"
}
```

## License

Do whatever you want with this. It's just tracking your slow descent into caffeine dependency.

## Contributing

1. Make it work better
2. Add more ways to shame users about their habits
3. Don't break existing functionality
4. Keep the sarcasm

---

**Note**: This API will accurately track your caffeine consumption and heart rate. It will not judge you (much), but the data probably will.