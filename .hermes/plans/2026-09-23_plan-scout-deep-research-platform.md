# Scout — Deep Research Platform: Implementation Plan

> **For Hermes:** Execute task-by-task with user checkpoints. This is a LONG-TERM project — each phase should be shippable on its own.

**Goal:** A self-hostable deep-research web app (Perplexity/ChatGPT deep-research class) with plan-first workflow, live agent progress, parallel subagents, and verifiable citations — that a premium ChatGPT/Claude user would still prefer (no credit limits, full transparency, local + web sources, developer outputs).

**Architecture:** Next.js 15 (App Router) full-stack — UI + API routes in one deployable. Research runs as a background job pipeline (plan → parallel subagents → synthesis → citation pass) with state persisted to SQLite (via Prisma or Drizzle) so runs survive navigation and can run 5–30 min. SSE (Server-Sent Events) streams live progress to the UI. Provider-agnostic LLM layer (any OpenAI-compatible endpoint).

**Tech Stack:** Next.js 15 · TypeScript · Tailwind + shadcn/ui · Drizzle + SQLite (upgradeable to Postgres) · httpx-equivalent fetch layer · DuckDuckGo search (keyless, upgradeable to Tavily/Bing) · uv-free (pure Node)

---

## Why this design (research findings, Sept 2026)

The bar set by existing tools — ALL of these are table stakes:

1. **Plan-first** (ChatGPT, Gemini): user reviews/edits the research plan before execution starts
2. **Live progress + interrupt** (all): stream every step; pause/stop mid-run
3. **Parallel subagents** (Claude Research): lead agent + 3–5 workers with separate context windows — Anthropic reports 90.2% quality gain and up to 90% time cut
4. **Inline citations, click-through** (all): numbered claims → live source URLs
5. **Background runs** (all): 5–45 min runs; notification on completion
6. **Export/share** (Perplexity): markdown/PDF export, shareable report page
7. **Conflict flagging** (Perplexity, Consensus): report where sources disagree

Our differentiators vs premium ChatGPT/Claude:
- **No usage limits** (self-hosted, your API key)
- **Radical transparency** — full step log, every search query, every fetched page inspectable
- **Local + web sources** — research across your files/docs AND the web (v2)
- **Developer outputs** — clean markdown + structured JSON per report
- **Source scoping** — allowlist domains per run (ChatGPT has this; we keep it)

---

## Repo decision

Rename/replace the current `scout` repo (github.com/shahadathhs/scout — currently CLI scaffold). Options:
- **(A) Wipe scout repo, rebuild as Next.js app there** — keeps the name, one repo
- **(B) New repo `scout` archived, new name** — e.g. keep CLI as `scout-cli`

Recommendation: **(A)** — the CLI code (llm.py/tools.py/agent.py) ports conceptually to TS; the repo has no users.

---

## Phase 0 — Foundation (Day 1)

### Task 0.1: Scaffold Next.js app
- `npx create-next-app@latest scout --typescript --tailwind --app --src-dir`
- Add shadcn/ui (`npx shadcn@latest init` + button, card, dialog, textarea, badge, scroll-area, sheet, tabs, toast)
- Add drizzle-orm + better-sqlite3 + zod
- Commit.

### Task 0.2: Data model (Drizzle schema)
`src/db/schema.ts`:
```
research_runs   id (uuid pk) · question · status (planning|awaiting_approval|running|paused|done|failed) · plan (json) · report (md) · report_json (json) · model · created_at · finished_at · error
plan_steps      id · run_id fk · order · description · status (pending|active|done|failed) · searches json
subagent_tasks  id · run_id fk · plan_step fk nullable · objective · status · findings (md) · sources json · tokens_used
sources         id · run_id fk · url · title · snippet · first_seen_step · credibility_hint
run_events      id · run_id fk · ts · type (plan|search|read|think|subagent_start|subagent_done|synthesis|citation|error|interrupt) · payload json   ← drives the live UI
```
- Push schema, verify with a seed insert. Commit.

### Task 0.3: LLM provider layer (port of scout_cli/llm.py → TS)
`src/lib/llm/client.ts` — OpenAI-compatible chat + tool-calling. Env: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (+ separate `FAST_MODEL` for cheap calls: titles, routing). Commit.

### Task 0.4: Tool layer (port of tools.py → TS)
`src/lib/tools/` — `webSearch.ts` (DuckDuckGo via ddgs-equivalent npm pkg or direct fetch), `webRead.ts` (fetch + readability extraction + per-page char budget), tool schemas. Unit-testable pure functions. Commit.

