"""Cost tracking — calculate API costs from token usage."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "coke_geo.db"

# Pricing per 1M tokens (Feb 2026)
PRICING = {
    "gpt-5": {"input": 2.00, "output": 8.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gemini-3-flash-preview": {"input": 0.10, "output": 0.40},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "sonar": {"input": 1.00, "output": 1.00},
    "sonar-pro": {"input": 3.00, "output": 15.00},
}

# Per-request fees
REQUEST_FEES = {
    "sonar": 5.00 / 1000,  # $5 per 1000 requests
    "sonar-pro": 5.00 / 1000,
}


@dataclass
class ProviderCost:
    provider: str
    model: str
    queries: int
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    request_cost: float
    total_cost: float


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def compute_costs(run_id: str | None = None) -> list[ProviderCost]:
    """Compute costs per provider/model."""
    conn = _get_conn()
    where = f"WHERE run_id = '{run_id}'" if run_id else ""

    rows = conn.execute(f"""
        SELECT provider, model, COUNT(*) as queries,
               SUM(input_tokens) as total_input,
               SUM(output_tokens) as total_output
        FROM responses {where}
        GROUP BY provider, model
    """).fetchall()

    conn.close()

    costs = []
    for r in rows:
        model = r["model"]
        pricing = PRICING.get(model, {"input": 0, "output": 0})

        input_cost = (r["total_input"] or 0) / 1_000_000 * pricing["input"]
        output_cost = (r["total_output"] or 0) / 1_000_000 * pricing["output"]
        request_cost = r["queries"] * REQUEST_FEES.get(model, 0)

        costs.append(ProviderCost(
            provider=r["provider"],
            model=model,
            queries=r["queries"],
            input_tokens=r["total_input"] or 0,
            output_tokens=r["total_output"] or 0,
            input_cost=round(input_cost, 4),
            output_cost=round(output_cost, 4),
            request_cost=round(request_cost, 4),
            total_cost=round(input_cost + output_cost + request_cost, 4),
        ))

    # Add extraction cost estimate (GPT-4o-mini for analysis)
    # Rough estimate: ~500 tokens input + ~200 tokens output per analysis
    total_analyses = sum(r["queries"] for r in rows)
    if total_analyses > 0:
        ext_pricing = PRICING["gpt-4o-mini"]
        ext_input = total_analyses * 500
        ext_output = total_analyses * 200
        ext_input_cost = ext_input / 1_000_000 * ext_pricing["input"]
        ext_output_cost = ext_output / 1_000_000 * ext_pricing["output"]
        costs.append(ProviderCost(
            provider="extraction",
            model="gpt-4o-mini",
            queries=total_analyses,
            input_tokens=ext_input,
            output_tokens=ext_output,
            input_cost=round(ext_input_cost, 4),
            output_cost=round(ext_output_cost, 4),
            request_cost=0,
            total_cost=round(ext_input_cost + ext_output_cost, 4),
        ))

    return costs
