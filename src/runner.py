"""Orchestrator — runs N prompts × M providers × R repeats (parallel per provider)."""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass

import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from src.extraction.analyzer import analyze_response
from src.extraction.normalizer import normalize_citations
from src.providers.base import BaseProvider
from src.providers.gemini_provider import GeminiProvider
from src.providers.openai_provider import OpenAIProvider
from src.providers.perplexity_provider import PerplexityProvider
from src.storage.db import (
    create_run, finish_run, init_db,
    store_analysis, store_citations, store_response,
)

console = Console()

PROVIDER_CLASSES: dict[str, type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "perplexity": PerplexityProvider,
}


def _load_config() -> dict:
    """Load config.yaml."""
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def _create_provider(name: str) -> BaseProvider:
    """Create a provider instance using the model from config.yaml."""
    cfg = _load_config()
    provider_cfg = cfg.get("providers", {}).get(name, {})
    model = provider_cfg.get("model")
    cls = PROVIDER_CLASSES[name]
    return cls(model=model) if model else cls()


@dataclass
class Prompt:
    id: str
    text: str
    category: str
    persona: str
    product: str | None
    intent: str


def load_prompts(path: str = "prompts/seed_prompts.yaml", category: str | None = None) -> list[Prompt]:
    """Load prompts from YAML, optionally filtered by category."""
    with open(path) as f:
        data = yaml.safe_load(f)

    prompts = []
    for p in data["prompts"]:
        prompt = Prompt(
            id=p["id"],
            text=p["text"],
            category=p["category"],
            persona=p["persona"],
            product=p.get("product"),
            intent=p["intent"],
        )
        if category is None or prompt.category == category:
            prompts.append(prompt)

    return prompts


async def _process_single(
    run_id: str,
    prompt: Prompt,
    provider_name: str,
    repeat: int,
    analyze: bool,
    semaphore: asyncio.Semaphore,
) -> tuple[bool, str | None]:
    """Process a single prompt/provider/repeat. Returns (success, error_msg)."""
    async with semaphore:
        provider = _create_provider(provider_name)
        try:
            # Add small jitter to avoid bursts to the same provider
            jitter = random.uniform(0.2, 1.0)
            await asyncio.sleep(jitter)

            resp = await provider.query(prompt.text)

            # Store response
            response_id = store_response(run_id, prompt.id, prompt.text, resp, repeat)

            # Normalize and store citations
            normalized = normalize_citations(resp)
            if normalized:
                store_citations(response_id, normalized)

            # Run brand extraction
            if analyze and resp.raw_text:
                try:
                    domains = [c.domain for c in normalized]
                    analysis = await analyze_response(resp.raw_text, domains)
                    store_analysis(response_id, analysis)
                except Exception as e:
                    return True, f"[yellow]Analysis warning {prompt.id}/{provider_name}/r{repeat}: {e}[/yellow]"

            return True, None

        except Exception as e:
            return False, f"[red]Error: {prompt.id}/{provider_name}/r{repeat}: {e}[/red]"


async def run_batch(
    prompts: list[Prompt],
    providers: list[str],
    repeats: int = 1,
    jitter_min: float = 1.0,
    jitter_max: float = 3.0,
    analyze: bool = True,
    concurrency: int = 5,
) -> str:
    """Run a full batch with parallel execution. Returns run_id."""
    init_db()

    active_providers = [p for p in providers if p in PROVIDER_CLASSES]
    if not active_providers:
        raise ValueError(f"No valid providers: {providers}")

    total_tasks = len(prompts) * len(active_providers) * repeats
    run_id = create_run(len(prompts), len(active_providers), repeats)

    console.print(f"\n[bold cyan]Run {run_id}[/bold cyan] — {len(prompts)} prompts × {len(active_providers)} providers × {repeats} repeats = {total_tasks} queries (concurrency={concurrency})")

    # Per-provider semaphores to respect rate limits
    provider_semaphores = {p: asyncio.Semaphore(concurrency) for p in active_providers}

    completed = 0
    errors = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Running queries...", total=total_tasks)

        # Build all tasks
        async def run_and_track(prompt, provider_name, repeat):
            nonlocal completed, errors
            result = await _process_single(
                run_id, prompt, provider_name, repeat, analyze,
                provider_semaphores[provider_name],
            )
            success, msg = result
            if success:
                completed += 1
            else:
                errors += 1
            if msg:
                console.print(f"  {msg}")
            progress.advance(task)

        # Launch all queries as concurrent tasks
        tasks = []
        for prompt in prompts:
            for provider_name in active_providers:
                for repeat in range(1, repeats + 1):
                    tasks.append(run_and_track(prompt, provider_name, repeat))

        progress.update(task, description=f"Running {total_tasks} queries in parallel...")
        await asyncio.gather(*tasks)

    finish_run(run_id)
    console.print(f"\n[bold green]Run {run_id} complete.[/bold green] {completed} succeeded, {errors} failed.")
    return run_id
