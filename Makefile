ifneq (,$(wildcard ./.env))
	include .env
	export
endif

.PHONY: help

help: ## Show this help message
	@echo "Conduit - FastAPI + Lit"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start development environment"
	@echo "  make dev-down         Stop development environment"
	@echo "  make dev-logs         View development logs"
	@echo "  make shell            Access backend shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests"
	@echo "  make test-cov         Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linter (ruff)"
	@echo "  make format           Format code"
	@echo "  make type-check       Run type checker"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          Apply database migrations"
	@echo "  make migration MSG=   Create new migration"
	@echo "  make db-shell         Access database shell"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-dev     Start frontend dev server"
	@echo "  make frontend-build   Build frontend"
	@echo "  make frontend-lint    Lint frontend"
	@echo ""
	@echo "Production:"
	@echo "  make deploy           Full production deployment"
	@echo "  make prod-up          Start production"
	@echo "  make prod-down        Stop production"
	@echo "  make backup           Backup database"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove temp files"
	@echo "  make clean-all        Remove containers and volumes"

## Development
dev: ## Start development environment
	docker-compose up -d
	@echo "✓ Development environment started"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

dev-down: ## Stop development environment
	docker-compose down

dev-logs: ## View development logs
	docker-compose logs -f --tail=100

shell: ## Access backend shell
	docker-compose exec backend /bin/bash

## Testing
test: ## Run all tests
	uv run pytest tests/ -v

test-unit: ## Run unit tests
	uv run pytest tests/unit -v

test-integration: ## Run integration tests
	docker-compose up -d db redis
	uv run pytest tests/integration -v
	docker-compose stop db redis

test-cov: ## Run tests with coverage
	uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "✓ Coverage report: htmlcov/index.html"

## Code Quality
lint: ## Run linter
	uv run ruff check .

format: ## Format code
	uv run ruff check --fix .
	uv run ruff format .

type-check: ## Run type checker
	uv run mypy src --ignore-missing-imports

## Database
migrate: ## Apply migrations
	docker-compose exec backend alembic upgrade head

migration: ## Create new migration (usage: make migration MSG="description")
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide MSG=..."; \
		echo "Example: make migration MSG='add user field'"; \
		exit 1; \
	fi
	docker-compose exec backend alembic revision --autogenerate -m "$(MSG)"

db-shell: ## Access database shell
	docker-compose exec db psql -U postgres conduit

## Frontend
frontend-dev: ## Start frontend dev server
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	cd frontend && npm run build

frontend-lint: ## Lint frontend code
	cd frontend && npm run lint

frontend-type-check: ## Type check frontend
	cd frontend && npx tsc --noEmit

## Production
deploy: ## Full production deployment
	./deploy.sh deploy

prod-up: ## Start production
	./deploy.sh start

prod-down: ## Stop production
	./deploy.sh stop

prod-logs: ## View production logs
	./deploy.sh logs

prod-status: ## Check production status
	./deploy.sh status

backup: ## Backup production database
	./deploy.sh backup

## Cleanup
clean: ## Remove temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov .coverage 2>/dev/null || true
	@echo "✓ Temporary files cleaned"

clean-all: clean ## Remove all containers and volumes
	docker-compose down -v
	@echo "✓ All containers and volumes removed"
