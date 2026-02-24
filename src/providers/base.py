"""Base provider interface and shared data models."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawCitation:
    """Provider-native citation before normalization."""
    url: str
    title: str | None = None
    text: str | None = None
    start_index: int | None = None
    end_index: int | None = None
    confidence: float = 1.0
    extra: dict = field(default_factory=dict)


@dataclass
class ProviderResponse:
    """Unified response from any LLM provider."""
    provider: str
    model: str
    raw_text: str
    raw_citations: list[RawCitation]
    raw_response: dict
    latency_ms: int
    input_tokens: int
    output_tokens: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str

    @abstractmethod
    async def query(self, prompt: str) -> ProviderResponse:
        """Send a prompt with web search enabled, return response + citations."""
        ...

    @staticmethod
    def _measure_latency(start: float) -> int:
        """Return elapsed time in milliseconds."""
        return int((time.time() - start) * 1000)
