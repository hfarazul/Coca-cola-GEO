"""Statistical aggregation — visibility scores, SOV, sentiment across runs."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "coke_geo.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@dataclass
class EngineOverview:
    """Aggregated stats for a single provider/engine."""
    provider: str
    total_responses: int
    visibility_score: float  # % of responses where any Coke brand is mentioned
    share_of_voice: float  # Coke mentions / total brand mentions
    recommendation_rate: float  # % where Coke is primary recommendation
    avg_position: float | None  # Average position of first Coke brand mention
    sentiment_dist: dict[str, int] = field(default_factory=dict)
    citation_rate: float = 0.0  # % of responses with any citations
    coke_citation_rate: float = 0.0  # % of citations from Coke domains
    avg_latency_ms: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


@dataclass
class PromptStats:
    """Per-prompt statistics across providers."""
    prompt_id: str
    prompt_text: str
    category: str | None
    by_provider: dict[str, dict] = field(default_factory=dict)


@dataclass
class CompetitorInfo:
    """Competitor brand summary."""
    brand: str
    mention_count: int
    avg_position: float
    sentiment_mode: str
    recommendation_count: int


def compute_engine_overview(run_id: str | None = None) -> list[EngineOverview]:
    """Compute per-engine aggregated stats."""
    conn = _get_conn()

    where = f"WHERE r.run_id = '{run_id}'" if run_id else ""

    # Get responses grouped by provider
    providers = conn.execute(
        f"SELECT DISTINCT provider FROM responses r {where}"
    ).fetchall()

    overviews = []

    for prow in providers:
        prov = prow["provider"]
        prov_where = f"r.provider = '{prov}'" + (f" AND r.run_id = '{run_id}'" if run_id else "")

        # Total responses
        total = conn.execute(f"SELECT COUNT(*) FROM responses r WHERE {prov_where}").fetchone()[0]

        # Visibility: % of responses where analysis found any Coke brand
        visible = conn.execute(f"""
            SELECT COUNT(*) FROM analyses a
            JOIN responses r ON a.response_id = r.response_id
            WHERE {prov_where}
            AND a.coke_brands_found != '[]'
        """).fetchone()[0]

        # Recommendation rate
        recommended = conn.execute(f"""
            SELECT COUNT(*) FROM analyses a
            JOIN responses r ON a.response_id = r.response_id
            WHERE {prov_where}
            AND a.coke_is_primary_recommendation = 1
        """).fetchone()[0]

        # Share of voice: Coke mentions / total mentions
        total_mentions = conn.execute(f"""
            SELECT COUNT(*) FROM brand_mentions bm
            JOIN responses r ON bm.response_id = r.response_id
            WHERE {prov_where}
        """).fetchone()[0]

        coke_mentions = conn.execute(f"""
            SELECT COUNT(*) FROM brand_mentions bm
            JOIN responses r ON bm.response_id = r.response_id
            WHERE {prov_where} AND bm.is_coke_brand = 1
        """).fetchone()[0]

        # Average position of Coke brands
        avg_pos_row = conn.execute(f"""
            SELECT AVG(bm.position) FROM brand_mentions bm
            JOIN responses r ON bm.response_id = r.response_id
            WHERE {prov_where} AND bm.is_coke_brand = 1
        """).fetchone()
        avg_pos = round(avg_pos_row[0], 1) if avg_pos_row[0] else None

        # Sentiment distribution for Coke brands
        sent_rows = conn.execute(f"""
            SELECT bm.sentiment, COUNT(*) as cnt FROM brand_mentions bm
            JOIN responses r ON bm.response_id = r.response_id
            WHERE {prov_where} AND bm.is_coke_brand = 1
            GROUP BY bm.sentiment
        """).fetchall()
        sentiment_dist = {row["sentiment"]: row["cnt"] for row in sent_rows}

        # Citation rate
        responses_with_citations = conn.execute(f"""
            SELECT COUNT(DISTINCT c.response_id) FROM citations c
            JOIN responses r ON c.response_id = r.response_id
            WHERE {prov_where}
        """).fetchone()[0]

        # Coke domain citation rate
        coke_citations = conn.execute(f"""
            SELECT COUNT(*) FROM citations c
            JOIN responses r ON c.response_id = r.response_id
            WHERE {prov_where} AND c.is_coke_domain = 1
        """).fetchone()[0]
        total_citations = conn.execute(f"""
            SELECT COUNT(*) FROM citations c
            JOIN responses r ON c.response_id = r.response_id
            WHERE {prov_where}
        """).fetchone()[0]

        # Latency and tokens
        perf = conn.execute(f"""
            SELECT AVG(r.latency_ms), SUM(r.input_tokens), SUM(r.output_tokens)
            FROM responses r WHERE {prov_where}
        """).fetchone()

        overviews.append(EngineOverview(
            provider=prov,
            total_responses=total,
            visibility_score=round(visible / total * 100, 1) if total else 0,
            share_of_voice=round(coke_mentions / total_mentions * 100, 1) if total_mentions else 0,
            recommendation_rate=round(recommended / total * 100, 1) if total else 0,
            avg_position=avg_pos,
            sentiment_dist=sentiment_dist,
            citation_rate=round(responses_with_citations / total * 100, 1) if total else 0,
            coke_citation_rate=round(coke_citations / total_citations * 100, 1) if total_citations else 0,
            avg_latency_ms=int(perf[0]) if perf[0] else 0,
            total_input_tokens=int(perf[1]) if perf[1] else 0,
            total_output_tokens=int(perf[2]) if perf[2] else 0,
        ))

    conn.close()
    return overviews


def get_top_competitors(run_id: str | None = None, limit: int = 10) -> list[CompetitorInfo]:
    """Get most mentioned competitor brands."""
    conn = _get_conn()
    where = f"JOIN responses r ON bm.response_id = r.response_id WHERE r.run_id = '{run_id}' AND" if run_id else "WHERE"

    rows = conn.execute(f"""
        SELECT bm.brand, COUNT(*) as cnt, AVG(bm.position) as avg_pos,
               bm.sentiment, SUM(bm.is_recommended) as rec_cnt
        FROM brand_mentions bm
        {where} bm.is_coke_brand = 0
        GROUP BY bm.brand
        ORDER BY cnt DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()
    return [
        CompetitorInfo(
            brand=r["brand"],
            mention_count=r["cnt"],
            avg_position=round(r["avg_pos"], 1) if r["avg_pos"] else 0,
            sentiment_mode=r["sentiment"] or "neutral",
            recommendation_count=r["rec_cnt"] or 0,
        )
        for r in rows
    ]


