"""HTTP endpoints for controlled LLM generation."""

from collections.abc import AsyncIterator
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.config import Settings, get_settings
from api.providers.schemas import LLMRequest
from api.services.llm_service import LLMService
from api.routes.llm_schemas import LLMGenerateRequest, LLMGenerateResponse


logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


async def get_llm_service() -> AsyncIterator[LLMService]:
    """Provide a service instance and close its provider client after use."""
    try:
        service = LLMService()
    except Exception as exc:
        logger.warning(
            "llm_service_initialization_failed",
            error_type=type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "llm_provider_unavailable",
                "message": "The language model provider could not complete the request.",
            },
        ) from None

    try:
        yield service
    finally:
        await service.aclose()


def require_llm_generation(
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Keep this endpoint unavailable unless explicitly enabled."""
    if (
        not settings.llm_generation_enabled
        or settings.environment != "development"
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Endpoint not found."},
        )


@router.post(
    "/generate",
    response_model=LLMGenerateResponse,
    dependencies=[Depends(require_llm_generation)],
)
async def generate(
    payload: LLMGenerateRequest,
    request: Request,
    service: Annotated[LLMService, Depends(get_llm_service)],
) -> LLMGenerateResponse:
    """Generate a model response using the configured provider."""
    llm_request = LLMRequest(
        model=payload.model,
        messages=payload.messages,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        timeout_seconds=payload.timeout_seconds,
    )

    try:
        result = await service.generate(llm_request)
    except Exception as exc:
        logger.warning(
            "llm_endpoint_failed",
            request_id=getattr(request.state, "request_id", None),
            error_type=type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "llm_provider_unavailable",
                "message": "The language model provider could not complete the request.",
            },
        ) from None

    return LLMGenerateResponse(
        content=result.content,
        provider=result.provider,
        model=result.model,
        usage=result.usage,
        finish_reason=result.finish_reason,
        latency_ms=result.latency_ms,
        request_id=result.request_id,
    )
