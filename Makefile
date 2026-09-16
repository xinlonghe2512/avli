# ---------------------- Project Config ---------------------- #
PROJECT_NAME := Avli

ENV_FILE := .env

AIS_DIR := services/asset-intel-service
WEB_DIR := apps/web

UV := uv

PNPM := pnpm
VP := vpr

.DEFAULT_GOAL := help

# ---------------------- Shell ---------------------- #

.PHONY: shell
shell: ## Open Python shell inside the uv environment
	$(UV) run python

# ---------------------- Local Development (Dev) ---------------------- #

.PHONY: dev
dev: ## Show commands for running all services
	@echo "Run the services in separate terminals:"
	@echo ""
	@echo " make web"
	@echo " make ais"
	@echo ""

.PHONY: web
web: ## Run the SvelteKit web application in development mode
	$(PNPM) --dir $(WEB_DIR) vpr dev --host 0.0.0.0

.PHONY: web-preview
web-preview: ## Preview the production web build
	$(PNPM) --dir $(WEB_DIR) vpr preview --host 0.0.0.0

.PHONY: web-build
web-build: ## Build the SvelteKit web application
	$(PNPM) --dir $(WEB_DIR) vpr build

.PHONY: ais
ais: ## Run the Asset Intelligence Service in development mode
	$(UV) run --directory $(AIS_DIR) uvicorn src.main:service --reload --host 0.0.0.0 --port 8000

# ---------------------- Workspace Dependencies ---------------------- #

.PHONY: install
install: install-python install-ts ## Install all workspace dependencies

.PHONY: install-ts
install-ts: ## Install TypeScript workspace dependencies
	$(PNPM) --dir $(WEB_DIR) install --frozen-lockfile

.PHONY: install-python
install-python: ## Install Python workspace dependencies
	$(UV) sync --all-packages

.PHONY: lock
lock: ## Update the uv lockfile
	$(PNPM) --dir $(WEB_DIR) install --lockfile-only
	$(UV) lock

.PHONY: upgrade
upgrade: ## Upgrade all dependencies and update the uv lockfile
	$(PNPM) --dir $(WEB_DIR) update
	$(UV) lock --upgrade

.PHONY: sync
sync: ## Sync the uv workspace from the lockfile
	$(PNPM) --dir $(WEB_DIR) install --frozen-lockfile
	$(UV) sync --all-packages --frozen

# ---------------------- Workspace Linting & Formatting ---------------------- #

.PHONY: check
web-check: ## Check all workspace code
	$(PNPM) --dir $(WEB_DIR) vpr check

.PHONY: lint
web-lint: ## Lint all workspace code (uv auto-fix code with Ruff)
	$(PNPM) --dir $(WEB_DIR) vpr lint
	$(UV) run ruff check . --fix

.PHONY: format
web-format:## Format all workspace code
	$(PNPM) --dir $(WEB_DIR) vpr fmt
	$(UV) run ruff format .

.PHONY: format-check
format-check: ## Check formatting without modifying files
	$(PNPM) --dir $(WEB_DIR) vpr fmt --check
	$(UV) run ruff format --check .

.PHONY: typecheck
typecheck: ## Type-check all workspace code
	$(PNPM) --dir $(WEB_DIR) vpr check
	$(UV) run ty check

.PHONY: audit
audit: ## Check workspace runtime dependencies
	$(PNPM) --dir $(WEB_DIR) audit || true
	$(UV) audit --no-dev || true

# ---------------------- Testing / Evaluation ---------------------- #

.PHONY: test
install: test-web test-ais ## Test workspace

.PHONY: test-web
web-test: ## Run web application tests
	$(PNPM) --dir $(WEB_DIR) vpr test

.PHONY: test-ais
test-ais: ## Run asset intelligence service tests
	$(UV) run --directory $(AIS_DIR) pytest tests

.PHONY: eval-ais
eval-ais: ## Run asset intelligence service DeepEval evaluations
	$(UV) run --directory $(AIS_DIR) deepeval test run tests/evals

# ---------------------- Full Check ------------------- #

.PHONY: full-check
full-check: ## Run all CI-equivalent checks
	lint format-check typecheck test

# ---------------------- Git Hooks -------------------- #

.PHONY: install-hooks
install-hooks: ## Install prek git hooks
	$(UV) run prek install

.PHONY: reinstall-hooks
reinstall-hooks: ## Reinstall prek git hooks
	$(UV) run prek uninstall
	$(UV) run prek install --install-hooks

.PHONY: hooks
hooks: ## Run all prek hooks against all files
	$(UV) run prek run --all-files

# ---------------------- Cleanup ---------------------- #
.PHONY: clean
clean: ## Remove caches and build artifacts
	@echo "Cleaning up build and cache files..."

	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ty_cache" -prune -exec rm -rf {} +

	rm -rf \
		 .coverage \
		 dist \
		 build \
		 $(WEB_DIR)/.svelte-kit \
		 $(WEB_DIR)/build \
		 $(WEB_DIR)/node_modules/.vite

# ---------------------- Docker Build ---------------------- #

.PHONY: build-web
build-web: ## Build the Asset Intelligence Service Docker image
	docker build -t $(PROJECT_NAME)-web $(WEB_DIR)

.PHONY: build-celery
build-celery: ## Build the Celery Docker image
	docker build -t $(PROJECT_NAME)-celery -f docker/celery/Dockerfile .

.PHONY: build-ais
build-ais: ## Build the Asset Intelligence Service Docker image
	docker build -t $(PROJECT_NAME)-asset-intel-service $(AIS_DIR)

.PHONY: build-all
build-all: build-web build-ais build-celery ## Build all Docker images

# ---------------------- Full Stack Docker Compose ---------------------- #

.PHONY: up
up: apps-up services-up obs-up obs-ai-up ## Start all Docker Compose stacks

.PHONY: down
down: apps-down services-down obs-down obs-ai-down ## Stop all Docker Compose stacks

# ---------------------- Application Stack Docker Compose ---------------------- #

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
apps-restart: apps-down apps-up ## Restart the application stack

# ---------------------- Service Stack Docker Compose ---------------------- #

.PHONY: services-up
services-up: ## Start the service stack
	docker compose -f docker/compose-services.yaml up -d --build

.PHONY: services-down
services-down: ## Stop the service stack
	docker compose -f docker/compose-services.yaml down

.PHONY: services-logs
services-logs: ## Follow the service stack logs
	docker compose -f docker/compose-services.yaml logs -f

.PHONY: services-restart
services-restart: services-down services-up ## Restart the service stack

# ---------------------- Observability Stack Docker Compose ---------------------- #

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

# ---------------------- AI Observability Stack Docker Compose ---------------------- #

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
