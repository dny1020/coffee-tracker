# Coffee Tracker API

Track caffeine consumption ☕️.

## Deploy (systemd)

This service is now **Node.js + TypeScript + Fastify + Prisma**.

On the target host (e.g. Raspberry Pi):

```bash
# copy files (or use ./deploy.sh)
scp -r . user@host:/opt/coffee
cd /opt/coffee

# configure
cp .env.example .env
nano .env  # set API_KEY + DATABASE_URL
mkdir -p data logs

# install + build + migrate
npm ci
npm run build
npm run migrate:deploy

# systemd
sudo cp coffee.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable coffee
sudo systemctl restart coffee
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
