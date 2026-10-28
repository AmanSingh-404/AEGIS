"""HTTP boundary security tests for LLM generation."""

from unittest.mock import AsyncMock

import anyio
import httpx
import pytest

from api.config import Settings, get_settings
from api.main import app
from api.routes.llm import get_llm_service


async def _post_generation(payload: dict[str, object]) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.post("/api/v1/llm/generate", json=payload)


@pytest.fixture
def mocked_llm_service():
    app.dependency_overrides.clear()
    settings = Settings(_env_file=None, llm_generation_enabled=True)
    app.dependency_overrides[get_settings] = lambda: settings

    service = type("FakeService", (), {})()
    service.generate = AsyncMock()
    service.aclose = AsyncMock()
    service.provider_name = "fake"
    app.dependency_overrides[get_llm_service] = lambda: service

    yield service
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "payload",
    [
        {
            "model": "test-model",
            "messages": [{"role": "user", "content": "hello"}] * 101,
        },
        {
            "model": "test-model",
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 8193,
        },
        {
            "model": "test-model",
            "messages": [{"role": "user", "content": "hello"}],
            "timeout_seconds": 121,
        },
        {
            "model": "test-model",
            "messages": [{"role": "user", "content": "hello"}],
            "unexpected_field": "must be rejected",
        },
    ],
)
def test_invalid_boundary_requests_are_rejected_before_provider_call(
    mocked_llm_service,
    payload: dict[str, object],
) -> None:
    response = anyio.run(_post_generation, payload)

    assert response.status_code == 422
    mocked_llm_service.generate.assert_not_awaited()

def test_message_content_at_limit_is_accepted_by_schema() -> None:
    from api.routes.llm_schemas import LLMGenerateRequest

    payload = {
        "model": "test-model",
        "messages": [
            {"role": "user", "content": "x" * 32000},
        ],
    }

    request = LLMGenerateRequest.model_validate(payload)

    assert len(request.messages[0].content) == 32000


def test_message_content_over_limit_is_rejected_before_provider_call(
    mocked_llm_service,
) -> None:
    payload = {
        "model": "test-model",
        "messages": [
            {"role": "user", "content": "x" * 32001},
        ],
    }

    response = anyio.run(_post_generation, payload)

    assert response.status_code == 422
    mocked_llm_service.generate.assert_not_awaited()
