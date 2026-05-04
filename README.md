# Coffee Tracker API

Track caffeine consumption ☕️.

## Deploy (Podman)

This service is **Node.js + TypeScript + Fastify + Prisma** and can run as a container.

On the target host (e.g. Raspberry Pi):

```bash
# copy files (or use ./deploy.sh)
scp -r . user@host:/opt/coffee
cd /opt/coffee

# configure
cp .env.example .env
nano .env  # set API_KEY (+ optionally PORT)
mkdir -p data logs

# build + run
podman compose -f podman-compose.yml up -d --build

# status / logs
podman compose -f podman-compose.yml ps
podman compose -f podman-compose.yml logs -n 50
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
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/v1/coffee/today
```

## Docs

http://localhost:8000/api/v1/docs
