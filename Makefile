.PHONY: help build up down restart logs test test-watch clean dev shell db-shell backup restore lint format check

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

logs:
	@echo "Showing logs..."
	docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE_NAME)

test:
	@echo "Running tests..."
	@if [ -f $(TEST_DB) ]; then rm $(TEST_DB); fi
	python -m pytest -v
	@if [ -f $(TEST_DB) ]; then rm $(TEST_DB); fi

test-docker:
	@echo "Running tests in Docker..."
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python -m pytest -v

test-docker-build:
	@echo "Running tests in fresh container..."
	docker-compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) python -m pytest -v

clean:
	@echo "Cleaning up..."
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f