.PHONY: all init format_backend format lint build run_cli dev help tests coverage clean_python_cache clean_npm_cache clean_all setup_uv add unit_tests unit_tests_looponfail integration_tests integration_tests_no_api_keys integration_tests_api_keys template_tests codespell fix_codespell unsafe_fix run_cli_debug setup_devcontainer setup_env backend build_and_run build_and_install build_aiexec_base build_aiexec_backup build_aiexec docker_build docker_build_backend docker_build_frontend dockerfile_build dockerfile_build_be dockerfile_build_fe clear_dockerimage docker_compose_up docker_compose_down dcdev_up lock_base lock_aiexec lock update publish_base publish_aiexec publish_base_testpypi publish_aiexec_testpypi publish publish_testpypi alembic-revision alembic-upgrade alembic-downgrade alembic-current alembic-history alembic-check alembic-stamp patch locust

# Configurations
VERSION := $(shell grep "^version" pyproject.toml | sed 's/.*"\(.*\)"$$/\1/')
DOCKERFILE := docker/build_and_push.Dockerfile
DOCKERFILE_BACKEND := docker/build_and_push_backend.Dockerfile
DOCKERFILE_FRONTEND := docker/frontend/build_and_push_frontend.Dockerfile
DOCKER_COMPOSE := docker/example/docker-compose.yml

