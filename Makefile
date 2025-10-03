.PHONY: help up down logs restart build test test-docker test-watch validate health status backup clean dev prod-check

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

restart: ## Restart all services
	docker-compose restart

build: ## Build the containers
	docker-compose build

test: ## Run tests locally (requires Python environment)
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-docker: ## Run tests in Docker container
	docker-compose exec coffee-tracker pytest tests/ -v --cov=app --cov-report=term

test-watch: ## Run tests in watch mode
	pytest-watch tests/

validate: ## Validate all API endpoints
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/health | jq .
	@echo "\nTesting root endpoint..."
	@curl -s http://localhost:8000/ | jq .
	@echo "\nTesting API info..."
	@curl -s http://localhost:8000/info | jq .

health: ## Check service health
	@curl -s http://localhost:8000/health

status: ## Show container status
	docker-compose ps

backup: ## Backup the database
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	if [ -f ./data/coffee.db ]; then \
		cp ./data/coffee.db ./backups/coffee_$${timestamp}.db; \
		echo "SQLite backup created: backups/coffee_$${timestamp}.db"; \
	fi; \
	docker-compose exec -T postgres pg_dump -U coffee coffee_db > ./backups/postgres_$${timestamp}.sql 2>/dev/null && \
		echo "Postgres backup created: backups/postgres_$${timestamp}.sql" || \
		echo "Postgres backup skipped (container not running or database not accessible)"

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

dev: ## Start services in development mode
	@echo "Starting development environment..."
	$(MAKE) build
	$(MAKE) up
	@echo "Waiting for services to be ready..."
	@sleep 5
	$(MAKE) logs

prod-check: ## Check production readiness
	@echo "🔍 Checking production readiness..."
	@echo ""
	@echo "1. Checking if API_KEY is set..."
	@grep -q "API_KEY" .env && echo "✅ API_KEY found in .env" || echo "❌ API_KEY not found in .env"
	@echo ""
	@echo "2. Checking if default key is changed..."
	@grep -q "coffee-addict-secret-key-2025" .env && echo "⚠️  WARNING: Default API_KEY detected - change in production!" || echo "✅ Custom API_KEY configured"
	@echo ""
	@echo "3. Checking CORS configuration..."
	@grep -q "CORS_ORIGINS" .env && echo "✅ CORS_ORIGINS configured" || echo "⚠️  CORS_ORIGINS not found"
	@echo ""
	@echo "4. Checking database configuration..."
	@grep -q "DATABASE_URL" .env && echo "✅ DATABASE_URL configured" || echo "❌ DATABASE_URL not found"
	@echo ""
	@echo "5. Checking Redis configuration..."
	@grep -q "REDIS_URL" .env && echo "✅ REDIS_URL configured" || echo "⚠️  REDIS_URL not found"
	@echo ""
	@echo "6. Checking container status..."
	@docker-compose ps

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest-watch black ruff alembic

format: ## Format code with black
	black app/ tests/

lint: ## Lint code with ruff
	ruff check app/ tests/

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
