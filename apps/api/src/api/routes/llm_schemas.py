"""Validated HTTP schemas for controlled LLM generation."""

from pydantic import BaseModel, ConfigDict, Field

from api.providers.schemas import LLMMessage, LLMUsage


class LLMGenerateRequest(BaseModel):
    """Public request schema for an LLM generation call."""

    model_config = ConfigDict(extra="forbid")

    model: str = Field(min_length=1, max_length=200)
    messages: tuple[LLMMessage, ...] = Field(min_length=1, max_length=100)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=8192)
    timeout_seconds: float = Field(default=30.0, gt=0.0, le=120.0)


class LLMGenerateResponse(BaseModel):
    """Normalized response returned to the API caller."""

    model_config = ConfigDict(extra="forbid")

    content: str
    provider: str
    model: str
    usage: LLMUsage
    finish_reason: str | None = None
    latency_ms: float = Field(ge=0.0)
    request_id: str | None = None
