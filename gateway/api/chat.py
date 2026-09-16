from __future__ import annotations

import uuid
from typing import AsyncIterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from gateway.core.errors import GatewayError, InternalError
from gateway.providers.base import LLMProvider, ProviderCompletion
from gateway.providers.openai_compat import OpenAICompatProvider
from gateway.schemas.chat import ChatCompletionRequest, ChatCompletionResponse, UsageInfo
from gateway.config import settings

router = APIRouter()

PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAICompatProvider,
    "openrouter": OpenAICompatProvider,
    "groq": OpenAICompatProvider,
}


def _get_provider(provider_name: str) -> LLMProvider:
    if provider_name not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider: {provider_name}")
    return OpenAICompatProvider(provider_name=provider_name)


def _build_usage(completion: ProviderCompletion) -> UsageInfo:
    return UsageInfo(
        input_tokens=completion.input_tokens,
        output_tokens=completion.output_tokens,
        total_tokens=completion.total_tokens,
    )


@router.post("/v1/chat/completions", response_model=None)
async def chat_completion(
    body: ChatCompletionRequest,
) -> ChatCompletionResponse | EventSourceResponse:
    request_id = f"req_{uuid.uuid4().hex[:12]}"

    # --- resolve provider ---
    provider_name = settings.default_provider

    try:
        provider = _get_provider(provider_name)
    except ValueError:
        raise InternalError(f"Provider '{provider_name}' not configured.")

    messages = [m.model_dump() for m in body.messages]
    kwargs = {
        "model": body.model,
        "messages": messages,
    }
    if body.temperature is not None:
        kwargs["temperature"] = body.temperature
    if body.max_tokens is not None:
        kwargs["max_tokens"] = body.max_tokens

    if body.stream:
        return EventSourceResponse(
            _stream_response(provider, request_id, kwargs),
            media_type="text/event-stream",
        )

    return await _complete_response(provider, request_id, kwargs)


async def _complete_response(
    provider: LLMProvider,
    request_id: str,
    kwargs: dict,
) -> ChatCompletionResponse:
    try:
        completion = await provider.complete(**kwargs)
    except GatewayError:
        raise
    except Exception as exc:
        raise InternalError(str(exc))

    return ChatCompletionResponse(
        id=request_id,
        model=kwargs["model"],
        provider=provider.name,
        provider_model=kwargs["model"],
        choices=[{"index": 0, "message": {"role": "assistant", "content": completion.content}, "finish_reason": "stop"}],
        usage=_build_usage(completion),
    )


async def _stream_response(
    provider: LLMProvider,
    request_id: str,
    kwargs: dict,
) -> AsyncIterator[dict]:
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0

    try:
        async for chunk in provider.stream(**kwargs):
            if chunk.input_tokens:
                input_tokens = chunk.input_tokens
            if chunk.output_tokens:
                output_tokens = chunk.output_tokens
            if chunk.total_tokens:
                total_tokens = chunk.total_tokens

            if chunk.content:
                yield {
                    "event": "chunk",
                    "data": chunk.content,
                }

            if chunk.finish_reason:
                yield {
                    "event": "done",
                    "data": {
                        "request_id": request_id,
                        "provider": provider.name,
                        "provider_model": kwargs["model"],
                        "finish_reason": chunk.finish_reason,
                        "usage": {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "total_tokens": total_tokens,
                        },
                    },
                }
                return
    except GatewayError:
        raise
    except Exception as exc:
        raise InternalError(str(exc))
