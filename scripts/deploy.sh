#!/bin/bash

# Coffee Tracker Deployment Script
# Usage: ./scripts/deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    error "Invalid environment. Use 'staging' or 'production'"
fi

log "Deploying Coffee Tracker to $ENVIRONMENT environment..."

# Check if required tools are installed
command -v docker >/dev/null 2>&1 || error "docker is required but not installed"
command -v docker-compose >/dev/null 2>&1 || error "docker-compose is required but not installed"

# Set environment-specific variables
if [[ "$ENVIRONMENT" == "production" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env.prod"
    BACKUP_DIR="backups/prod"
else
    COMPOSE_FILE="docker-compose.staging.yml"
    ENV_FILE=".env.staging"
    BACKUP_DIR="backups/staging"
fi

# Check if environment file exists
if [[ ! -f "$ENV_FILE" ]]; then
    warn "Environment file $ENV_FILE not found. Using .env as fallback"
    ENV_FILE=".env"
fi

# Create necessary directories
log "Creating necessary directories..."
mkdir -p data
mkdir -p "$BACKUP_DIR"
mkdir -p nginx/logs

# Backup existing database if it exists
if [[ -f "data/coffee.db" ]]; then
    log "Backing up existing database..."
    cp "data/coffee.db" "$BACKUP_DIR/coffee-backup-$(date +%Y%m%d-%H%M%S).db"
fi

# Pull latest images
log "Pulling latest Docker images..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull

# Stop existing containers
log "Stopping existing containers..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down

# Start services
log "Starting services..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# Wait for services to be healthy
log "Waiting for services to be healthy..."
sleep 10

# Health check
log "Performing health check..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null; then
        log "✅ Health check passed!"
        break
    fi
    
    if [[ $i -eq 30 ]]; then
        error "❌ Health check failed after 30 attempts"
    fi
    
    echo -n "."
    sleep 2
done

# Show deployment status
log "Deployment completed successfully!"
echo ""
log "Service Status:"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

echo ""
log "Service URLs:"
echo "  API: http://localhost:8000"
echo "  Health: http://localhost:8000/health"
echo "  Docs: http://localhost:8000/docs"

echo ""
log "Useful commands:"
echo "  View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "  Restart: docker-compose -f $COMPOSE_FILE restart"
echo "  Stop: docker-compose -f $COMPOSE_FILE down"

# Optional: Run smoke tests
if [[ -f "scripts/smoke-tests.sh" ]]; then
    log "Running smoke tests..."
    ./scripts/smoke-tests.sh
fi

log "🎉 Coffee Tracker deployed successfully to $ENVIRONMENT!"