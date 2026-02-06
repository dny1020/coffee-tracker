# Coffee Tracker API ☕

Track your caffeine consumption with decay estimation.

## Quick Start

```bash
cp .env.example .env  # Edit API_KEY
docker-compose up -d
curl http://localhost:4000/api/v1/health
```

## API

- **Docs**: http://localhost:4000/api/v1/docs
- **Auth**: Bearer token required

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:4000/api/v1/coffee/stats
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/coffee/` | Log coffee |
| GET | `/api/v1/coffee/` | List logs |
| GET | `/api/v1/coffee/stats` | Statistics |
| GET | `/api/v1/coffee/active` | Active caffeine (decay) |
| GET | `/api/v1/coffee/summary` | Daily summary |
| DELETE | `/api/v1/coffee/{id}` | Delete log |

## Configuration

```env
DATABASE_URL=sqlite:///data/coffee.db
API_KEY=your-secret-key
```

## Development

```bash
# Local
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 4000

# Tests
pytest tests/ -v
```

## License

Apache 2.0