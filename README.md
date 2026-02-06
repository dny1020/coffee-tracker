# Coffee Tracker API

Track caffeine consumption.

## Setup

```bash
cp .env.example .env  # Edit API_KEY
docker-compose up -d
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/coffee/` | Log coffee |
| GET | `/api/v1/coffee/` | List all |
| GET | `/api/v1/coffee/today` | Today's summary |
| GET | `/api/v1/coffee/stats` | Statistics |
| DELETE | `/api/v1/coffee/{id}` | Delete |
| GET | `/api/v1/health` | Health check |

## Auth

All `/coffee` endpoints require Bearer token:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:4000/api/v1/coffee/today
```

## Docs

http://localhost:4000/api/v1/docs