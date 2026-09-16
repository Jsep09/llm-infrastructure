from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from gateway.providers.base import LLMProvider, ProviderCompletion


@pytest.fixture
def mock_provider():
    instance = AsyncMock(spec=LLMProvider)
    instance.name = "openai"
    instance.complete = AsyncMock(
        return_value=ProviderCompletion(
            content="Mock response.",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
        )
    )
    return instance


def test_non_streaming_completion(client: TestClient, mock_provider):
    with patch("gateway.api.chat.OpenAICompatProvider", return_value=mock_provider):
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False,
            },
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["model"] == "gpt-4o-mini"
    assert len(data["choices"]) > 0
    assert data["choices"][0]["message"]["role"] == "assistant"


def test_missing_model(client: TestClient):
    response = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert response.status_code == 422


def test_empty_messages(client: TestClient):
    response = client.post(
        "/v1/chat/completions",
        json={"model": "gpt-4o-mini", "messages": []},
    )
    assert response.status_code == 422


def test_invalid_role(client: TestClient):
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "robot", "content": "Hello"}],
        },
    )
    assert response.status_code == 422
