"""Agent tools: web search (DuckDuckGo) and page reading (fetch + extract)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import httpx

MAX_PAGE_CHARS = 12_000  # per-page budget fed to the model

# Tools exposed to the LLM (OpenAI function schemas)
TOOL_SPECS = [
    {
        "name": "web_search",
        "description": (
            "Search the web. Returns a list of results with title, URL, and "
            "snippet. Use for finding sources; follow up with web_read on the "
            "most promising URLs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {
                    "type": "integer",
                    "description": "Number of results (default 5, max 10)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "web_read",
        "description": (
            "Fetch a web page and return its readable text (markdown-ish). "
            "Use after web_search to get actual content from a URL."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to read"},
            },
            "required": ["url"],
        },
    },
]


@dataclass
class Source:
    """A source the agent actually used — for citations."""

    url: str
    title: str
    snippet: str = ""
    quote: str = ""  # key claim extracted from this source


@dataclass
class ToolResult:
    ok: bool
    output: str
    source: Source | None = None


@dataclass
class ToolStats:
    calls: int = 0
    searches: int = 0
    reads: int = 0
    failed_reads: int = 0


def html_to_text(html: str) -> str:
    """Crude but effective HTML → text extraction."""
    html = re.sub(r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>",
                  "", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    import html as html_mod

    text = html_mod.unescape(html)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def web_search(query: str, max_results: int = 5, stats: ToolStats | None = None) -> ToolResult:
    from ddgs import DDGS

    if stats:
        stats.calls += 1
        stats.searches += 1
    max_results = max(1, min(10, max_results))
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(query, max_results=max_results, region="wt-wt", safesearch="off")
            )
    except Exception as e:  # noqa: BLE001
        return ToolResult(ok=False, output=f"Search failed: {e}")
    if not results:
        return ToolResult(ok=False, output=f"No results for: {query}")
    lines = []
    for i, r in enumerate(results, 1):
        title = (r.get("title") or "").strip()
        url = r.get("href") or r.get("url") or ""
        snippet = (r.get("body") or r.get("snippet") or "").strip()
        lines.append(f"[{i}] {title}\n    {url}\n    {snippet[:300]}")
    return ToolResult(ok=True, output="\n".join(lines))


def web_read(url: str, stats: ToolStats | None = None) -> ToolResult:
    if stats:
        stats.calls += 1
        stats.reads += 1
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        with httpx.Client(timeout=20, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
        if resp.status_code != 200:
            if stats:
                stats.failed_reads += 1
            return ToolResult(ok=False, output=f"HTTP {resp.status_code} for {url}")
        ctype = resp.headers.get("content-type", "")
        if "html" in ctype:
            text = html_to_text(resp.text)
        else:
            text = resp.text
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", resp.text[:5000], re.S | re.I)
        if m:
            import html as html_mod

            title = html_mod.unescape(m.group(1)).strip()
        truncated = len(text) > MAX_PAGE_CHARS
        text = text[:MAX_PAGE_CHARS]
        note = f"\n\n[page truncated at {MAX_PAGE_CHARS} chars]" if truncated else ""
        return ToolResult(
            ok=True,
            output=f"TITLE: {title}\nURL: {url}\n\n{text}{note}",
            source=Source(url=url, title=title or url),
        )
    except Exception as e:  # noqa: BLE001
        if stats:
            stats.failed_reads += 1
        return ToolResult(ok=False, output=f"Read failed ({url}): {e}")
