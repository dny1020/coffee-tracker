# Coffee Tracker API

Track caffeine consumption ☕️.

## Deploy (Docker Compose)

This service is **Node.js + Fastify + Prisma** and runs as a container.

On the target host (e.g. Raspberry Pi):

```bash
# copy files (or use ./deploy.sh)
scp -r . user@host:~/coffee
cd ~/coffee

# configure
cp .env.example .env
nano .env  # set API_KEY (+ optionally PORT)
mkdir -p data logs

# build + run
docker compose up -d --build

# status / logs
docker compose ps
docker compose logs -n 50
```

By default this maps **host port 8001 → container port 8000** to avoid conflicts.

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
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/v1/coffee/today
```

## Docs

http://localhost:8000/api/v1/docs
