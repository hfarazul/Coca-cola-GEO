"""Coke GEO Tracker — CLI entry point."""

from __future__ import annotations

import asyncio

import yaml
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.providers.openai_provider import OpenAIProvider
from src.providers.gemini_provider import GeminiProvider
from src.providers.perplexity_provider import PerplexityProvider
from src.extraction.normalizer import normalize_citations
from src.extraction.analyzer import analyze_response

load_dotenv()

app = typer.Typer(help="Coca-Cola India GEO Measure Loop")
console = Console()


def _load_config() -> dict:
    """Load config.yaml."""
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def _build_providers() -> dict:
    """Build provider map from config.yaml."""
    cfg = _load_config()
    providers = {}
    provider_cfg = cfg.get("providers", {})

    if provider_cfg.get("openai", {}).get("enabled", False):
        model = provider_cfg["openai"].get("model", "gpt-5.2-chat-latest")
        providers["openai"] = lambda m=model: OpenAIProvider(model=m)

    if provider_cfg.get("gemini", {}).get("enabled", False):
        model = provider_cfg["gemini"].get("model", "gemini-3-flash-preview")
        providers["gemini"] = lambda m=model: GeminiProvider(model=m)

    if provider_cfg.get("perplexity", {}).get("enabled", False):
        model = provider_cfg["perplexity"].get("model", "sonar")
        providers["perplexity"] = lambda m=model: PerplexityProvider(model=m)

    return providers


PROVIDERS = _build_providers()


def _run_async(coro):
    """Run an async function synchronously."""
    return asyncio.run(coro)


@app.command()
def query(
    prompt: str = typer.Argument(..., help="The prompt to send to LLM(s)"),
    provider: str = typer.Option("openai", "--provider", "-p", help="Provider to query (openai, gemini, perplexity, all)"),
    show_citations: bool = typer.Option(False, "--show-citations", "-c", help="Show normalized citation table"),
    analyze: bool = typer.Option(False, "--analyze", "-a", help="Run brand extraction analysis"),
):
    """Query a single prompt against one or all providers."""
    if provider == "all":
        providers_to_run = list(PROVIDERS.keys())
    elif provider in PROVIDERS:
        providers_to_run = [provider]
    else:
        console.print(f"[red]Unknown provider: {provider}[/red]")
        console.print(f"Available: {', '.join(PROVIDERS.keys())}, all")
        raise typer.Exit(1)

    console.print(Panel(f"[bold]{prompt}[/bold]", title="Prompt", border_style="cyan"))

    all_normalized = []

    for pname in providers_to_run:
        p = PROVIDERS[pname]()
        console.print(f"\n[bold blue]Querying {pname}...[/bold blue]")

        try:
            resp = _run_async(p.query(prompt))
        except Exception as e:
            console.print(f"[red]Error from {pname}: {e}[/red]")
            continue

        # Response text (truncated for display)
        display_text = resp.raw_text[:2000]
        if len(resp.raw_text) > 2000:
            display_text += "\n... (truncated)"
        console.print(Panel(display_text, title=f"{pname} — {resp.model}", border_style="green"))

        # Normalize citations
        normalized = normalize_citations(resp)
        all_normalized.extend([(pname, c) for c in normalized])

        # Citations table
        if resp.raw_citations:
            table = Table(title=f"Citations ({len(resp.raw_citations)})")
            table.add_column("#", style="dim", width=3)
            table.add_column("URL", style="cyan", max_width=80)
            table.add_column("Title", max_width=40)

            for i, c in enumerate(resp.raw_citations, 1):
                table.add_row(str(i), c.url, c.title or "—")

            console.print(table)
        else:
            console.print("[dim]No citations returned[/dim]")

        # Stats
        console.print(
            f"  [dim]Latency: {resp.latency_ms}ms | "
            f"Tokens: {resp.input_tokens} in / {resp.output_tokens} out | "
            f"Citations: {len(resp.raw_citations)}[/dim]"
        )

        # Brand extraction analysis
        if analyze and resp.raw_text:
            try:
                domains = [c.domain for _, c in all_normalized if _ == pname]
                analysis = _run_async(analyze_response(resp.raw_text, domains))

                analysis_table = Table(title=f"Brand Analysis — {pname}", border_style="magenta")
                analysis_table.add_column("Brand", style="bold", width=15)
                analysis_table.add_column("Pos", justify="center", width=4)
                analysis_table.add_column("Sentiment", width=10)
                analysis_table.add_column("Recommended?", justify="center", width=12)
                analysis_table.add_column("Context", max_width=50)

                for m in analysis.all_mentions:
                    sent_color = {"positive": "green", "neutral": "yellow", "negative": "red", "mixed": "blue"}
                    color = sent_color.get(m.sentiment.value, "white")
                    analysis_table.add_row(
                        m.brand,
                        str(m.position),
                        f"[{color}]{m.sentiment.value}[/{color}]",
                        "[green]Yes[/green]" if m.is_recommended else "—",
                        m.context,
                    )

                console.print(analysis_table)

                # Summary line
                coke_str = ", ".join(analysis.coke_brands_found) if analysis.coke_brands_found else "none"
                comp_str = ", ".join(analysis.competitor_brands_found) if analysis.competitor_brands_found else "none"
                primary = "[green]Yes[/green]" if analysis.coke_is_primary_recommendation else "[red]No[/red]"

                console.print(f"  Coke brands: [cyan]{coke_str}[/cyan]")
                console.print(f"  Competitors: [yellow]{comp_str}[/yellow]")
                console.print(f"  Response type: {analysis.response_type}")
                console.print(f"  Coke is primary recommendation: {primary}")

            except Exception as e:
                console.print(f"  [red]Analysis error: {e}[/red]")

    # Unified normalized citation table (when --show-citations or multiple providers)
    if show_citations and all_normalized:
        console.print("\n")
        table = Table(title="Normalized Citations (All Providers)", border_style="blue")
        table.add_column("Provider", style="bold", width=12)
        table.add_column("Domain", style="cyan", max_width=30)
        table.add_column("Title", max_width=40)
        table.add_column("Conf.", justify="right", width=6)
        table.add_column("Coke?", justify="center", width=5)

        for pname, c in all_normalized:
            coke_flag = "[green]Yes[/green]" if c.is_coke_domain else "—"
            table.add_row(
                pname,
                c.domain,
                c.title or "—",
                f"{c.confidence:.2f}",
                coke_flag,
            )

        console.print(table)

        # Domain overlap analysis
        domains_by_provider: dict[str, set[str]] = {}
        for pname, c in all_normalized:
            domains_by_provider.setdefault(pname, set()).add(c.domain)

        if len(domains_by_provider) > 1:
            all_domains = [s for s in domains_by_provider.values()]
            shared = set.intersection(*all_domains) if all_domains else set()
            total = set.union(*all_domains) if all_domains else set()
            overlap_pct = (len(shared) / len(total) * 100) if total else 0

            console.print(
                f"\n  [dim]Domain overlap: {len(shared)}/{len(total)} "
                f"({overlap_pct:.0f}%) — shared: {', '.join(shared) if shared else 'none'}[/dim]"
            )


