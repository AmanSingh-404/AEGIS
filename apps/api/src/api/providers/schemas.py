from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MessageRole = Literal["system", "user", "assistant"]


class LLMMessage(BaseModel):
    """A provider-independent chat message."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    role: MessageRole
    content: str


class LLMRequest(BaseModel):
    """A normalized request shared by all LLM providers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    model: str = Field(min_length=1, max_length=200)
    messages: tuple[LLMMessage, ...] = Field(min_length=1)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1)
    timeout_seconds: float = Field(default=60.0, gt=0.0, le=600.0)


class LLMUsage(BaseModel):
    """Token usage reported by a provider."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMResponse(BaseModel):
    """A normalized response returned by an LLM provider."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    content: str
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    usage: LLMUsage
    finish_reason: str | None = None
    latency_ms: float = Field(ge=0.0)
    request_id: str | None = None
