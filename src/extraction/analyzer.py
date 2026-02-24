"""Brand extraction engine — GPT-4o-mini + Instructor for structured output."""

from __future__ import annotations

from enum import Enum
from typing import Literal

import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field


# --- Brand dictionaries ---

COKE_BRANDS = {
    "coca_cola": ["coca-cola", "coca cola", "coke", "diet coke", "coke zero", "coca-cola zero sugar"],
    "thums_up": ["thums up", "thumbs up", "thumps up"],
    "sprite": ["sprite"],
    "fanta": ["fanta"],
    "limca": ["limca"],
    "maaza": ["maaza"],
    "minute_maid": ["minute maid"],
    "kinley": ["kinley"],
    "schweppes": ["schweppes"],
    "georgia": ["georgia coffee"],
}

COMPETITORS = {
    "pepsi": ["pepsi", "pepsico", "pepsi cola"],
    "mountain_dew": ["mountain dew", "mtn dew"],
    "mirinda": ["mirinda"],
    "7up": ["7up", "seven up", "7 up"],
    "slice": ["slice"],
    "tropicana": ["tropicana"],
    "sting": ["sting energy"],
    "campa": ["campa cola", "campa"],
    "bovonto": ["bovonto"],
    "paper_boat": ["paper boat"],
    "real": ["real juice", "real fruit"],
    "frooti": ["frooti"],
    "lahori": ["lahori", "lahori zeera"],
    "brobond": ["brobond"],
}


# --- Pydantic models ---

class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    mixed = "mixed"


class BrandMention(BaseModel):
    """A single brand mention extracted from the response."""
    brand: str = Field(description="Brand name as mentioned in the text")
    position: int = Field(description="Order of first mention (1 = first mentioned)")
    sentiment: Sentiment = Field(description="Sentiment toward this brand in the response")
    is_recommended: bool = Field(description="Whether the response recommends or favors this brand")
    context: str = Field(description="One sentence summarizing how this brand is discussed")


class ResponseAnalysis(BaseModel):
    """Structured analysis of brand mentions in an LLM response."""
    coke_brands_found: list[str] = Field(description="Coca-Cola portfolio brands found (use canonical names: coca_cola, thums_up, sprite, fanta, limca, maaza, etc.)")
    competitor_brands_found: list[str] = Field(description="Competitor brands found (use canonical names: pepsi, campa, bovonto, etc.)")
    all_mentions: list[BrandMention] = Field(description="All brand mentions in order of appearance")
    coke_domains_cited: list[str] = Field(description="Any Coca-Cola owned domains in citations (e.g., coca-cola.com)")
    response_type: Literal["list", "comparison", "direct_answer", "narrative", "refusal"] = Field(
        description="Type of response: list (ranked items), comparison (A vs B), direct_answer (single recommendation), narrative (story/history), refusal (won't answer)"
    )
    coke_is_primary_recommendation: bool = Field(
        description="Whether a Coca-Cola brand is the #1 recommendation or most favorably positioned"
    )


# --- Analyzer ---

ANALYSIS_PROMPT = """Analyze this LLM-generated response about beverages/drinks in the Indian market.

Extract ALL brand mentions (soft drinks, beverages, cola brands). For each brand, determine:
- Its position (order of first mention, 1 = first)
- Sentiment (positive/neutral/negative/mixed)
- Whether it's recommended or favored
- Brief context

Categorize brands into Coca-Cola portfolio (Coca-Cola, Thums Up, Sprite, Fanta, Limca, Maaza, Minute Maid, Kinley, Schweppes) vs competitors (Pepsi, Mountain Dew, Mirinda, 7Up, Campa, Bovonto, Paper Boat, Frooti, Lahori, etc.).

Response to analyze:
---
{response_text}
---

Citations found: {citation_domains}"""


async def analyze_response(
    response_text: str,
    citation_domains: list[str] | None = None,
    model: str = "gpt-4o-mini",
) -> ResponseAnalysis:
    """Extract brand mentions and sentiment from an LLM response."""
    client = instructor.from_openai(AsyncOpenAI())

    domains_str = ", ".join(citation_domains) if citation_domains else "none"

    analysis = await client.chat.completions.create(
        model=model,
        response_model=ResponseAnalysis,
        messages=[
            {
                "role": "user",
                "content": ANALYSIS_PROMPT.format(
                    response_text=response_text,
                    citation_domains=domains_str,
                ),
            }
        ],
        max_retries=2,
    )

    return analysis