@app.command()
def run(
    category: str = typer.Option(None, "--category", help="Filter prompts by category"),
    provider: str = typer.Option("all", "--provider", "-p", help="Provider(s) to query"),
    repeats: int = typer.Option(1, "--repeats", "-r", help="Number of repeats per prompt/provider"),
    no_analyze: bool = typer.Option(False, "--no-analyze", help="Skip brand extraction analysis"),
    prompts_file: str = typer.Option("prompts/seed_prompts.yaml", "--prompts", help="Path to prompts YAML"),
):
    """Run all prompts across providers with optional repeats."""
    from src.runner import load_prompts, run_batch

    prompts = load_prompts(prompts_file, category=category)
    if not prompts:
        console.print("[red]No prompts found.[/red]")
        raise typer.Exit(1)

    if provider == "all":
        providers = list(PROVIDERS.keys())
    else:
        providers = [p.strip() for p in provider.split(",")]

    console.print(f"[bold]Loaded {len(prompts)} prompts, {len(providers)} providers, {repeats} repeats[/bold]")

    run_id = _run_async(run_batch(prompts, providers, repeats=repeats, analyze=not no_analyze))
    console.print(f"\n[bold cyan]Run ID: {run_id}[/bold cyan] — use this for reports and comparisons")


@app.command()
def report(
    run_id: str = typer.Option(None, "--run", help="Specific run ID (default: all data)"),
    provider: str = typer.Option(None, "--provider", "-p", help="Filter by provider"),
):
    """Generate visibility report from stored data."""
    from src.aggregation.stats import (
        compute_engine_overview,
        get_top_competitors,
        get_top_cited_domains,
        get_weakest_prompts,
    )

    overviews = compute_engine_overview(run_id)
    if provider:
        overviews = [o for o in overviews if o.provider == provider]

    if not overviews:
        console.print("[red]No data found. Run some queries first.[/red]")
        raise typer.Exit(1)

    # Engine overview table
    table = Table(title="Visibility by Engine", border_style="cyan")
    table.add_column("Engine", style="bold", width=12)
    table.add_column("Visibility", justify="right", width=12)
    table.add_column("SOV", justify="right", width=8)
    table.add_column("Rec. Rate", justify="right", width=10)
    table.add_column("Avg Pos", justify="right", width=8)
    table.add_column("Sentiment", width=25)
    table.add_column("Cite Rate", justify="right", width=10)

    for o in overviews:
        sent_str = ", ".join(f"{k}: {v}" for k, v in o.sentiment_dist.items()) if o.sentiment_dist else "—"
        table.add_row(
            o.provider,
            f"{o.visibility_score}%",
            f"{o.share_of_voice}%",
            f"{o.recommendation_rate}%",
            f"{o.avg_position}" if o.avg_position else "—",
            sent_str,
            f"{o.citation_rate}%",
        )

    console.print(table)

    # Top competitors
    competitors = get_top_competitors(run_id)
    if competitors:
        ctable = Table(title="Top Competitors", border_style="yellow")
        ctable.add_column("Brand", style="bold", width=15)
        ctable.add_column("Mentions", justify="right", width=10)
        ctable.add_column("Avg Pos", justify="right", width=8)
        ctable.add_column("Sentiment", width=10)
        ctable.add_column("Recommended", justify="right", width=12)

        for c in competitors:
            ctable.add_row(c.brand, str(c.mention_count), f"{c.avg_position}", c.sentiment_mode, str(c.recommendation_count))

        console.print(ctable)

    # Top cited domains
    domains = get_top_cited_domains(run_id)
    if domains:
        dtable = Table(title="Top Cited Domains", border_style="green")
        dtable.add_column("Domain", style="cyan", max_width=40)
        dtable.add_column("Citations", justify="right", width=10)

        for domain, cnt in domains:
            dtable.add_row(domain, str(cnt))

        console.print(dtable)

    # Weakest prompts
    weak = get_weakest_prompts(run_id)
    if weak:
        wtable = Table(title="Weakest Prompts (Lowest Coke Visibility)", border_style="red")
        wtable.add_column("ID", style="dim", width=5)
        wtable.add_column("Prompt", max_width=50)
        wtable.add_column("Visibility", justify="right", width=12)
        wtable.add_column("Rec. Rate", justify="right", width=10)

        for w in weak:
            wtable.add_row(w["prompt_id"], w["prompt_text"], f"{w['visibility']}%", f"{w['recommendation']}%")

        console.print(wtable)


