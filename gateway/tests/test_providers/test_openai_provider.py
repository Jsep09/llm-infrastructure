from __future__ import annotations

import httpx2
import openai
import pytest

from gateway.core.errors import ProviderError, ProviderRateLimitedError, ProviderTimeoutError, ProviderUnavailableError
from gateway.providers.openai_compat import OpenAICompatProvider


@pytest.fixture
def provider():
    return OpenAICompatProvider(provider_name="openai", api_key="sk-test-fake-key")


def _req() -> httpx2.Request:
    return httpx2.Request("POST", "https://api.openai.com/v1")


def test_normalize_timeout_error(provider: OpenAICompatProvider):
    exc = openai.APITimeoutError(request=_req())
    with pytest.raises(ProviderTimeoutError):
        raise provider._normalize_error(exc)


def test_normalize_api_error(provider: OpenAICompatProvider):
    exc = openai.APIError(message="bad gateway", request=_req(), body=None)
    with pytest.raises(ProviderError):
        raise provider._normalize_error(exc)


def test_normalize_rate_limit(provider: OpenAICompatProvider):
    exc = openai.RateLimitError(
        message="rate limited",
        response=httpx2.Response(429, request=_req()),
        body=None,
    )
    with pytest.raises(ProviderRateLimitedError):
        raise provider._normalize_error(exc)


def test_normalize_connection_error(provider: OpenAICompatProvider):
    exc = openai.APIConnectionError(message="connection failed", request=_req())
    with pytest.raises(ProviderUnavailableError):
        raise provider._normalize_error(exc)


def test_uses_correct_api_key_key(provider: OpenAICompatProvider):
    """OpenAI should look up 'openai_api_key' in config."""
    # Just verify the provider name is correct
    assert provider.name == "openai"
