.PHONY: build up down restart logs test clean shell

# Variables
COMPOSE_FILE = docker-compose.yml
SERVICE_NAME = coffee-tracker

# Docker
build:
	@echo "🛠️  Building containers..."
	docker-compose -f $(COMPOSE_FILE) build

up: build
	@echo "🚀 Starting services..."
	docker-compose -f $(COMPOSE_FILE) up -d

down:
	@echo "🧨 Stopping services..."
	docker-compose -f $(COMPOSE_FILE) down

restart:
	@echo "🔁 Restarting services..."
	docker-compose -f $(COMPOSE_FILE) restart

logs:
	@echo "📜 Logs:"
	docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE_NAME)

# Testing
test:
	@echo "✅ Running minimal API smoke test..."
	SKIP_DB_INIT=1 python3 -m pytest tests/test_smoke.py -v

# Shell
shell:
	@echo "🧑‍💻 Shell into container..."
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) sh

# Clean
clean:
	@echo "🧹 Cleaning containers and volumes..."
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f
