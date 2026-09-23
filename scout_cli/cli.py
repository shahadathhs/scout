"""CLI: `research <question>` — watch the agent think, get a cited answer."""

from __future__ import annotations

import json
import time

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .agent import run_agent
from .llm import LLMClient

app = typer.Typer(help="AI research agent with citations.")
console = Console()


@app.command()
def ask(
    question: str = typer.Argument(..., help="The question to research"),
    steps: int = typer.Option(8, "--steps", "-s", help="Max agent steps"),
    model: str = typer.Option(None, "--model", "-m", help="Override model"),
    show_thoughts: bool = typer.Option(True, "--thoughts/--no-thoughts"),
    json_out: bool = typer.Option(False, "--json", help="Dump raw JSON result"),
):
    client = LLMClient(model=model)
    t0 = time.time()

    def on_step(step):
        if not show_thoughts:
            return
        header = f"[bold cyan]step {step.n}[/]"
        if step.tool:
            args_str = json.dumps(step.tool_args)
            status = "[green]ok[/]" if step.ok else "[red]FAILED[/]"
            console.print(
                f"{header} [yellow]{step.tool}[/] {args_str[:120]} → {status}"
            )
        else:
            console.print(f"{header} thinking...")

    console.print(Panel(f"[bold]{question}[/]", title="researching", border_style="blue"))
    run = run_agent(client, question, max_steps=steps, on_step=on_step)

    dt = time.time() - t0
    console.print()
    console.print(Markdown(run.answer or "(no answer produced)"))
    console.print()

    if run.sources:
        table = Table(title="sources", show_lines=False)
        table.add_column("#", style="dim", width=3)
        table.add_column("title", max_width=48)
        table.add_column("url", style="cyan", max_width=60)
        for i, s in enumerate(run.sources, 1):
            table.add_row(str(i), s.title[:48], s.url)
        console.print(table)

    console.print(
        f"[dim]{run.stats.searches} searches · {run.stats.reads} reads "
        f"({run.stats.failed_reads} failed) · {len(run.steps)} steps · "
        f"{run.total_tokens} tokens · {dt:.1f}s · model {client.model}[/]"
    )

    if json_out:
        console.print_json(
            json.dumps(
                {
                    "question": question,
                    "answer": run.answer,
                    "sources": [{"title": s.title, "url": s.url} for s in run.sources],
                    "steps": [
                        {
                            "n": s.n,
                            "tool": s.tool,
                            "args": s.tool_args,
                            "ok": s.ok,
                        }
                        for s in run.steps
                    ],
                }
            )
        )


if __name__ == "__main__":
    app()