@app.command("db-stats")
def db_stats():
    """Show database statistics."""
    from src.storage.db import get_db_stats, init_db

    init_db()
    stats = get_db_stats()

    table = Table(title="Database Stats", border_style="cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Count", justify="right")

    table.add_row("Runs", str(stats["runs"]))
    table.add_row("Responses", str(stats["responses"]))
    table.add_row("Citations", str(stats["citations"]))
    table.add_row("Brand Mentions", str(stats["brand_mentions"]))
    table.add_row("Analyses", str(stats["analyses"]))

    console.print(table)

    if stats.get("by_provider"):
        ptable = Table(title="Responses by Provider", border_style="green")
        ptable.add_column("Provider", style="bold")
        ptable.add_column("Count", justify="right")
        for prov, cnt in stats["by_provider"].items():
            ptable.add_row(prov, str(cnt))
        console.print(ptable)

    if stats.get("latest_run"):
        lr = stats["latest_run"]
        console.print(f"\n  [dim]Latest run: {lr['run_id']} ({lr['status']}) — {lr['started_at']}[/dim]")


@app.command()
def costs(
    run_id: str = typer.Option(None, "--run", help="Specific run ID (default: all data)"),
):
    """Show cost breakdown by provider."""
    from src.reporting.costs import compute_costs

    cost_data = compute_costs(run_id)
    if not cost_data:
        console.print("[red]No data found.[/red]")
        raise typer.Exit(1)

    table = Table(title="Cost Breakdown", border_style="cyan")
    table.add_column("Provider", style="bold", width=12)
    table.add_column("Model", width=18)
    table.add_column("Queries", justify="right", width=8)
    table.add_column("Tokens Used", justify="right", width=12)
    table.add_column("Cost", justify="right", width=10)

    total_cost = 0
    for c in cost_data:
        tokens_str = f"{c.input_tokens + c.output_tokens:,}"
        table.add_row(c.provider, c.model, str(c.queries), tokens_str, f"${c.total_cost:.4f}")
        total_cost += c.total_cost

    table.add_section()
    table.add_row("[bold]TOTAL[/bold]", "", "", "", f"[bold]${total_cost:.4f}[/bold]")

    console.print(table)


@app.command()
def export(
    output: str = typer.Option("export.csv", "--output", "-o", help="Output CSV path"),
    run_id: str = typer.Option(None, "--run", help="Specific run ID (default: all data)"),
):
    """Export run data to CSV."""
    from src.reporting.csv_export import export_run

    count = export_run(run_id, output)
    console.print(f"[green]Exported {count} rows to {output}[/green]")


if __name__ == "__main__":
    app()
