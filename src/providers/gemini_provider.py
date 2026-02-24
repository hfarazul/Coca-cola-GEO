"""Gemini provider — Gemini 3 Flash with Google Search grounding."""

from __future__ import annotations

import time

from google import genai
from google.genai import types

from .base import BaseProvider, ProviderResponse, RawCitation


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, model: str = "gemini-3-flash-preview"):
        self.model = model
        self.client = genai.Client()

    async def query(self, prompt: str) -> ProviderResponse:
        start = time.time()

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        latency_ms = self._measure_latency(start)

        # Extract text
        raw_text = response.text or ""

        # Extract citations from grounding metadata
        citations: list[RawCitation] = []
        metadata = getattr(response.candidates[0], "grounding_metadata", None) if response.candidates else None

        if metadata:
            # groundingChunks contain the source URLs
            chunks = getattr(metadata, "grounding_chunks", []) or []
            supports = getattr(metadata, "grounding_supports", []) or []

            # Build chunk index -> citation mapping
            chunk_citations: dict[int, RawCitation] = {}
            for i, chunk in enumerate(chunks):
                web = getattr(chunk, "web", None)
                if web:
                    chunk_citations[i] = RawCitation(
                        url=web.uri or "",
                        title=web.title,
                        confidence=1.0,
                    )

            # Enrich with confidence scores from grounding supports
            for support in supports:
                segment = getattr(support, "segment", None)
                chunk_indices = getattr(support, "grounding_chunk_indices", []) or []
                confidence_scores = getattr(support, "confidence_scores", []) or []

                segment_text = segment.text if segment else None
                start_idx = segment.start_index if segment else None
                end_idx = segment.end_index if segment else None

                for idx, conf in zip(chunk_indices, confidence_scores):
                    if idx in chunk_citations:
                        c = chunk_citations[idx]
                        # Update with best confidence and text if available
                        if conf > c.confidence or c.confidence == 1.0:
                            c.confidence = conf
                        if segment_text and not c.text:
                            c.text = segment_text
                            c.start_index = start_idx
                            c.end_index = end_idx

            citations = list(chunk_citations.values())

        # Token usage
        usage = response.usage_metadata
        input_tokens = getattr(usage, "prompt_token_count", 0) or 0 if usage else 0
        output_tokens = getattr(usage, "candidates_token_count", 0) or 0 if usage else 0

        # Build raw response dict safely
        try:
            raw_response = response.model_dump() if hasattr(response, "model_dump") else {}
        except Exception:
            raw_response = {"model": self.model, "text_length": len(raw_text)}

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_text=raw_text,
            raw_citations=citations,
            raw_response=raw_response,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