# Colors
RED := \033[0;31m
GREEN := \033[0;32m
NC := \033[0m # No Color

# Default variables
log_level ?= debug
host ?= 0.0.0.0
port ?= 7860
env ?= .env
open_browser ?= true
path = api/base/aiexec/frontend
workers ?= 1
async ?= true
lf ?= false
ff ?= true

all: help

######################
# UTILITIES
######################

# Some directories may be mount points as in devcontainer, so we need to clear their
# contents rather than remove the entire directory. But we must also be mindful that
# we are not running in a devcontainer, so need to ensure the directories exist.
# See https://code.visualstudio.com/remote/advancedcontainers/improve-performance
CLEAR_DIRS = $(foreach dir,$1,$(shell mkdir -p $(dir) && find $(dir) -mindepth 1 -delete))

# check for required tools
check_tools:
	@command -v uv >/dev/null 2>&1 || { echo >&2 "$(RED)uv is not installed. Aborting.$(NC)"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo >&2 "$(RED)NPM is not installed. Aborting.$(NC)"; exit 1; }
	@echo "$(GREEN)All required tools are installed.$(NC)"

help: ## show this help message
	@echo '----'
	@grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | \
	awk -F ':.*##' '{printf "\033[36mmake %-25s\033[0m %s\n", $$1, $$2}' | \
	column -c2 -t -s :
	@echo '----'
	@echo 'For frontend commands, run: make help_frontend'

######################
# INSTALL PROJECT
######################

reinstall_backend: check_tools ## forces reinstall all dependencies (no caching)
	@echo 'Installing backend dependencies'
	@uv sync -n --reinstall --frozen

install_backend: check_tools ## install the backend dependencies
	@echo 'Installing backend dependencies'
	@uv sync --frozen --extra "postgresql" $(EXTRA_ARGS)

init: check_tools ## initialize the project
	@make install_backend
	@make install_frontend
	@uvx pre-commit install
	@echo "$(GREEN)All requirements are installed.$(NC)"

######################
# CLEAN PROJECT
######################

clean_python_cache: ## clean python cache
	@echo "Cleaning Python cache..."
	@find . -type d -name '__pycache__' -exec rm -r {} + 
	@find . -type f -name '*.py[cod]' -exec rm -f {} + 
	@find . -type f -name '*~' -exec rm -f {} + 
	@find . -type f -name '.*~' -exec rm -f {} + 
	@$(call CLEAR_DIRS,.mypy_cache )
	@echo "$(GREEN)Python cache cleaned.$(NC)"

clean_npm_cache: ## clean npm cache
	@echo "Cleaning npm cache..."
	@cd web && npm cache clean --force
	@$(call CLEAR_DIRS,web/node_modules web/build api/base/aiexec/frontend)
	@rm -f web/package-lock.json
	@echo "$(GREEN)NPM cache and frontend directories cleaned.$(NC)"

clean_all: clean_python_cache clean_npm_cache ## clean all caches and temporary directories
	@echo "$(GREEN)All caches and temporary directories cleaned.$(NC)"

setup_uv: ## install uv using pipx
	pipx install uv

add: check_tools ## add dependencies (e.g. make add main=package, make add devel=package, make add base=package)
	@echo 'Adding dependencies'
ifdef devel
	@cd api/base && uv add --group dev $(devel)
endif
ifdef main
	@uv add $(main)
endif
ifdef base
	@cd api/base && uv add $(base)
endif

######################
# CODE TESTS
######################

coverage: ## run the tests and generate a coverage report
	@uv run coverage run
	@uv run coverage erase

unit_tests: ## run unit tests (e.g. make unit_tests async=false)
	@uv sync --frozen
	@EXTRA_ARGS="--instafail -ra -m 'not api_key_required' --durations-path api/tests/.test_durations --splitting-algorithm least_duration $(args)"
	@if [ "$(async)" = "true" ]; then EXTRA_ARGS="$$EXTRA_ARGS --instafail -n auto"; fi;
	@if [ "$(lf)" = "true" ]; then EXTRA_ARGS="$$EXTRA_ARGS --lf"; fi;
	@if [ "$(ff)" = "true" ]; then EXTRA_ARGS="$$EXTRA_ARGS --ff"; fi;
	uv run pytest api/tests/unit \
	--ignore=api/tests/integration \
	--ignore=api/tests/unit/template \
	$$EXTRA_ARGS

unit_tests_looponfail: ## run unit tests in a loop on fail
	@make unit_tests args="-f"

integration_tests: ## run all integration tests
	uv run pytest api/tests/integration --instafail -ra $(args)

integration_tests_no_api_keys: ## run integration tests that don't require api keys
	uv run pytest api/tests/integration --instafail -ra -m "not api_key_required" $(args)

integration_tests_api_keys: ## run integration tests that require api keys
	uv run pytest api/tests/integration --instafail -ra -m "api_key_required" $(args)

tests: unit_tests integration_tests coverage ## run all tests

######################
# TEMPLATE TESTING
######################

template_tests: ## run all starter project template tests
	@echo 'Running Starter Project Template Tests...'
	@uv run pytest api/tests/unit/template/test_starter_projects.py -v -n auto

######################
# CODE QUALITY
######################

codespell: ## run codespell to check spelling
	@uvx codespell --toml pyproject.toml

fix_codespell: ## run codespell to fix spelling errors
	@uvx codespell --toml pyproject.toml --write

format_backend: ## backend code formatters
	@uv run ruff check . --fix
	@uv run ruff format . --config pyproject.toml

format: format_backend format_frontend ## run code formatters

format_frontend_check: ## run biome check without formatting
	@echo 'Running Biome check on frontend...'
	@cd web && npx @biomejs/biome check

unsafe_fix: ## run ruff with unsafe fixes
	@uv run ruff check . --fix --unsafe-fixes

lint: install_backend ## run linters
	@uv run mypy --namespace-packages -p "aiexec"

######################
# RUN PROJECT
######################

run_cli: install_frontend install_backend build_frontend ## run the CLI
	@echo 'Running the CLI'
	@uv run aiexec run \
		--frontend-path $(path) \
		--log-level $(log_level) \
		--host $(host) \
		--port $(port) \
		$(if $(env),--env-file $(env),) \
		$(if $(filter false,$(open_browser)),--no-open-browser)

run_cli_debug: install_frontend build_frontend install_backend ## run the CLI in debug mode
	@echo 'Running the CLI in debug mode'
	@make start env=$(env) host=$(host) port=$(port) log_level=debug

setup_devcontainer: install_backend install_frontend build_frontend ## set up the development container
	uv run aiexec --frontend-path web/build

setup_env: ## set up the environment
	@sh ./scripts/setup/setup_env.sh

backend: setup_env install_backend ## run the backend in development mode
	@-kill -9 $$(lsof -t -i:$(port)) || true
	@echo "Running backend with workers=$(workers) and reload=$(if $(filter-out 1,$(workers)),false,true)"
	AIEXEC_AUTO_LOGIN=$(login) uv run uvicorn \
		--factory aiexec.main:create_app \
		--host $(host) \
		--port $(port) \
		$(if $(filter-out 1,$(workers)),, --reload) \
		--env-file $(env) \
		--loop asyncio \
		$(if $(workers),--workers $(workers),)

build_and_run: setup_env build ## build the project and run it
	$(call CLEAR_DIRS,dist api/base/dist)
	uv run pip install dist/*.tar.gz
	uv run aiexec run

build_and_install: build ## build the project and install it
	@echo 'Removing dist folder'
	$(call CLEAR_DIRS,dist api/base/dist)
	uv run pip install dist/*.whl && pip install api/base/dist/*.whl --force-reinstall

build: setup_env install_frontendci build_frontend ## build the frontend static files and package the project
	@make build_aiexec_base args="$(args)"
	@make build_aiexec args="$(args)"

build_aiexec_base:
	cd api/base && uv build $(args)

build_aiexec_backup:
	uv lock && uv build

build_aiexec:
	uv lock --no-upgrade
	uv build $(args)
ifdef restore
	mv pyproject.toml.bak pyproject.toml
	mv uv.lock.bak uv.lock
endif

######################
# DOCKER
######################

docker_build: dockerfile_build clear_dockerimage ## build DockerFile

docker_build_backend: dockerfile_build_be clear_dockerimage ## build Backend DockerFile

docker_build_frontend: dockerfile_build_fe clear_dockerimage ## build Frontend Dockerfile

dockerfile_build:
	@echo 'BUILDING DOCKER IMAGE: ${DOCKERFILE}'
	@docker build --rm \
		-f ${DOCKERFILE} \
		-t aiexec:${VERSION} .

dockerfile_build_be: dockerfile_build
	@echo 'BUILDING DOCKER IMAGE BACKEND: ${DOCKERFILE_BACKEND}'
	@docker build --rm \
		--build-arg AIEXEC_IMAGE=aiexec:${VERSION} \
		-f ${DOCKERFILE_BACKEND} \
		-t aiexec_backend:${VERSION} .

dockerfile_build_fe: dockerfile_build
	@echo 'BUILDING DOCKER IMAGE FRONTEND: ${DOCKERFILE_FRONTEND}'
	@docker build --rm \
		--build-arg AIEXEC_IMAGE=aiexec:${VERSION} \
		-f ${DOCKERFILE_FRONTEND} \
		-t aiexec_frontend:${VERSION} .

clear_dockerimage:
	@echo 'Clearing the docker build'
	@if docker images -f "dangling=true" -q | grep -q '.*'; then \
		docker rmi $$(docker images -f "dangling=true" -q); \
	fi

docker_compose_up: docker_build docker_compose_down ## run docker compose up
	@echo 'Running docker compose up'
	docker compose -f $(DOCKER_COMPOSE) up --remove-orphans

docker_compose_down: ## run docker compose down
	@echo 'Running docker compose down'
	docker compose -f $(DOCKER_COMPOSE) down || true

dcdev_up: ## run dev docker compose up
	@echo 'Running docker compose up'
	docker compose -f docker/dev.docker-compose.yml down || true
	docker compose -f docker/dev.docker-compose.yml up --remove-orphans

######################
# DEPENDENCY MANAGEMENT
######################

lock_base:
	cd api/base && uv lock

lock_aiexec:
	uv lock

lock: lock_base lock_aiexec ## lock dependencies

update: ## update dependencies
	@echo 'Updating dependencies'
	cd api/base && uv sync --upgrade
	uv sync --upgrade

publish_base:
	cd api/base && uv publish

publish_aiexec:
	uv publish

publish_base_testpypi:
	cd api/base && uv publish -r test-pypi

publish_aiexec_testpypi:
	uv publish -r test-pypi

publish: ## publish the project to PyPI (e.g. make publish target=base/main)
	@echo 'Publishing the project'
ifeq ($(target),base)
	make publish_base
else ifeq ($(target),main)
	make publish_aiexec
else
	@echo "Usage: make publish target=[base|main]"
endif

publish_testpypi: ## publish the project to TestPyPI (e.g. make publish_testpypi target=base/main)
	@echo 'Publishing the project to TestPyPI'
ifeq ($(target),base)
	make publish_base_testpypi
else ifeq ($(target),main)
	make publish_aiexec_testpypi
else
	@echo "Usage: make publish_testpypi target=[base|main]"
endif

######################
# DATABASE MIGRATIONS
######################

alembic-revision: ## generate a new migration (e.g. make alembic-revision message="Add user table")
	@echo 'Generating a new Alembic revision'
	cd api/base/aiexec/ && uv run alembic revision --autogenerate -m "$(message)"

alembic-upgrade: ## upgrade database to the latest version
	@echo 'Upgrading database to the latest version'
	cd api/base/aiexec/ && uv run alembic upgrade head

alembic-downgrade: ## downgrade database by one version
	@echo 'Downgrading database by one version'
	cd api/base/aiexec/ && uv run alembic downgrade -1

alembic-current: ## show current revision
	@echo 'Showing current Alembic revision'
	cd api/base/aiexec/ && uv run alembic current

alembic-history: ## show migration history
	@echo 'Showing Alembic migration history'
	cd api/base/aiexec/ && uv run alembic history --verbose

alembic-check: ## check migration status
	@echo 'Running alembic check'
	cd api/base/aiexec/ && uv run alembic check

alembic-stamp: ## stamp the database with a specific revision (e.g. make alembic-stamp revision=<revision_id>)
	@echo 'Stamping the database with revision $(revision)'
	cd api/base/aiexec/ && uv run alembic stamp $(revision)

######################
# VERSION MANAGEMENT
######################

patch: ## Update version across all projects. Usage: make patch v=1.5.0
	@uv run python scripts/update_version.py $(v)

######################
# LOAD TESTING
######################

# Default values for locust configuration
locust_users ?= 10
locust_spawn_rate ?= 1
locust_host ?= http://localhost:7860
locust_headless ?= true
locust_time ?= 300s
locust_api_key ?= your-api-key
locust_flow_id ?= your-flow-id
locust_file ?= api/tests/locust/locustfile.py
locust_min_wait ?= 2000
locust_max_wait ?= 5000
locust_request_timeout ?= 30.0

locust: ## run locust load tests (see Makefile for options)
	@if [ ! -f "$(locust_file)" ]; then \
		echo "$(RED)Error: Locustfile not found at $(locust_file)$(NC)"; \
		exit 1;
	fi
	@echo "Starting Locust with $(locust_users) users, spawn rate of $(locust_spawn_rate)"
	@echo "Testing host: $(locust_host)"
	@echo "Using locustfile: $(locust_file)"
	@export API_KEY=$(locust_api_key) && \
	export FLOW_ID=$(locust_flow_id) && \
	export AIEXEC_HOST=$(locust_host) && \
	export MIN_WAIT=$(locust_min_wait) && \
	export MAX_WAIT=$(locust_max_wait) && \
	export REQUEST_TIMEOUT=$(locust_request_timeout) && \
	cd $$(dirname "$(locust_file)") && \
	if [ "$(locust_headless)" = "true" ]; then \
		uv run locust \
			--headless \
			-u $(locust_users) \
			-r $(locust_spawn_rate) \
			--run-time $(locust_time) \
			--host $(locust_host) \
			-f $$(basename "$(locust_file)"); \
	else \
		uv run locust \
			-u $(locust_users) \
			-r $(locust_spawn_rate) \
			--host $(locost_host) \
			-f $$(basename "$(locust_file)"); \
	fi

######################
# INCLUDE FRONTEND MAKEFILE
######################

# Include frontend-specific Makefile
include Makefile.frontend