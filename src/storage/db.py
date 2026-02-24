"""SQLite storage layer for GEO tracker."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from src.extraction.analyzer import ResponseAnalysis
from src.extraction.normalizer import NormalizedCitation
from src.providers.base import ProviderResponse

DB_PATH = Path(__file__).parent.parent.parent / "data" / "coke_geo.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            prompt_count INTEGER,
            provider_count INTEGER,
            repeats INTEGER,
            status TEXT DEFAULT 'running'
        );

        CREATE TABLE IF NOT EXISTS responses (
            response_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL REFERENCES runs(run_id),
            prompt_id TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            raw_response TEXT,
            latency_ms INTEGER,
            input_tokens INTEGER,
            output_tokens INTEGER,
            repeat_num INTEGER DEFAULT 1,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS citations (
            citation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT NOT NULL REFERENCES responses(response_id),
            url TEXT NOT NULL,
            domain TEXT,
            title TEXT,
            cited_text TEXT,
            char_offset INTEGER,
            confidence REAL DEFAULT 1.0,
            is_coke_domain INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS brand_mentions (
            mention_id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT NOT NULL REFERENCES responses(response_id),
            brand TEXT NOT NULL,
            position INTEGER,
            sentiment TEXT,
            is_recommended INTEGER DEFAULT 0,
            context TEXT,
            is_coke_brand INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS analyses (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT NOT NULL REFERENCES responses(response_id),
            coke_brands_found TEXT,
            competitor_brands_found TEXT,
            response_type TEXT,
            coke_is_primary_recommendation INTEGER DEFAULT 0,
            coke_domains_cited TEXT
        );
    """)
    conn.commit()
    conn.close()


def create_run(prompt_count: int, provider_count: int, repeats: int) -> str:
    """Create a new run and return its ID."""
    run_id = str(uuid.uuid4())[:8]
    conn = _get_conn()
    conn.execute(
        "INSERT INTO runs (run_id, started_at, prompt_count, provider_count, repeats) VALUES (?, ?, ?, ?, ?)",
        (run_id, datetime.utcnow().isoformat(), prompt_count, provider_count, repeats),
    )
    conn.commit()
    conn.close()
    return run_id


def finish_run(run_id: str):
    """Mark a run as finished."""
    conn = _get_conn()
    conn.execute(
        "UPDATE runs SET finished_at = ?, status = 'completed' WHERE run_id = ?",
        (datetime.utcnow().isoformat(), run_id),
    )
    conn.commit()
    conn.close()


def store_response(
    run_id: str,
    prompt_id: str,
    prompt_text: str,
    response: ProviderResponse,
    repeat_num: int = 1,
) -> str:
    """Store a provider response and return response_id."""
    response_id = str(uuid.uuid4())[:12]
    conn = _get_conn()
    conn.execute(
        """INSERT INTO responses
           (response_id, run_id, prompt_id, prompt_text, provider, model,
            raw_text, raw_response, latency_ms, input_tokens, output_tokens,
            repeat_num, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            response_id, run_id, prompt_id, prompt_text,
            response.provider, response.model, response.raw_text,
            json.dumps(response.raw_response, default=str),
            response.latency_ms, response.input_tokens, response.output_tokens,
            repeat_num, response.timestamp.isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return response_id


def store_citations(response_id: str, citations: list[NormalizedCitation]):
    """Store normalized citations for a response."""
    conn = _get_conn()
    for c in citations:
        conn.execute(
            """INSERT INTO citations
               (response_id, url, domain, title, cited_text, char_offset, confidence, is_coke_domain)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (response_id, c.url, c.domain, c.title, c.cited_text, c.char_offset, c.confidence, int(c.is_coke_domain)),
        )
    conn.commit()
    conn.close()


def store_analysis(response_id: str, analysis: ResponseAnalysis):
    """Store brand extraction analysis for a response."""
    conn = _get_conn()

    # Store analysis summary
    conn.execute(
        """INSERT INTO analyses
           (response_id, coke_brands_found, competitor_brands_found, response_type,
            coke_is_primary_recommendation, coke_domains_cited)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            response_id,
            json.dumps(analysis.coke_brands_found),
            json.dumps(analysis.competitor_brands_found),
            analysis.response_type,
            int(analysis.coke_is_primary_recommendation),
            json.dumps(analysis.coke_domains_cited),
        ),
    )

    # Store individual brand mentions
    coke_canonical = set()
    for brands in [analysis.coke_brands_found]:
        coke_canonical.update(brands)

    for m in analysis.all_mentions:
        # Determine if this is a coke brand
        brand_lower = m.brand.lower()
        is_coke = any(
            brand_lower in [alias.lower() for alias in aliases] or brand_lower == key
            for key, aliases in {
                "coca_cola": ["coca-cola", "coca cola", "coke", "diet coke", "coke zero"],
                "thums_up": ["thums up", "thumbs up"],
                "sprite": ["sprite"], "fanta": ["fanta"], "limca": ["limca"],
                "maaza": ["maaza"], "minute_maid": ["minute maid"],
            }.items()
        ) or brand_lower.replace(" ", "_") in coke_canonical

        conn.execute(
            """INSERT INTO brand_mentions
               (response_id, brand, position, sentiment, is_recommended, context, is_coke_brand)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (response_id, m.brand, m.position, m.sentiment.value, int(m.is_recommended), m.context, int(is_coke)),
        )

    conn.commit()
    conn.close()


def get_db_stats() -> dict:
    """Get summary stats from the database."""
    conn = _get_conn()
    stats = {}
    stats["runs"] = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    stats["responses"] = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
    stats["citations"] = conn.execute("SELECT COUNT(*) FROM citations").fetchone()[0]
    stats["brand_mentions"] = conn.execute("SELECT COUNT(*) FROM brand_mentions").fetchone()[0]
    stats["analyses"] = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]

    # Per-provider counts
    rows = conn.execute("SELECT provider, COUNT(*) as cnt FROM responses GROUP BY provider").fetchall()
    stats["by_provider"] = {r["provider"]: r["cnt"] for r in rows}

    # Latest run
    row = conn.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT 1").fetchone()
    if row:
        stats["latest_run"] = dict(row)

    conn.close()
    return stats


def get_run_responses(run_id: str) -> list[dict]:
    """Get all responses for a run."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM responses WHERE run_id = ? ORDER BY prompt_id, provider, repeat_num",
        (run_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_run_analyses(run_id: str) -> list[dict]:
    """Get all analyses for a run with their response data."""
    conn = _get_conn()
    rows = conn.execute(
        """SELECT a.*, r.prompt_id, r.prompt_text, r.provider, r.model, r.repeat_num
           FROM analyses a
           JOIN responses r ON a.response_id = r.response_id
           WHERE r.run_id = ?
           ORDER BY r.prompt_id, r.provider, r.repeat_num""",
        (run_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
