"""The agent loop: LLM ↔ tools, with step budget and citation tracking."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from .llm import LLMClient, LLMResponse, Message
from .tools import TOOL_SPECS, ToolStats, ToolResult, web_read, web_search


@dataclass
class Step:
    n: int
    thought: str = ""
    tool: str = ""
    tool_args: dict = field(default_factory=dict)
    result_preview: str = ""
    ok: bool = True


@dataclass
class AgentRun:
    steps: list[Step] = field(default_factory=list)
    sources: list = field(default_factory=list)  # Source objects
    stats: ToolStats = field(default_factory=ToolStats)
    answer: str = ""
    total_tokens: int = 0


SYSTEM_QUICK = """You are a research agent. Answer the user's question using the
web tools available to you.

Rules:
- Search first. Read 2-4 of the most promising results before answering.
- Prefer primary sources (official docs, papers, reputable outlets) over blogs.
- When you have enough evidence, stop and answer. Do not over-search.
- Cite sources inline as [1], [2] matching the numbered sources you used.
- If searches repeatedly fail or the question is unanswerable, say so honestly."""


def _run_tool(name: str, args: dict, stats: ToolStats):
    if name == "web_search":
        return web_search(
            args.get("query", ""), int(args.get("max_results", 5)), stats
        )
    if name == "web_read":
        return web_read(args.get("url", ""), stats)
    return ToolResult(ok=False, output=f"Unknown tool: {name}")


def run_agent(
    client: LLMClient,
    question: str,
    max_steps: int = 8,
    verbose: bool = False,
    on_step=None,
) -> AgentRun:
    run = AgentRun()
    messages = [Message(role="system", content=SYSTEM_QUICK), Message(role="user", content=question)]
    source_urls: dict[str, int] = {}  # url -> citation number

    for n in range(1, max_steps + 1):
        resp: LLMResponse = client.chat(messages, tools=TOOL_SPECS)

        step = Step(n=n, thought=resp.content or "")
        run.total_tokens += (
            resp.usage.get("prompt_tokens", 0) + resp.usage.get("completion_tokens", 0)
        )

        if not resp.tool_calls:
            run.answer = resp.content or ""
            run.steps.append(step)
            if on_step:
                on_step(step)
            return run

        # assistant message with tool calls must be echoed back
        messages.append(
            Message(role="assistant", content=resp.content, tool_calls=resp.tool_calls)
        )

        for tc in resp.tool_calls:
            try:
                args = json.loads(tc.arguments) if tc.arguments.strip() else {}
            except json.JSONDecodeError:
                args = {}
            step.tool, step.tool_args = tc.name, args
            result = _run_tool(tc.name, args, run.stats)

            if result.source and result.source.url not in source_urls:
                source_urls[result.source.url] = len(source_urls) + 1
                result.source.quote = (args.get("query") or "")[:120]
                run.sources.append(result.source)

            step.result_preview = result.output[:200]
            step.ok = result.ok
            messages.append(
                Message(role="tool", content=result.output, tool_call_id=tc.id)
            )

        run.steps.append(step)
        if on_step:
            on_step(step)

    run.answer = (
        "I hit my research step budget before finishing. Here's what I found so far:\n\n"
        + "\n".join(
            f"- step {s.n}: {s.tool} {json.dumps(s.tool_args)} → {'ok' if s.ok else 'FAILED'}"
            for s in run.steps[-4:]
        )
    )
    return run
