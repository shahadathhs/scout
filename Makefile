# ── scout Makefile ────────────────────────────────────────────────────
# Run `make` (or `make help`) to list all targets.

.DEFAULT_GOAL := help

BACKEND_DIR  := backend
WEB_DIR      := apps/web
UV           := uv run
PNPM         := pnpm

.PHONY: help setup install dev backend web typecheck lint lint-backend \
        lint-web format build check clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / \
	  {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ── Setup ─────────────────────────────────────────────────────────────

setup: env install ## Full setup: env files + all installs

env: ## Create .env from example (root + backend)
	@for f in .env backend/.env; do \
	  if [ ! -f "$$f" ] && [ -f "$$f.example" ]; then cp "$$f.example" "$$f" && echo "Created $$f"; \
	  else echo "$$f exists (skipped)"; fi; \
	done

install: ## Install backend (uv) + workspace (pnpm)
	cd $(BACKEND_DIR) && uv sync
	pnpm install

# ── Dev ───────────────────────────────────────────────────────────────

dev: ## Run backend + web in parallel
	$(MAKE) -j2 backend web

backend: ## Run FastAPI dev server (:7001)
	cd $(BACKEND_DIR) && $(UV) uvicorn app.main:app --reload --port 7001

web: ## Run Next.js dev server (:3100)
	cd $(WEB_DIR) && pnpm dev

# ── Quality ───────── pipeline: typecheck + lint + build

typecheck: ## Typecheck backend (pyright) + web (tsc)
	cd $(BACKEND_DIR) && $(UV) pyright
	cd $(WEB_DIR) && pnpm typecheck

lint: lint-backend lint-web ## Lint everything

lint-backend: ## Ruff check backend
	cd $(BACKEND_DIR) && $(UV) ruff check .

lint-web: ## ESLint frontend
	cd $(WEB_DIR) && pnpm lint

format: ## Format backend (ruff) + root (prettier)
	cd $(BACKEND_DIR) && $(UV) ruff format .
	pnpm format

build: ## Build web for production
	pnpm build

check: typecheck lint build ## Full CI check

clean: ## Remove build artifacts
	cd $(BACKEND_DIR) && rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	rm -rf .turbo node_modules apps/web/.next
