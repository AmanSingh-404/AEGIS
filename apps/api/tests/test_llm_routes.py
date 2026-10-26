"""Tests for the controlled LLM generation endpoint."""

from unittest.mock import AsyncMock

import anyio
import httpx
import pytest

from api.config import Settings, get_settings
from api.main import app
from api.providers.schemas import LLMResponse, LLMUsage
from api.routes.llm import get_llm_service


def make_response() -> LLMResponse:
    return LLMResponse(
        content="test response",
        provider="fake",
        model="test-model",
        usage=LLMUsage(input_tokens=3, output_tokens=5),
        finish_reason="stop",
        latency_ms=10.0,
        request_id="fake-request-id",
    )


async def request_generation(payload: dict[str, object]) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.post("/api/v1/llm/generate", json=payload)


@pytest.fixture
def enabled_settings():
    settings = Settings(_env_file=None, llm_generation_enabled=True)
    app.dependency_overrides[get_settings] = lambda: settings
    yield settings
    app.dependency_overrides.clear()


def test_generation_endpoint_is_disabled_by_default() -> None:
    app.dependency_overrides.clear()
    response = anyio.run(
        request_generation,
        {
            "model": "test-model",
            "messages": [{"role": "user", "content": "hello"}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_generation_endpoint_stays_disabled_in_production() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        llm_generation_enabled=True,
    )
    app.dependency_overrides.clear()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        response = anyio.run(
            request_generation,
            {
                "model": "test-model",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_generation_endpoint_returns_normalized_response(enabled_settings) -> None:
    service = type("FakeService", (), {})()
    service.generate = AsyncMock(return_value=make_response())
    service.aclose = AsyncMock()
    service.provider_name = "fake"
    app.dependency_overrides[get_llm_service] = lambda: service

    try:
        response = anyio.run(
            request_generation,
            {
                "model": "test-model",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "test response"
    assert body["provider"] == "fake"
    assert body["usage"]["input_tokens"] == 3
    assert body["usage"]["output_tokens"] == 5
    service.generate.assert_awaited_once()


def test_generation_endpoint_sanitizes_service_initialization_errors(
    enabled_settings,
) -> None:
    from unittest.mock import patch

    with patch(
        "api.routes.llm.LLMService",
        side_effect=ValueError("private credential initialization detail"),
    ):
        response = anyio.run(
            request_generation,
            {
                "model": "test-model",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "llm_provider_unavailable"
    assert "private credential initialization detail" not in response.text


def test_generation_endpoint_sanitizes_provider_errors(enabled_settings) -> None:
    service = type("FakeService", (), {})()
    service.generate = AsyncMock(
        side_effect=RuntimeError("private provider secret detail")
    )
    service.aclose = AsyncMock()
    app.dependency_overrides[get_llm_service] = lambda: service

    try:
        response = anyio.run(
            request_generation,
            {
                "model": "test-model",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "llm_provider_unavailable"
    assert "private provider secret detail" not in response.text


def test_generation_endpoint_rejects_invalid_request(enabled_settings) -> None:
    service = type("FakeService", (), {})()
    service.generate = AsyncMock(return_value=make_response())
    service.aclose = AsyncMock()
    app.dependency_overrides[get_llm_service] = lambda: service

    try:
        response = anyio.run(
        request_generation,
        {
            "model": "test-model",
            "messages": [],
            "unexpected_field": "rejected",
        },
    )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    service.generate.assert_not_awaited()


def test_llm_service_dependency_closes_service_on_exit() -> None:
    from unittest.mock import patch

    service = type("FakeService", (), {})()
    service.aclose = AsyncMock()

    async def exercise_dependency() -> None:
        with patch("api.routes.llm.LLMService", return_value=service):
            dependency = get_llm_service()
            provided_service = await anext(dependency)
            assert provided_service is service
            await dependency.aclose()

    anyio.run(exercise_dependency)

    service.aclose.assert_awaited_once()


def test_llm_service_dependency_closes_service_after_exception() -> None:
    from unittest.mock import patch

    service = type("FakeService", (), {})()
    service.aclose = AsyncMock()

    async def exercise_dependency() -> None:
        with patch("api.routes.llm.LLMService", return_value=service):
            dependency = get_llm_service()
            provided_service = await anext(dependency)

            assert provided_service is service

            with pytest.raises(RuntimeError, match="simulated request failure"):
                await dependency.athrow(
                    RuntimeError("simulated request failure")
                )

    anyio.run(exercise_dependency)

    service.aclose.assert_awaited_once()
