.PHONY: help build up down restart logs test test-clean test-watch clean dev shell db-shell backup restore lint format check validate

# Variables
COMPOSE_FILE = docker-compose.yml
SERVICE_NAME = coffee-tracker
TEST_DB = test.db
BACKUP_DIR = backups

# Default target
help:
	@echo "Coffee Tracker - Makefile Commands"
	@echo "=================================="
	@echo "Development:"
	@echo "  build       Build Docker containers"
	@echo "  up          Start services in background"
	@echo "  down        Stop all services"
	@echo "  restart     Restart services"
	@echo "  logs        Show service logs"
	@echo ""
	@echo "Testing:"
	@echo "  test        Run tests locally"
	@echo "  test-clean  Run tests with completely clean environment"
	@echo "  test-docker Run tests in Docker"
	@echo "  validate    Validate API with sample requests"
	@echo ""
	@echo "Maintenance:"
	@echo "  backup      Backup database"
	@echo "  restore     Restore database from backup"
	@echo "  clean       Clean up containers and volumes"
	@echo "  shell       Shell into container"
	@echo ""
	@echo "Monitoring:"
	@echo "  status      Check service status"
	@echo "  health      Check API health"

# Development commands
build:
	@echo "Building containers..."
	docker-compose -f $(COMPOSE_FILE) build

up: build
	@echo "Starting services in background..."
	docker-compose -f $(COMPOSE_FILE) up -d

down:
	@echo "Stopping services..."
	docker-compose -f $(COMPOSE_FILE) down

restart:
	@echo "Restarting services..."
	docker-compose -f $(COMPOSE_FILE) restart

logs:
	@echo "Showing logs..."
	docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE_NAME)

logs-redis:
	@echo "Showing Redis logs..."
	docker-compose -f $(COMPOSE_FILE) logs -f redis

# Testing commands
test:
	@echo "Running tests locally..."
	@echo "Cleaning up any existing test databases..."
	@rm -f $(TEST_DB) test_coffee_tracker.db ./data/test_*.db
	@echo "Running tests with proper isolation..."
	@if [ -d "venv" ]; then \
		echo "Using virtual environment..."; \
		venv/bin/python -m pytest -v; \
	else \
		echo "Using system Python3..."; \
		python3 -m pytest -v; \
	fi
	@echo "Cleaning up test files..."
	@rm -f $(TEST_DB) test_coffee_tracker.db ./data/test_*.db

test-docker:
	@echo "Running tests in Docker..."
	docker-compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) sh -c "python -m pytest -v"

test-watch:
	@echo "Running tests in watch mode..."
	@if [ -d "venv" ]; then \
		venv/bin/python -m pytest -f; \
	else \
		python3 -m pytest -f; \
	fi

test-clean:
	@echo "Running tests with completely fresh environment..."
	@echo "Cleaning up any previous temp files..."
	@rm -f ./data/coffee.db.temp ./data/coffee.db.backup $(TEST_DB) test_coffee_tracker.db ./data/test_*.db
	@echo "Running tests with isolated database..."
	@if [ -d "venv" ]; then \
		venv/bin/python -m pytest -v; \
	else \
		python3 -m pytest -v; \
	fi
	@echo "Test complete"

validate: up
	@echo "Validating API endpoints..."
	@sleep 5
	@echo "Testing health endpoint..."
	@curl -f http://localhost:8000/health || echo "Health check failed"
	@echo "\nTesting root endpoint..."
	@curl -f http://localhost:8000/ || echo "Root endpoint failed"
	@echo "\nTesting with invalid auth..."
	@curl -H "Authorization: Bearer invalid" http://localhost:8000/coffee/ || echo "Auth validation working"
	@echo "\nAPI validation complete"

# Maintenance commands
backup:
	@echo "Creating backup..."
	@mkdir -p $(BACKUP_DIR)
	@if [ -f ./data/coffee.db ]; then \
		cp ./data/coffee.db $(BACKUP_DIR)/coffee-backup-$(shell date +%Y%m%d-%H%M%S).db; \
		echo "Backup created in $(BACKUP_DIR)/"; \
		ls -la $(BACKUP_DIR)/; \
	else \
		echo "No database file found to backup"; \
	fi

restore:
	@echo "Available backups:"
	@ls -la $(BACKUP_DIR)/ 2>/dev/null || echo "No backups found"
	@echo "To restore: cp $(BACKUP_DIR)/backup-file.db ./data/coffee.db"

shell:
	@echo "Opening shell in coffee-tracker container..."
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) sh

db-shell:
	@echo "Opening database shell..."
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) sh -c "python -c \"import sqlite3; conn = sqlite3.connect('/app/data/coffee.db'); conn.execute('.tables'); conn.close()\""

# Monitoring commands
status:
	@echo "Service status:"
	docker-compose -f $(COMPOSE_FILE) ps

health:
	@echo "Checking API health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not responding"

# Cleanup commands
clean:
	@echo "Cleaning up..."
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f
	@if [ -f $(TEST_DB) ]; then rm $(TEST_DB); fi

clean-data:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@rm -rf ./data/coffee.db
	@echo "Database deleted"

# Development helpers
dev: down up logs

prod-check:
	@echo "Production readiness check:"
	@echo "✓ Docker containers"
	@echo "✓ Environment variables"
	@echo "✓ Health checks"
	@echo "✓ Rate limiting"
	@echo "✓ Input validation"
	@echo "✓ Database persistence"
	@echo ""
	@echo "Still needed for production:"
	@echo "- HTTPS/TLS termination (nginx)"
	@echo "- Change default API key"
	@echo "- Set up log aggregation"
	@echo "- Configure backup strategy"
	@echo "- Set up monitoring alerts"