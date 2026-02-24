"""Perplexity provider — Sonar with native citations."""

from __future__ import annotations

import os
import time

import httpx

from .base import BaseProvider, ProviderResponse, RawCitation


class PerplexityProvider(BaseProvider):
    name = "perplexity"

    BASE_URL = "https://api.perplexity.ai/chat/completions"

    def __init__(self, model: str = "sonar"):  # "sonar" (free) or "sonar-pro" (paid)
        self.model = model
        self.api_key = os.environ.get("PERPLEXITY_API_KEY", "")

    async def query(self, prompt: str) -> ProviderResponse:
        start = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.BASE_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = self._measure_latency(start)

        # Extract text from choices
        raw_text = ""
        if data.get("choices"):
            raw_text = data["choices"][0].get("message", {}).get("content", "")

        # Extract citations — Perplexity returns a flat URL array
        citation_urls = data.get("citations", [])
        citations: list[RawCitation] = []
        for url in citation_urls:
            citations.append(RawCitation(
                url=url,
                title=None,  # Perplexity doesn't return titles in the citations array
            ))

        # Token usage
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_text=raw_text,
            raw_citations=citations,
            raw_response=data,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
