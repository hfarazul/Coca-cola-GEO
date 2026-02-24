"""CSV export for GEO data."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "coke_geo.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def export_run(run_id: str | None, output_path: str):
    """Export run data to CSV."""
    conn = _get_conn()
    where = f"WHERE r.run_id = '{run_id}'" if run_id else ""

    rows = conn.execute(f"""
        SELECT r.run_id, r.prompt_id, r.prompt_text, r.provider, r.model,
               r.latency_ms, r.input_tokens, r.output_tokens, r.repeat_num,
               a.coke_brands_found, a.competitor_brands_found, a.response_type,
               a.coke_is_primary_recommendation,
               (SELECT COUNT(*) FROM citations c WHERE c.response_id = r.response_id) as citation_count,
               (SELECT COUNT(*) FROM citations c WHERE c.response_id = r.response_id AND c.is_coke_domain = 1) as coke_citation_count
        FROM responses r
        LEFT JOIN analyses a ON r.response_id = a.response_id
        {where}
        ORDER BY r.prompt_id, r.provider, r.repeat_num
    """).fetchall()

    conn.close()

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "run_id", "prompt_id", "prompt_text", "provider", "model",
            "latency_ms", "input_tokens", "output_tokens", "repeat_num",
            "coke_brands_found", "competitor_brands_found", "response_type",
            "coke_is_primary_recommendation", "citation_count", "coke_citation_count",
        ])
        for r in rows:
            writer.writerow([dict(r)[k] for k in [
                "run_id", "prompt_id", "prompt_text", "provider", "model",
                "latency_ms", "input_tokens", "output_tokens", "repeat_num",
                "coke_brands_found", "competitor_brands_found", "response_type",
                "coke_is_primary_recommendation", "citation_count", "coke_citation_count",
            ]])

    return len(rows)
