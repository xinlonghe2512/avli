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
	@echo " make agents"
	@echo " make ingestor"

.PHONY: agents
agents: ## Run the Agents FastAPI service in development mode
	cd apps/agents && $(UV) run python main.py --env-file ../../$(ENV_FILE)

.PHONY: ingestor
ingestor: ## Run the Ingestor FastAPI service in development mode
	cd apps/ingestor && $(UV) run python main.py --env-file ../../$(ENV_FILE)

# ---------------------- Dependencies ---------------------- #

.PHONY: install
install: ## Install and sync all workspace dependencies
	$(UV) sync --all-packages

.PHONY: lock
lock: ## Update the uv lockfile
	$(UV) lock

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

# ---------------------- Testing ---------------------- #

.PHONY: test
test: test-agents test-ingestor ## Run all service test suites

.PHONY: test-agents
test-agents: ## Run Agents tests
	cd apps/agents && $(UV) run pytest tests

.PHONY: test-ingestor
test-ingestor: ## Run Ingestor tests
	cd apps/ingestor && $(UV) run pytest tests

# ---------------------- DeepEval ---------------------- #

.PHONY: eval-agents
eval-agents: ## Run Agents DeepEval evaluations
	cd apps/agents && $(UV) run run deepeval test run tests/evals

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

# ---------------------- Docker ---------------------- #

.PHONY: docker-build-agents
docker-build: ## Build the Agents Docker image
	docker build -t $(PROJECT_NAME)-agents apps/agents

.PHONY: docker-build-ingestor
docker-build-ingestor: ## Build the Ingestor Docker image
	docker build -t $(PROJECT_NAME)-ingestor apps/ingestor

.PHONY: docker-up
docker-up: ## Start the development Docker Compose stack
	docker compose -f compose.dev.yml up -d

.PHONY: docker-down
docker-down: ## Stop the development Docker Compose stack
	docker compose -f compose.dev.yml down

.PHONY: docker-logs
docker-logs: ## Follow development Docker Compose logs
	docker compose -f compose.dev.yml logs -f

# ---------------------- Help ---------------------- #
.PHONY: help
help: ## Show available Make targets
	@echo ""
	@echo "Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.## .$$' $(MAKEFILE_LIST) |
	sort |
	awk 'BEGIN {FS = ":.*## "}; {printf " \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""