# Coffee Tracker API

Track caffeine consumption.

## Deploy to VPS

```bash
# En tu máquina local
scp -r . user@vps:~/coffee-tracker

# En el VPS
cd ~/coffee-tracker
cp .env.example .env
nano .env  # Cambiar API_KEY
mkdir -p data
docker compose up -d --build
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

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:4000/api/v1/coffee/today
```

## Docs

http://localhost:4000/api/v1/docs