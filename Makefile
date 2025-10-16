.PHONY: help up down logs restart build test test-docker test-watch validate health status backup clean dev prod-check install-dev format lint init-alembic migrate upgrade-db downgrade-db prod-up prod-down prod-logs prod-pull prod-update prod-rollback prod-status prod-backup prod-shell prod-restart clean-prod

help: ## Show this help message
@echo 'Usage: make [target]'
@echo ''
@echo 'Available targets:'
@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# DEVELOPMENT COMMANDS
# =============================================================================

up: ## Start all services (development)
docker-compose up -d

down: ## Stop all services (development)
docker-compose down

logs: ## Show logs from all services (development)
docker-compose logs -f

restart: ## Restart all services (development)
docker-compose restart

build: ## Build the containers (development)
docker-compose build

dev: ## Start services in development mode
@echo "Starting development environment..."
$(MAKE) build
$(MAKE) up
@echo "Waiting for services to be ready..."
@sleep 5
$(MAKE) logs

# =============================================================================
# PRODUCTION COMMANDS (using docker-compose.prod.yml)
# =============================================================================

prod-up: ## Start services in production mode (use pre-built images)
@echo "🚀 Starting production environment..."
@if [ ! -f .env.production ]; then \
echo "❌ Error: .env.production not found!"; \
echo "Copy .env.production.example and configure:"; \
echo "  cp .env.production.example .env.production"; \
exit 1; \
fi
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
@echo "✅ Production services started"
@echo "Checking health..."
@sleep 5
@$(MAKE) prod-status

prod-down: ## Stop production services
docker-compose -f docker-compose.prod.yml down

prod-logs: ## Show logs from production services
docker-compose -f docker-compose.prod.yml logs -f

prod-pull: ## Pull latest production images from GHCR
@echo "📥 Pulling latest images from GitHub Container Registry..."
docker-compose -f docker-compose.prod.yml pull
@echo "✅ Images pulled successfully"

prod-update: ## Update production to latest image and restart
@echo "🔄 Updating production deployment..."
$(MAKE) prod-pull
docker-compose -f docker-compose.prod.yml up -d
@echo "✅ Production updated successfully"
@sleep 3
@$(MAKE) prod-status

prod-rollback: ## Rollback to previous image version
@echo "⏮️  Rolling back to previous version..."
@read -p "Enter image tag to rollback to (e.g., main-abc1234): " tag; \
export IMAGE_TAG=$$tag; \
docker-compose -f docker-compose.prod.yml pull; \
docker-compose -f docker-compose.prod.yml up -d
@echo "✅ Rollback complete"

prod-status: ## Check production service status
@echo "📊 Production Service Status:"
@echo ""
docker-compose -f docker-compose.prod.yml ps
@echo ""
@echo "🏥 Health Check:"
@curl -s http://localhost:8000/api/v1/health 2>/dev/null | jq . || echo "❌ Health check failed"

prod-backup: ## Backup production database
@echo "💾 Creating production backup..."
@mkdir -p backups/production
@timestamp=$$(date +%Y%m%d_%H%M%S); \
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U coffee coffee_db > ./backups/production/postgres_$${timestamp}.sql && \
echo "✅ Production backup created: backups/production/postgres_$${timestamp}.sql" || \
echo "❌ Production backup failed"

prod-shell: ## Access production container shell
docker-compose -f docker-compose.prod.yml exec coffee-tracker sh

prod-restart: ## Restart production services
docker-compose -f docker-compose.prod.yml restart

# =============================================================================
# TESTING COMMANDS
# =============================================================================

test: ## Run tests locally (requires Python environment)
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-docker: ## Run tests in Docker container
docker-compose exec coffee-tracker pytest tests/ -v --cov=app --cov-report=term

test-watch: ## Run tests in watch mode
pytest-watch tests/

# =============================================================================
# VALIDATION & HEALTH COMMANDS
# =============================================================================

