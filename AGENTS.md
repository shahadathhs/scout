# AGENTS.md

Guidance for coding agents working in this repo.

## What this is

scout — a self-hosted deep-research platform (plan-first research, parallel
subagents, cited reports). FastAPI backend + Next.js frontend.

## Commands

```bash
make setup      # first-time: env files + uv sync + pnpm install + postgres + migrations
make dev        # backend :7001 (uvicorn --reload) + frontend :3100 (next dev)
make backend    # backend only
make frontend   # frontend only
make db-up      # postgres in docker
make migrate    # alembic upgrade head
make migration m="msg"   # autogenerate migration
make check      # pyright + ruff + oxlint/eslint/prettier + next build
make format     # ruff format + autofix (backend)
make lint-web   # frontend lint
```

## Ports & URLs

| Service  | Port | URL                          |
| -------- | ---- | ---------------------------- |
| backend  | 7001 | http://localhost:7001/docs   |
| frontend | 3100 | http://localhost:3100        |
| postgres | 5432 | scout:scout@localhost/scout  |

## Backend (FastAPI, uv, Python 3.12)

- Layout: `main.py` (app + CORS + health), `core/` (config, database),
  `models/` (SQLAlchemy Base + models), `modules/<feature>/` per domain
  feature (router.py, schemas.py, service/).
- All HTTP routers mount under `settings.api_prefix` (`/api`).
- Config via pydantic-settings reading `backend/.env` (`core/config.py`).
- Migrations: Alembic async, URL comes from settings (not alembic.ini).
- Import style: absolute within the app root (`from core.config import
  settings`) — the app root is the cwd when running.

## Frontend (Next.js 16, pnpm)

- App Router with `src/` dir; shadcn/ui components in `src/components/ui`
  (install new ones with `pnpm dlx shadcn@latest add <component>`).
- API base URL helper: `src/lib/api.ts` (`NEXT_PUBLIC_API_BASE_URL`,
  default `http://localhost:7001`). Backend calls are cross-origin; CORS is
  configured on the backend.
- Lint chain: oxlint (TS/TSX) → eslint → prettier. Run before committing.
- Next.js 16 has breaking changes vs older Next — consult
  `frontend/node_modules/next/dist/docs/` when unsure.

## Conventions

- Conventional Commits (enforced by commitlint).
- pre-commit runs lint-staged (oxlint --fix + prettier) on staged TS/TSX.
- Don't commit secrets; env files are gitignored (`make env` recreates them).
