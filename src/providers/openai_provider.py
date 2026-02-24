"""OpenAI provider — GPT-5.2 Instant with web_search for citations."""

from __future__ import annotations

import time

from openai import AsyncOpenAI

from .base import BaseProvider, ProviderResponse, RawCitation


class OpenAIProvider(BaseProvider):
    name = "openai"

    # Models that use "web_search" vs legacy "web_search_preview"
    _WEB_SEARCH_MODELS = {"gpt-5", "gpt-5.2-chat-latest", "gpt-5.2"}

    def __init__(self, model: str = "gpt-5.2-chat-latest"):
        self.model = model
        self.client = AsyncOpenAI()

    async def query(self, prompt: str) -> ProviderResponse:
        start = time.time()

        # GPT-5+ uses "web_search", older models use "web_search_preview"
        tool_type = "web_search" if any(self.model.startswith(m) for m in self._WEB_SEARCH_MODELS) else "web_search_preview"

        response = await self.client.responses.create(
            model=self.model,
            tools=[{"type": tool_type}],
            input=prompt,
        )

        latency_ms = self._measure_latency(start)

        # Extract text and citations from the response output
        raw_text = ""
        citations: list[RawCitation] = []

        for item in response.output:
            # The message item contains the generated text + annotations
            if item.type == "message":
                for content_block in item.content:
                    if content_block.type == "output_text":
                        raw_text = content_block.text
                        # Extract url_citation annotations
                        for ann in getattr(content_block, "annotations", []) or []:
                            if ann.type == "url_citation":
                                citations.append(RawCitation(
                                    url=ann.url,
                                    title=ann.title,
                                    text=raw_text[ann.start_index:ann.end_index] if ann.start_index and ann.end_index else None,
                                    start_index=ann.start_index,
                                    end_index=ann.end_index,
                                ))

        # Token usage
        usage = response.usage
        input_tokens = usage.input_tokens if usage else 0
        output_tokens = usage.output_tokens if usage else 0

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_text=raw_text,
            raw_citations=citations,
            raw_response=response.model_dump(),
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
