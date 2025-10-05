#!/bin/bash
# Coffee Tracker - Production Deployment Script
# Run this on your production server after git pull

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "☕ Coffee Tracker - Production Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env with required variables"
    echo "See .env.example for reference"
    exit 1
fi

# 2. Check if Traefik network exists
if ! docker network inspect traefik_net >/dev/null 2>&1; then
    echo "📡 Creating Traefik network..."
    docker network create traefik_net
else
    echo "✅ Traefik network exists"
fi

# 3. Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down

# 4. Pull latest images
echo ""
echo "📥 Pulling latest images..."
docker-compose pull

# 5. Start all services
echo ""
echo "🚀 Starting all services..."
docker-compose up -d

# 6. Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# 7. Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

# 8. Test health endpoints
echo ""
echo "🏥 Health Checks:"

# API Health
if curl -f -s https://coffee.danilocloud.me/health >/dev/null 2>&1; then
    echo "✅ Coffee Tracker API: Healthy"
else
    echo "❌ Coffee Tracker API: Not responding"
fi

# Prometheus Health
if curl -f -s https://prometheus.danilocloud.me/-/healthy >/dev/null 2>&1; then
    echo "✅ Prometheus: Healthy"
else
    echo "❌ Prometheus: Not responding"
fi

# Grafana Health
if curl -f -s https://grafana.danilocloud.me/api/health >/dev/null 2>&1; then
    echo "✅ Grafana: Healthy"
else
    echo "❌ Grafana: Not responding"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access URLs:"
echo "  • API:        https://coffee.danilocloud.me"
echo "  • Docs:       https://coffee.danilocloud.me/docs"
echo "  • Prometheus: https://prometheus.danilocloud.me"
echo "  • Grafana:    https://grafana.danilocloud.me"
echo ""
echo "📋 Next Steps:"
echo "  1. Check Prometheus targets: https://prometheus.danilocloud.me/targets"
echo "  2. Login to Grafana and change default password"
echo "  3. Test API with: curl https://coffee.danilocloud.me/health"
echo "  4. Create Apple Shortcuts (see SHORTCUTS.md)"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo ""
