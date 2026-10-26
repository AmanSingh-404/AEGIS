"""Application service for normalized LLM requests."""

import time
from typing import Any

import structlog

from api.providers import LLMProvider, LLMRequest, LLMResponse, create_llm_provider


logger = structlog.get_logger(__name__)


class LLMService:
    """Coordinate normalized requests with a configured LLM provider."""

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider if provider is not None else create_llm_provider()

    @property
    def provider_name(self) -> str:
        """Return the selected provider's stable identifier."""
        return self._provider.name

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response and log safe operational metadata."""
        started = time.perf_counter()

        logger.info(
            "llm_generation_started",
            provider=self._provider.name,
            model=request.model,
            message_count=len(request.messages),
        )

        try:
            response = await self._provider.generate(request)
        except Exception as exc:
            logger.warning(
                "llm_generation_failed",
                provider=self._provider.name,
                model=request.model,
                elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
                error_type=type(exc).__name__,
            )
            raise

        logger.info(
            "llm_generation_completed",
            provider=response.provider,
            model=response.model,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.finish_reason,
        )

        return response

    async def aclose(self) -> None:
        """Close the provider client when it exposes an async close method."""
        close = getattr(self._provider, "aclose", None)
        if close is not None:
            result: Any = close()
            if hasattr(result, "__await__"):
                await result
