
# help: ## display a help message detailing commands and their purpose
# 	@echo "Commands:"
# 	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
# 	@echo ""

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



init-env:
	@test -f .env || (cp example.env .env && echo .env file initialized)

## [DATABASE]
superuser: ## creates a superuser for the API
	docker compose run --rm app ./manage.py createsuperuser

migrations: ## generate migrations in a clean container
	docker compose run --rm app ./manage.py makemigrations

migrate: ## apply migrations in a clean container
	docker compose run --rm app ./manage.py migrate

## [UTILS]

shell:  ## start a django shell
	docker compose run --rm app ./manage.py shell

lint:  ## run linter
	docker compose run --rm app flake8
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


