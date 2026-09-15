# ---------------------- Project Config ---------------------- #
PROJECT_NAME := Avli
ENV_FILE := .env
UV := uv
PYTHON := $(UV) run python
PREK := $(UV) run prek

.DEFAULT_GOAL := help

# ---------------------- Local Development ---------------------- #
.PHONY: shell
shell: ## Open Python shell inside the uv environment
	$(PYTHON)

.PHONY: dev
dev: ## Show commands for running all services
	@echo "Run the services in separate terminals:"
	@echo " make asset-intel-service"

.PHONY: asset-intel-service
asset-intel-service: ## Run the Asset Intelligence Service in development mode
	cd services/asset-intel-service && $(UV) run uvicorn src.main:service --reload --host 0.0.0.0 --port 8000

# ---------------------- Dependencies ---------------------- #

.PHONY: install
install: ## Install and sync all workspace dependencies
	$(UV) sync --all-packages

.PHONY: lock
lock: ## Update the uv lockfile
	$(UV) lock

.PHONY: upgrade
upgrade: ## Upgrade all dependencies and update the uv lockfile
	$(UV) lock --upgrade

.PHONY: sync
sync: ## Sync the uv workspace from the lockfile
	$(UV) sync --all-packages --frozen

# ---------------------- Linting & Formatting ---------------------- #
.PHONY: format
format: ## Format code with Ruff
	$(UV) run ruff format .

.PHONY: lint
lint: ## Lint and auto-fix code with Ruff
	$(UV) run ruff check . --fix

.PHONY: format-check
format-check: ## Check formatting without modifying files
	$(UV) run ruff format --check .

.PHONY: typecheck
typecheck: ## Type-check the workspace with ty
	$(UV) run ty check

.PHONY: audit
audit: ## Check project's runtime dependencies
	$(UV) audit --no-dev || true

# .PHONY: scan
# scan: ## Check project's runtime dependencies
# 	@$(UV) run python scripts/scan-dependencies.py

# ---------------------- Testing ---------------------- ### Run all service test suites

.PHONY: test-asset-intel-service
test-asset-intel-service: ## Run Asset Intelligence Service tests
	cd services/asset-intel-service && $(UV) run pytest tests

# ---------------------- DeepEval ---------------------- #

.PHONY: eval-asset-intel-service
eval-asset-intel-service: ## Run Asset Intelligence Service DeepEval evaluations
	cd services/asset-intel-service && $(UV) run run deepeval test run tests/evals

# ---------------------- Full Check ------------------- #

.PHONY: full-check
full-check: ## Run all CI-equivalent checks
	$(UV) run ruff format --check .
	$(UV) run ruff check .
	$(UV) run ty check
	$(UV) run pytest -v

# ---------------------- Git Hooks -------------------- #

.PHONY: hooks
hooks: ## Run all prek hooks against all files
	$(PREK) run --all-files

.PHONY: install-hooks
install-hooks: ## Install prek git hooks
	$(PREK) install

.PHONY: reinstall-hooks
reinstall-hooks: ## Reinstall prek git hooks
	$(PREK) uninstall
	$(PREK) install --install-hooks

# ---------------------- Cleanup ---------------------- #
.PHONY: clean
clean: ## Remove caches and build artifacts
	@echo "Cleaning up build and cache files..."
	find . -type d -name "pycache" -prune -exec rm -rf {} +
	rm -rf
	.pytest_cache
	.ruff_cache
	.ty_cache
	.coverage
	dist
	build

# ---------------------- Docker Build ---------------------- #

.PHONY: build-web
build-web: ## Build the Asset Intelligence Service Docker image
	docker build -t $(PROJECT_NAME)-web apps/web

.PHONY: build-asset-intel-service
build-asset-intel-service: ## Build the Asset Intelligence Service Docker image
	docker build -t $(PROJECT_NAME)-asset-intel-service services/asset-intel-service

.PHONY: build-celery
build-celery: ## Build the Celery Docker image
	docker build -t $(PROJECT_NAME)-celery -f docker/celery/Dockerfile .

.PHONY: build-all
build: build-asset-intel-service build-celery ## Build both Docker images

# ---------------------- Application Docker Compose ---------------------- #

.PHONY: apps-up
apps-up: ## Start the application stack
	docker compose -f docker/compose-apps.yaml up -d --build

.PHONY: apps-down
apps-down: ## Stop the application stack
	docker compose -f docker/compose-apps.yaml down

.PHONY: apps-logs
apps-logs: ## Follow the application stack logs
	docker compose -f docker/compose-apps.yaml logs -f

.PHONY: apps-restart
apps-restart: docker-down docker-up ## Restart the application stack

# ---------------------- Service Docker Compose ---------------------- #

.PHONY: services-up
services-up: ## Start the service stack
	docker compose -f docker/compose-services.yaml up -d --build

.PHONY: services-down
services-down: ## Stop the service stack
	docker compose -f docker/compose-services.yaml down

.PHONY: apps-logs
services-logs: ## Follow the service stack logs
	docker compose -f docker/compose-services.yaml logs -f

.PHONY: apps-restart
services-restart: docker-down docker-up ## Restart the service stack

# ---------------------- Observability Docker Compose ---------------------- #

.PHONY: obs-up
obs-up: ## Start the observability stack
	docker compose -f docker/compose-obs.yaml up -d

.PHONY: obs-down
obs-down: ## Stop the observability stack
	docker compose -f docker/compose-obs.yaml down

.PHONY: obs-logs
obs-logs: ## Follow observability stack logs
	docker compose -f docker/compose-obs.yaml logs -f

.PHONY: obs-restart
obs-restart: obs-down obs-up ## Restart the observability stack

# ---------------------- AI Observability Docker Compose ---------------------- #

.PHONY: obs_ai-up
obs_ai-up: ## Start the ai observability stack
	docker compose -f docker/compose-obs_ai.yaml up -d

.PHONY: obs_ai-down
obs_ai-down: ## Stop the ai observability stack
	docker compose -f docker/compose-obs_ai.yaml down

.PHONY: obs-logs
obs_ai-logs: ## Follow ai observability stack logs
	docker compose -f docker/compose-obs_ai.yaml logs -f

.PHONY: obs_ai-restart
obs_ai-restart: obs_ai-down obs_ai-up ## Restart the ai observability stack

# ---------------------- Help ---------------------- #
.PHONY: help
help: ## Show available Make targets
	@echo ""
	@echo "Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*## "}; {printf " \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
