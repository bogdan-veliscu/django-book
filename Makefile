ifneq (,$(wildcard ./.env))
	include .env
	export
endif

IMAGE_NAME = $(shell basename "`pwd`")
IMAGE_TAG = $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)
REGISTRY = $(shell echo $(REGISTRY_HOST))
IMAGE = $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: help

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ \
	{ printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ \
	{ printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

## [ENV SETUP]
install:init-env ## builds and start the dev container
	docker compose build --pull --no-cache
	docker compose up -d

run: ## Run the application
	docker compose up -d --build

dev:
	docker compose up --build

prod:
	docker compose -f docker-compose.prod.yml up --build -d

prod-local: ## Run production setup locally for testing
	@if [ ! -f .env.prod ]; then \
		cp example.env .env.prod; \
		echo "Created .env.prod file. Please update it with your production settings."; \
		exit 1; \
	fi
	docker compose -f docker-compose.prod.yml up --build -d
	@echo "Production environment is running locally"
	@echo "Access the application at http://localhost"
	@echo "Run 'make logs' to view logs"

logs: ## View logs from all containers
	docker compose -f docker-compose.prod.yml logs -f

prod-down: ## Stop production environment
	docker compose -f docker-compose.prod.yml down -v

build: ## Build the Docker image
	docker buildx build --platform linux/amd64 -t $(IMAGE) --load .

init-env:
	@test -f .env || (cp example.env .env && echo .env file initialized)

## [DATABASE]
superuser: ## creates a superuser for the API
	docker compose run --rm app ./manage.py createsuperuser

migrations: ## generate migrations in a clean container
	docker compose run --rm app ./manage.py makemigrations

migrate: ## apply migrations in a clean container
	docker compose run --rm app ./manage.py migrate

collectstatic: ## collect static files
	docker compose run --rm app ./manage.py collectstatic --noinput

## [UTILS]
install_local: ## Install the package locally
	uv pip install -e .[dev]

test_local: ## Run the tests locally
	python -m pytest

shell:  ## start a django shell
	docker compose run --rm app ./manage.py shell

lint:  ## run linter
	docker compose run --rm app ruff .
isort:  ## run isort
	docker compose run --rm app isort .
black:  ## run black
	docker compose run --rm app black .

## [TEST]
test:  ## run all tests
	docker compose run --rm app pytest

test-lf:  ## rerun tests that failed last time
	docker compose run --rm app pytest --lf --pdb

## [CLEAN]
clean: clean/docker clean/py ## remove all build, test, coverage and Python artifacts

clean/docker: ## stop docker containers and remove orphaned images and volumes
	docker compose down -t 60
	docker system prune -f

clean/py: ## remove Python test, coverage, file artifacts, and compiled message files
	find . -name '.coverage' -delete
	find . -name '.pytest_cache' -delete
	find . -name '__pycache__' -delete
	find . -name 'htmlcov' -delete
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*.mo' -delete

start:
	uvicorn conduit.config.asgi:application --host 0.0.0.0 --port 8000
