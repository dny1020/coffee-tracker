.PHONY: help up down logs restart build test test-docker validate health status backup clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Commands

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

restart: ## Restart services
	docker-compose restart

build: ## Build containers
	docker-compose build

# Testing Commands

test: ## Run tests locally
	pytest tests/ -v

test-docker: ## Run tests in Docker
	docker-compose exec coffee-tracker pytest tests/ -v

# Validation Commands

validate: ## Validate API endpoints
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/api/v1/health | jq . || curl -s http://localhost:8000/api/v1/health
	@echo "\nTesting root endpoint..."
	@curl -s http://localhost:8000/api/v1/ | jq . || curl -s http://localhost:8000/api/v1/

health: ## Check service health
	@curl -s http://localhost:8000/api/v1/health

status: ## Show container status
	docker-compose ps

# Backup Commands

backup: ## Backup database
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker-compose exec -T postgres pg_dump -U coffee coffee_db > ./backups/postgres_$${timestamp}.sql 2>/dev/null && \
	echo "Backup created: backups/postgres_$${timestamp}.sql" || echo "Backup failed"

# Cleanup Commands

clean: ## Clean up containers
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
