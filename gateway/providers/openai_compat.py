from __future__ import annotations

from typing import AsyncIterator

from openai import AsyncOpenAI

from gateway.config import get_api_key, settings
from gateway.core.errors import (
    ProviderError,
    ProviderRateLimitedError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from gateway.providers.base import LLMProvider, ProviderCompletion, ProviderStreamChunk


class OpenAICompatProvider(LLMProvider):
    """Adapter for any OpenAI-compatible provider (OpenAI, OpenRouter, etc.)."""

    def __init__(self, provider_name: str = "openai", api_key: str | None = None) -> None:
        self._provider = provider_name
        self._api_key = api_key or get_api_key(f"{provider_name}_api_key")
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            kwargs = {
                "api_key": self._api_key or "placeholder-do-not-use",
                "timeout": settings.provider_timeout,
            }
            if self._provider == "openrouter":
                kwargs["base_url"] = settings.openrouter_base_url
                kwargs["default_headers"] = {
                    "HTTP-Referer": "https://github.com/user/llm-infrastructure",
                    "X-Title": "LLM Infrastructure",
                }
            self._client = AsyncOpenAI(**kwargs)
        return self._client

    @property
    def name(self) -> str:
        return self._provider

    async def complete(
        self,
        model: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ProviderCompletion:
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )
        except Exception as exc:
            raise self._normalize_error(exc)

        choice = response.choices[0]
        usage = response.usage

        return ProviderCompletion(
            content=choice.message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    async def stream(
        self,
        model: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[ProviderStreamChunk]:
        client = self._get_client()
        try:
            stream_obj = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                stream_options={"include_usage": True},
            )
        except Exception as exc:
            raise self._normalize_error(exc)

        async for chunk in stream_obj:
            delta = chunk.choices[0].delta if chunk.choices else None
            finish = chunk.choices[0].finish_reason if chunk.choices else None
            usage = chunk.usage

            yield ProviderStreamChunk(
                content=delta.content or "" if delta else "",
                finish_reason=finish,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
            )

    def _normalize_error(self, exc: Exception) -> Exception:
        import openai

        if isinstance(exc, openai.RateLimitError):
            return ProviderRateLimitedError(str(exc))
        if isinstance(exc, openai.APITimeoutError):
            return ProviderTimeoutError(str(exc))
        if isinstance(exc, openai.APIConnectionError):
            return ProviderUnavailableError(str(exc))
        if isinstance(exc, openai.APIError):
            return ProviderError(str(exc))
        return ProviderError(str(exc))
