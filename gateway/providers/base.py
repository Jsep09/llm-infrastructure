from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class ProviderCompletion:
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass
class ProviderStreamChunk:
    content: str = ""
    finish_reason: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class LLMProvider(ABC):
    """Abstract interface every provider adapter must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier, e.g. 'openai', 'openrouter'."""
        ...

    @abstractmethod
    async def complete(
        self,
        model: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ProviderCompletion:
        """Non-streaming completion. Returns the full response."""
        ...

    @abstractmethod
    async def stream(
        self,
        model: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[ProviderStreamChunk]:
        """Streaming completion. Yields chunks as they arrive."""
        ...
