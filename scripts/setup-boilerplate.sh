#!/bin/bash
# scout monorepo boilerplate setup
# structure: turborepo (pnpm) + FastAPI backend (uv) + Next.js frontend
set -euo pipefail

cd /Users/digitalpylot/code/own/scout
ROOT=$(pwd)

echo "── 1. wipe old CLI scaffold ──"
rm -rf scout_cli pyproject.toml uv.lock .python-version README.md
mkdir -p backend frontend apps/web packages/db packages/eslint-config packages/typescript-config

echo "── 2. turborepo root files ──"

cat > package.json << 'EOF'
{
  "name": "scout",
  "version": "0.1.0",
  "private": true,
  "packageManager": "pnpm@10.0.0",
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "start": "turbo start",
    "typecheck": "turbo typecheck",
    "lint": "turbo lint",
    "lint:fix": "turbo lint:fix",
    "format": "turbo format",
    "format:check": "turbo format:check",
    "clean": "turbo clean"
  },
  "devDependencies": {
    "turbo": "^2.5.0",
    "prettier": "^3.4.0"
  }
}
EOF

cat > pnpm-workspace.yaml << 'EOF'
packages:
  - "apps/*"
  - "packages/*"
EOF

cat > turbo.json << 'EOF'
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["$TURBO_DEFAULT$", "!{**/*.test.ts,**/*.spec.ts}"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "start": { "cache": false },
    "typecheck": { "dependsOn": ["^typecheck"] },
    "lint": { "dependsOn": ["^lint"] },
    "format": { "dependsOn": ["^format"] },
    "format:check": { "dependsOn": ["^format:check"] },
    "clean": { "cache": false }
  }
}
EOF

cat > .gitignore << 'EOF'
# deps
node_modules/
.pnp
.pnp.js
# build
.next/
out/
dist/
*.tsbuildinfo
# turbo
.turbo/
# python
__pycache__/
*.pyc
.venv/
.pytest_cache/
.ruff_cache/
# env & data
.env
.env.local
*.db
*.sqlite
data/
# misc
.DS_Store
*.log
EOF

cat > .npmrc << 'EOF'
# pnpm workspace
link-workspace-packages=true
EOF

echo "── 3. shared packages (typescript-config, eslint-config) ──"

cat > packages/typescript-config/package.json << 'EOF'
{
  "name": "@scout/typescript-config",
  "version": "0.0.0",
  "private": true,
  "files": ["*.json"]
}
EOF
cat > packages/typescript-config/base.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve"
  }
}
EOF
cat > packages/typescript-config/nextjs.json << 'EOF'
{
  "extends": "./base.json",
  "compilerOptions": {
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

cat > packages/eslint-config/package.json << 'EOF'
{
  "name": "@scout/eslint-config",
  "version": "0.0.0",
  "private": true,
  "files": ["*.js"]
}
EOF
# minimal flat config; apps extend by re-export
cat > packages/eslint-config/base.js << 'EOF'
// @ts-check
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: [".next/", "dist/", "node_modules/"] },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
);
EOF
cat > packages/eslint-config/package.json << 'EOF'
{
  "name": "@scout/eslint-config",
  "version": "0.0.0",
  "private": true,
  ", files": ["*.js"],
  "dependencies": {
    "@eslint/js": "^9.0.0",
    "typescript-eslint": "^8.0.0"
  }
}
EOF
# (fix the typo'd key above)
python3 - << 'PYEOF'
import json
p = "packages/eslint-config/package.json"
d = json.load(open(p))
d.pop(", files", None)
d["files"] = ["*.js"]
json.dump(d, open(p, "w"), indent=2)
open(p, "a").write("\n")
PYEOF

echo "── 4. Next.js app: apps/web ──"
cd "$ROOT/apps/web"

cat > package.json << 'EOF'
{
  "name": "web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --port 3100",
    "build": "next build",
    "start": "next start",
    "typecheck": "tsc --noEmit",
    "lint": "next lint",
    "clean": "rm -rf .next .turbo"
  },
  "dependencies": {
    "next": "^15.3.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@scout/typescript-config": "workspace:*",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.7.0"
  }
}
EOF

cat > tsconfig.json << 'EOF'
{
  "extends": "@scout/typescript-config/nextjs.json"
}
EOF

mkdir -p src/app
cat > src/app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "scout — deep research",
  description: "Self-hosted AI research agent with verifiable citations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
EOF

cat > src/app/page.tsx << 'EOF'
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-24">
      <h1 className="text-4xl font-bold">scout</h1>
      <p className="text-lg opacity-70">Deep research, self-hosted. Boilerplate is up.</p>
    </main>
  );
}
EOF

cat > src/app/globals.css << 'EOF'
:root {
  --background: #0a0a0a;
  --foreground: #ededed;
}

