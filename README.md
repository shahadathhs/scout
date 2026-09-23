# scout

A self-hosted deep-research platform. Ask a question — scout drafts a research
plan you approve, runs parallel subagents across the web, and delivers a report
where every claim cites a source you can open.

## Features

### Core research pipeline

- **Plan-first workflow** — scout drafts a research plan (sub-questions +
  objectives) that you review, edit, and approve before anything runs
- **Parallel subagents** — a lead agent spawns 3–5 workers, each with its own
  context window, researching sub-questions simultaneously
- **Live progress** — every step streams to the UI: searches, pages being
  read, subagent status. Pause or stop mid-run at any time
- **Verified inline citations** — every claim is numbered and links to a real
  collected source; a second pass flags unsupported claims
- **Background runs** — research jobs take minutes, not seconds; runs survive
  navigation and notify on completion

### The report

- **Click-through citations** — hover for source cards (title, URL, snippet),
  click to open; sources sidebar sorted by most-cited
- **Conflict flagging** — where sources disagree, the report says so
- **Follow-up questions** — chat with the report, grounded in collected
  sources only
- **Export & share** — copy/download as Markdown, structured JSON (the full
  reproducible artifact), print to PDF, shareable report links

### Trust & control

- **Radical transparency** — expandable log of every query, fetched page,
  and LLM thought, with token counts per phase
- **Source scoping** — allowlist/denylist domains per run, "academic only"
  presets, local files researched alongside the web

### Developer outputs

- Clean Markdown + structured JSON for every report — built to be piped
  somewhere else

## Stack

- **Backend** — FastAPI, Python 3.12, uv, SQLAlchemy 2 (async) + Alembic,
  Postgres
- **Frontend** — Next.js 16 (App Router), TypeScript, Tailwind v4, shadcn/ui,
  pnpm
- **Orchestration** — Makefile + Docker Compose

## Quick start

```bash
make setup      # env files + uv sync + pnpm install + postgres + migrations
make dev        # backend :7001 + frontend :3100 (hot reload)
```

Or all-Docker: `make up` (then http://localhost:3100).

## Layout

```
scout/
├── backend/           FastAPI app (core/, models/, modules/, alembic/)
├── frontend/          Next.js app (src/app, src/components/ui)
├── compose.yaml       postgres + backend + frontend
└── Makefile           task runner
```

| Service  | Port | URL                        |
| -------- | ---- | -------------------------- |
| backend  | 7001 | http://localhost:7001/docs |
| frontend | 3100 | http://localhost:3100      |
| postgres | 5432 | —                          |

## Status

🚧 Boilerplate — the research pipeline is not built yet. The skeleton above
(dev environment, DB, quality gates, CI) is in place.

## License

MIT
