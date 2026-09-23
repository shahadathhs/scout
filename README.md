# scout

A CLI AI research agent. Ask a question — scout plans, searches the web, reads
sources, and answers with citations you can verify.

```bash
scout "what HTTP status code should a successful DELETE return?"
```

## Goal

Build a research agent that is **trustworthy by construction**: every claim in
its answer traces back to a URL the agent actually read. Not a chatbot with a
search box — an agent loop with a step budget, source tracking, and honest
failure ("I couldn't verify this") instead of confident hallucination.

Design principles:

1. **Citations or it didn't happen** — answers cite `[n]`-numbered sources;
   the source table shows exactly which pages were read
2. **Watch it think** — every tool call (search, read) streams to the terminal
   live, so you see the reasoning path, not just the verdict
3. **Provider-agnostic** — any OpenAI-compatible endpoint (GLM/z.ai default,
   OpenRouter, Groq, OpenAI, local Ollama) via env vars; no vendor lock
4. **Keyless search** — DuckDuckGo results + raw page fetches; no search API
  key required to run it
5. **Bounded** — a step budget stops runaway loops; the agent reports what it
  found even when it runs out

## Architecture

```
question ──▶ agent loop (LLM + tools, max N steps)
                │
                ├── web_search   DuckDuckGo → titles, URLs, snippets
                ├── web_read     fetch page → readable text (budgeted chars)
                │
                └── answer       markdown + [n] citations + source table
```

- Python 3.12 · uv · httpx · ddgs · typer · rich
- LLM: OpenAI-compatible chat completions with tool calling

## Status

🚧 Building — see [TODO](#) for the roadmap.

## License

MIT