html {
  color-scheme: dark;
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: ui-sans-serif, system-ui, sans-serif;
}
EOF

cat > next.config.ts << 'EOF'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {};

export default nextConfig;
EOF

echo "── 5. FastAPI backend: backend/ (uv) ──"
cd "$ROOT/backend"

cat > pyproject.toml << 'EOF'
[project]
name = "scout-backend"
version = "0.1.0"
description = "scout — deep research backend (FastAPI)"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "pydantic>=2.10",
    "pydantic-settings>=2.7",
    "httpx>=0.28",
    "ddgs>=9.0",
]

[dependency-groups]
dev = [
    "ruff>=0.9",
    "pyright>=1.1.390",
    "pytest>=8.0",
    "pytest-asyncio>=0.25",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pyright]
venvPath = "."
venv = ".venv"
EOF

cat > .python-version << 'EOF'
3.12
EOF

mkdir -p app/core
cat > app/__init__.py << 'EOF'
EOF
cat > app/core/__init__.py << 'EOF'
EOF

cat > app/core/config.py << 'EOF'
"""Environment-driven settings (adda-style)."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    # LLM (any OpenAI-compatible endpoint)
    llm_base_url: str = "https://api.z.ai/api/paas/v4"
    llm_api_key: str = ""
    llm_model: str = "glm-4.6"
    fast_model: str = ""  # falls back to llm_model

    # research knobs
    max_subagents: int = 4
    subagent_step_budget: int = 8


settings = Settings()
EOF

cat > app/main.py << 'EOF'
"""scout backend entry."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="scout", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3100"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "model": settings.llm_model,
        "key_present": bool(settings.llm_api_key),
    }
EOF

echo "── 6. root README, env example, compose, Makefile ──"
cd "$ROOT"

cat > README.md << 'EOF'
# scout

A self-hosted deep-research platform. Ask a question — scout drafts a research
plan you approve, runs parallel subagents across the web, and delivers a
report where every claim cites a source you can open.

Monorepo: **FastAPI backend** (`backend/`, uv, Python 3.12) + **Next.js
frontend** (`apps/web`, Turborepo/pnpm).

## Quick start

```bash
make setup     # env files + install backend (uv) + frontend (pnpm)
make dev       # backend :7001 + web :3100 (parallel)
```

Or all-Docker: `docker compose up --build`

## Layout

```
scout/
├── apps/web          Next.js 15 frontend (Turborepo)
├── backend/          FastAPI + uv
├── packages/         shared ts-config / eslint-config
├── compose.yaml      postgres? no — sqlite for now; app services only
└── Makefile          adda-style task runner
```

## Status

🚧 Phase 0 — boilerplate. See the plan in `.hermes/plans/`.

## License

MIT
EOF

cat > .env.example << 'EOF'
# ── LLM provider (any OpenAI-compatible endpoint) ──
# z.ai GLM (default), OpenRouter, Groq, OpenAI, Ollama — swap base URL + key
LLM_BASE_URL=https://api.z.ai/api/paas/v4
LLM_API_KEY=
LLM_MODEL=glm-4.6
# cheap model for routing/titles (falls back to LLM_MODEL)
FAST_MODEL=

# ── research knobs ──
MAX_SUBAGENTS=4
SUBAGENT_STEP_BUDGET=8
EOF

cat > compose.yaml << 'EOF'
services:
  backend:
    build: ./backend
    ports:
      - "7001:7001"
    env_file: .env
    volumes:
      - ./data:/data
  web:
    build: ./apps/web
    ports:
      - "3100:3100"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:7001
    depends_on:
      - backend
EOF

cat > backend/Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY app ./app

EXPOSE 7001

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7001"]
EOF

cat > apps/web/Dockerfile << 'EOF'
FROM node:22-slim AS builder
WORKDIR /app
RUN corepack enable
COPY . .
RUN pnpm install --frozen-lockfile || pnpm install
RUN pnpm build

FROM node:22-slim
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/public ./public
EXPOSE 3100
CMD ["node", "server.js"]
EOF
# standalone output needs next.config tweak + public dir — patch next.config
cat > apps/web/next.config.ts << 'EOF'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
EOF
mkdir -p apps/web/public

cat > Makefile << 'EOF'
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
EOF

# backend .env.example (backend reads its own .env too)
cp .env.example backend/.env.example

echo "── 7. install everything ──"
cd "$ROOT/backend" && uv sync 2>&1 | tail -3
cd "$ROOT" && pnpm install 2>&1 | tail -5

echo "── 8. verify ──"
cd "$ROOT/backend" && uv run python -c "from app.main import app; print('backend imports OK')"
cd "$ROOT" && pnpm -r --filter web typecheck 2>&1 | tail -3

echo "DONE"