validate: ## Validate all API endpoints
@echo "Testing health endpoint..."
@curl -s http://localhost:8000/api/v1/health | jq .
@echo "\nTesting root endpoint..."
@curl -s http://localhost:8000/api/v1/ | jq .
@echo "\nTesting API info..."
@curl -s http://localhost:8000/api/v1/info | jq .

health: ## Check service health
@curl -s http://localhost:8000/api/v1/health

status: ## Show container status
docker-compose ps

# =============================================================================
# BACKUP & RESTORE COMMANDS
# =============================================================================

backup: ## Backup the database (development)
@mkdir -p backups
@timestamp=$$(date +%Y%m%d_%H%M%S); \
if [ -f ./data/coffee.db ]; then \
cp ./data/coffee.db ./backups/coffee_$${timestamp}.db; \
echo "SQLite backup created: backups/coffee_$${timestamp}.db"; \
fi; \
docker-compose exec -T postgres pg_dump -U coffee coffee_db > ./backups/postgres_$${timestamp}.sql 2>/dev/null && \
echo "Postgres backup created: backups/postgres_$${timestamp}.sql" || \
echo "Postgres backup skipped (container not running or database not accessible)"

# =============================================================================
# CLEANUP COMMANDS
# =============================================================================

clean: ## Clean up containers and volumes
docker-compose down -v
rm -rf __pycache__ .pytest_cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

clean-prod: ## Clean up production containers and volumes
docker-compose -f docker-compose.prod.yml down -v

# =============================================================================
# PRODUCTION READINESS CHECK
# =============================================================================

prod-check: ## Check production readiness
@echo "🔍 Checking production readiness..."
@echo ""
@echo "1. Checking if .env.production exists..."
@test -f .env.production && echo "✅ .env.production found" || echo "❌ .env.production not found (copy from .env.production.example)"
@echo ""
@echo "2. Checking if API_KEY is set..."
@grep -q "API_KEY" .env.production 2>/dev/null && echo "✅ API_KEY found" || echo "❌ API_KEY not found"
@echo ""
@echo "3. Checking if default key is changed..."
@grep -q "CHANGE_THIS" .env.production 2>/dev/null && echo "⚠️  WARNING: Default values detected - change in production!" || echo "✅ Configuration customized"
@echo ""
@echo "4. Checking if DOCKER_IMAGE is set..."
@grep -q "DOCKER_IMAGE" .env.production 2>/dev/null && echo "✅ DOCKER_IMAGE configured" || echo "⚠️  DOCKER_IMAGE not found (will use default)"
@echo ""
@echo "5. Checking Docker login to GHCR..."
@docker pull ghcr.io/dny1020/coffee-tracker:latest > /dev/null 2>&1 && echo "✅ Can pull from GHCR" || echo "⚠️  Cannot pull from GHCR (check authentication or image availability)"
@echo ""
@echo "6. Checking network..."
@docker network inspect traefik_net > /dev/null 2>&1 && echo "✅ traefik_net network exists" || echo "⚠️  traefik_net network not found (create with: docker network create traefik_net)"
@echo ""

# =============================================================================
# DEVELOPMENT SETUP COMMANDS
# =============================================================================

install-dev: ## Install development dependencies
pip install -r requirements.txt
pip install pytest-watch black ruff alembic

format: ## Format code with black
black app/ tests/

lint: ## Lint code with ruff
ruff check app/ tests/

# =============================================================================
# DATABASE MIGRATION COMMANDS
# =============================================================================

init-alembic: ## Initialize Alembic for database migrations
alembic init migrations
@echo "⚠️  Remember to configure alembic.ini with your database URL"

migrate: ## Create a new migration
@read -p "Enter migration message: " msg; \
alembic revision --autogenerate -m "$$msg"

upgrade-db: ## Apply database migrations
alembic upgrade head

downgrade-db: ## Rollback last database migration
alembic downgrade -1
