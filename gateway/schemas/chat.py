from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern=r"^(system|user|assistant)$")
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage] = Field(..., min_length=1)
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False


class UsageInfo(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_input_cost: float = 0.0
    estimated_output_cost: float = 0.0
    estimated_total_cost: float = 0.0


class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    provider: str
    provider_model: str
    choices: list[dict]
    usage: UsageInfo | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str = ""
