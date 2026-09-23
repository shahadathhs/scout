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
