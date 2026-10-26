"""Tests for the LLM application service."""

from unittest.mock import AsyncMock

import pytest

from api.providers.schemas import LLMMessage, LLMRequest, LLMResponse, LLMUsage
from api.services.llm_service import LLMService


def make_request() -> LLMRequest:
    return LLMRequest(
        model="test-model",
        messages=(LLMMessage(role="user", content="private prompt content"),),
    )


def make_response() -> LLMResponse:
    return LLMResponse(
        content="private response content",
        provider="fake",
        model="test-model",
        usage=LLMUsage(input_tokens=4, output_tokens=7),
        finish_reason="stop",
        latency_ms=12.5,
        request_id="test-request-id",
    )


class FakeProvider:
    name = "fake"

    def __init__(self, response: LLMResponse | None = None) -> None:
        self.response = response or make_response()
        self.generate = AsyncMock(return_value=self.response)
        self.aclose = AsyncMock()


@pytest.mark.anyio
async def test_generate_returns_provider_response() -> None:
    provider = FakeProvider()
    service = LLMService(provider=provider)

    response = await service.generate(make_request())

    assert response == provider.response
    provider.generate.assert_awaited_once()


def test_provider_name_is_exposed() -> None:
    service = LLMService(provider=FakeProvider())

    assert service.provider_name == "fake"


@pytest.mark.anyio
async def test_generate_propagates_provider_error() -> None:
    provider = FakeProvider()
    provider.generate.side_effect = RuntimeError("provider unavailable")
    service = LLMService(provider=provider)

    with pytest.raises(RuntimeError, match="provider unavailable"):
        await service.generate(make_request())


@pytest.mark.anyio
async def test_generate_logs_failure_type_without_prompt_content(
    capsys: pytest.CaptureFixture[str],
) -> None:
    provider = FakeProvider()
    provider.generate.side_effect = RuntimeError("private provider detail")
    service = LLMService(provider=provider)

    with pytest.raises(RuntimeError):
        await service.generate(make_request())

    output = capsys.readouterr().out
    assert "llm_generation_failed" in output
    assert "RuntimeError" in output
    assert "private prompt content" not in output
    assert "private provider detail" not in output


@pytest.mark.anyio
async def test_aclose_closes_provider_client() -> None:
    provider = FakeProvider()
    service = LLMService(provider=provider)

    await service.aclose()

    provider.aclose.assert_awaited_once()


@pytest.mark.anyio
async def test_aclose_supports_provider_without_close_method() -> None:
    class ProviderWithoutClose:
        name = "fake"

        async def generate(self, request: LLMRequest) -> LLMResponse:
            return make_response()

    service = LLMService(provider=ProviderWithoutClose())

    await service.aclose()