def get_top_cited_domains(run_id: str | None = None, limit: int = 10) -> list[tuple[str, int]]:
    """Get most frequently cited domains."""
    conn = _get_conn()
    where = f"JOIN responses r ON c.response_id = r.response_id WHERE r.run_id = '{run_id}'" if run_id else ""

    rows = conn.execute(f"""
        SELECT c.domain, COUNT(*) as cnt FROM citations c
        {where}
        GROUP BY c.domain
        ORDER BY cnt DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()
    return [(r["domain"], r["cnt"]) for r in rows]


def get_weakest_prompts(run_id: str | None = None, limit: int = 5) -> list[dict]:
    """Get prompts where Coke visibility is lowest."""
    conn = _get_conn()
    where = f"AND r.run_id = '{run_id}'" if run_id else ""

    rows = conn.execute(f"""
        SELECT r.prompt_id, r.prompt_text,
               COUNT(*) as total_responses,
               SUM(CASE WHEN a.coke_brands_found != '[]' THEN 1 ELSE 0 END) as visible,
               SUM(a.coke_is_primary_recommendation) as recommended
        FROM responses r
        JOIN analyses a ON r.response_id = a.response_id
        {f"WHERE r.run_id = '{run_id}'" if run_id else ""}
        GROUP BY r.prompt_id
        ORDER BY (CAST(visible AS FLOAT) / total_responses) ASC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()
    return [
        {
            "prompt_id": r["prompt_id"],
            "prompt_text": r["prompt_text"],
            "visibility": round(r["visible"] / r["total_responses"] * 100) if r["total_responses"] else 0,
            "recommendation": round(r["recommended"] / r["total_responses"] * 100) if r["total_responses"] else 0,
        }
        for r in rows
    ]