---

## Phase 1 — The Research Pipeline (the core, Week 1)

Runs **in-process as an async job** (no queue infra yet) with every action logged to `run_events`.

### Task 1.1: Planner
- POST `/api/runs` { question, model?, scope? } → creates run, calls LLM to produce structured plan: `{ sub_questions: [{ objective, search_hints }], synthesis_outline }`
- Status → `awaiting_approval`. Commit.

### Task 1.2: Plan review UI
- Run page shows editable plan (add/remove/reorder sub-questions) + **Approve & Run** / **Edit plan** buttons — the ChatGPT/Gemini plan-first moment. Commit.

### Task 1.3: Subagent executor
- On approval → status `running`. For each sub-question (max parallelism 3): fresh agent loop with own message history, tools webSearch/webRead, step budget ~8, writes findings + sources back to DB
- Every tool call logged as run_events. Commit.

### Task 1.4: Synthesizer + citation pass
- Lead-agent prompt: all subagent findings + sources table → structured markdown report; every claim must cite `[n]`
- Second pass (cheap model): verify each `[n]` maps to a real collected source; flag unsupported claims; detect contradictions (two sources disagree → "Conflicting evidence" callout). Commit.

### Task 1.5: SSE live progress
- GET `/api/runs/:id/events` — SSE stream from run_events (poll DB table every 500ms, simplest reliable approach)
- Run page: activity feed (searches with query text, pages being read, subagent status chips), interrupt button → status `paused`. Commit.

---

## Phase 2 — The Report Experience (Week 2)

### Task 2.1: Report renderer
- Markdown → React with numbered citation superscripts; hover a citation → source card (title, URL, snippet); click → opens source
- Sources sidebar with favicon, read-order, "most cited" sort. Commit.

### Task 2.2: Report actions
- Copy as markdown · download .md · download JSON (report + plan + steps + sources — the full reproducible artifact) · print-to-PDF stylesheet. Commit.

### Task 2.3: Run history + share
- Home: list of runs with status badges; run page deep-linkable (shareable if `PUBLIC_SHARE=true`)
- Delete run (cascades). Commit.

---

## Phase 3 — Trust & Control (Week 3)

- Task 3.1: **Full transparency view** — expandable panel showing every search query, every fetched page (cached text), every LLM thought, token counts per phase
- Task 3.2: **Source scoping** — allowlist/denylist domains per run, "academic only" preset (arxiv.org, *.edu, scholar)
- Task 3.3: **Follow-up questions** — chat with the report: answers grounded in collected sources only (no new searches by default)
- Task 3.4: **Conflict/consensus UI** — callout boxes where sources disagree; optional consensus meter for yes/no questions

## Phase 4 — Power features (later)

- Local file research (upload PDFs/MD → chunked, searched by subagents alongside web)
- Tavily/Exa search backend option (env-flagged)
- Multiple models per role (planner = smart model, subagents = fast model, configurable)
- Report templates (competitive analysis, literature scan, due diligence)
- Docker image + one-command self-host deploy

---

## Validation

- Per task: `pnpm build && pnpm lint` clean; manual happy-path via `pnpm dev`
- Phase 1 exit: full run on "Compare Postgres vs SQLite for a multi-tenant SaaS" produces an 800+ word report with ≥6 cited sources, live-streamed, interruptible
- Phase 2 exit: report readable end-to-end, export works, shareable link works
- E2E test script (Playwright, Phase 2+): submit question → approve plan → wait for done → assert citations render

## Risks / Open Questions

- **LLM key**: current GLM key is out of balance — needs a working key (z.ai recharge, OpenRouter, or Groq free tier) before Phase 1 can run. Phase 0 is key-independent.
- DuckDuckGo rate-limiting under parallel subagents → mitigate with backoff; Tavily fallback
- In-process job runner is fine for single-user self-host; if multi-user later → move runs to a worker (BullMQ) — design keeps pipeline code runner-agnostic
- SQLite check: concurrent SSE poll + job writes is fine at this scale; Postgres swap is a config change

## What NOT to build (YAGNI guardrails)

- No auth/multi-tenant in v1 (self-hosted single user)
- No streaming LLM tokens to UI (reports are synthesized once; activity feed is the "live" feel)
- No browser-use agent (webSearch + webRead only; no JS-rendered page handling in v1)
- No k8s/queue/microservices — one Next.js app, one SQLite file
