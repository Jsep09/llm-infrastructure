from __future__ import annotations

from typing import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from gateway.main import app
from gateway.providers.base import LLMProvider, ProviderCompletion, ProviderStreamChunk


class FakeProvider(LLMProvider):
    """In-memory fake provider used for integration tests."""

    def __init__(self) -> None:
        self.name = "fake"
        self.requests: list[dict] = []

    @property
    def name(self) -> str:
        return "fake"

    async def complete(
        self,
        model: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ProviderCompletion:
        self.requests.append(locals())
        return ProviderCompletion(
            content="This is a fake response.",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
        )

    async def stream(
        self,
        model: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[ProviderStreamChunk]:
        self.requests.append(locals())
        yield ProviderStreamChunk(content="Hello ")
        yield ProviderStreamChunk(content="world!")
        yield ProviderStreamChunk(
            finish_reason="stop",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
        )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
