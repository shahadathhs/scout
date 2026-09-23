# Scout

A self-hosted deep-research platform. Ask a question — Scout drafts a research
plan you approve, runs parallel subagents across the web, and delivers a report
where every claim cites a source you can open.

## What it is

Scout is a Perplexity / ChatGPT deep-research–class tool you run yourself.
Because it's self-hosted with your own API key: no usage limits, no credit
system, and full transparency — every search query, every fetched page, and
every reasoning step is inspectable.

## Features

### Core research pipeline

- **Plan-first workflow** — Scout drafts a research plan (sub-questions +
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

## Tech stack (planned)

Next.js 15 (App Router) · TypeScript · Tailwind + shadcn/ui · SQLite
(Drizzle) · Server-Sent Events · provider-agnostic LLM layer (any
OpenAI-compatible endpoint) · DuckDuckGo search (upgradeable to
Tavily/Bing/Exa)

## Status

🚧 Clean slate — design complete, implementation starting. See the roadmap:
Phase 0 foundation → Phase 1 research pipeline → Phase 2 report experience →
Phase 3 trust & control → Phase 4 power features.

## License

MIT
