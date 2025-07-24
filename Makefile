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
	@if [ -d "venv" ]; then \
		echo "Using virtual environment..."; \
		venv/bin/python -m pytest -v; \
	else \
		echo "Using system Python3..."; \
		python3 -m pytest -v; \
	fi
	@if [ -f $(TEST_DB) ]; then rm $(TEST_DB); fi

test-docker:
	@echo "Running tests in Docker..."
	docker-compose -f $(COMPOSE_FILE) run --rm -e DATABASE_URL=sqlite:///test_coffee_tracker.db $(SERVICE_NAME) sh -c "rm -f test_coffee_tracker.db && python -m pytest -v"

test-docker-build:
	@echo "Running tests in fresh container..."
	docker-compose -f $(COMPOSE_FILE) run --rm -e DATABASE_URL=sqlite:///test_coffee_tracker.db $(SERVICE_NAME) sh -c "rm -f test_coffee_tracker.db && python -m pytest -v"

clean:
	@echo "Cleaning up..."
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f