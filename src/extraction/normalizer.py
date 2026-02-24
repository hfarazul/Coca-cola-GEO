"""Citation normalizer — converts provider-native citations to unified schema."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from src.providers.base import ProviderResponse, RawCitation


@dataclass
class NormalizedCitation:
    """Unified citation across all providers."""
    url: str
    domain: str
    title: str | None
    cited_text: str | None
    char_offset: int | None
    confidence: float

    @property
    def is_coke_domain(self) -> bool:
        """Check if the citation is from a Coca-Cola owned domain."""
        coke_domains = {
            "coca-cola.com", "coca-colaindia.com", "coca-colacompany.com",
            "coke.com", "thumsup.com", "sprite.com", "fanta.com",
            "maaza.com", "limca.com", "minutemaid.in",
        }
        return any(d in self.domain for d in coke_domains)


def normalize_citations(response: ProviderResponse) -> list[NormalizedCitation]:
    """Normalize provider-specific citations to unified format."""
    normalizer = _NORMALIZERS.get(response.provider, _normalize_generic)
    return normalizer(response)


def _extract_domain(url: str) -> str:
    """Extract clean domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Strip www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url


def _normalize_openai(response: ProviderResponse) -> list[NormalizedCitation]:
    """OpenAI: url_citation annotations with start/end indices."""
    results = []
    seen_urls = set()

    for c in response.raw_citations:
        if c.url in seen_urls:
            continue
        seen_urls.add(c.url)

        results.append(NormalizedCitation(
            url=c.url,
            domain=_extract_domain(c.url),
            title=c.title,
            cited_text=c.text,
            char_offset=c.start_index,
            confidence=1.0,  # OpenAI doesn't provide confidence scores
        ))
    return results


def _normalize_gemini(response: ProviderResponse) -> list[NormalizedCitation]:
    """Gemini: groundingChunks with confidence scores from groundingSupports."""
    results = []
    seen_urls = set()

    for c in response.raw_citations:
        # Gemini URLs go through vertexaisearch proxy — extract the title as domain hint
        url = c.url
        if url in seen_urls:
            continue
        seen_urls.add(url)

        results.append(NormalizedCitation(
            url=url,
            domain=_extract_domain(url) if "vertexaisearch" not in url else (c.title or _extract_domain(url)),
            title=c.title,
            cited_text=c.text,
            char_offset=c.start_index,
            confidence=c.confidence if c.confidence != 1.0 else 0.9,  # Gemini provides real scores
        ))
    return results


def _normalize_perplexity(response: ProviderResponse) -> list[NormalizedCitation]:
    """Perplexity: flat URL array with [n] bracket refs in text."""
    results = []
    seen_urls = set()

    for c in response.raw_citations:
        if c.url in seen_urls:
            continue
        seen_urls.add(c.url)

        results.append(NormalizedCitation(
            url=c.url,
            domain=_extract_domain(c.url),
            title=c.title,
            cited_text=None,  # Perplexity doesn't provide cited text snippets
            char_offset=None,
            confidence=1.0,  # Perplexity doesn't provide confidence scores
        ))
    return results


def _normalize_generic(response: ProviderResponse) -> list[NormalizedCitation]:
    """Fallback normalizer for unknown providers."""
    results = []
    for c in response.raw_citations:
        results.append(NormalizedCitation(
            url=c.url,
            domain=_extract_domain(c.url),
            title=c.title,
            cited_text=c.text,
            char_offset=c.start_index,
            confidence=c.confidence,
        ))
    return results


_NORMALIZERS = {
    "openai": _normalize_openai,
    "gemini": _normalize_gemini,
    "perplexity": _normalize_perplexity,
}
