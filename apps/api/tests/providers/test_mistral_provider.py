from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

pytestmark = pytest.mark.anyio
from api.config import get_settings
from api.providers.mistral_provider import MistralProvider
from api.providers.schemas import LLMMessage, LLMRequest


def make_request() -> LLMRequest:
    return LLMRequest(
        model="mistral-small-latest",
        messages=(
            LLMMessage(role="system", content="Be concise."),
            LLMMessage(role="user", content="Hello"),
        ),
        temperature=0.2,
        max_tokens=64,
        timeout_seconds=5,
    )


def make_response(
    *,
    content="Hello back",
    model="mistral-small-latest",
    prompt_tokens=7,
    completion_tokens=3,
    choices=None,
):
    if choices is None:
        choices = [
            SimpleNamespace(
                message=SimpleNamespace(content=content),
                finish_reason="stop",
            )
        ]

    usage = None
    if prompt_tokens is not None and completion_tokens is not None:
        usage = SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    return SimpleNamespace(
        id="mistral-request-123",
        model=model,
        choices=choices,
        usage=usage,
    )


async def test_generate_maps_request_and_normalizes_response():
    client = SimpleNamespace(
        chat=SimpleNamespace(
            complete_async=AsyncMock(return_value=make_response())
        )
    )
    provider = MistralProvider(client=client)

    result = await provider.generate(make_request())

    call = client.chat.complete_async.await_args
    assert call.kwargs["model"] == "mistral-small-latest"
    assert call.kwargs["temperature"] == 0.2
    assert call.kwargs["max_tokens"] == 64
    assert call.kwargs["timeout_ms"] == 5000
    assert call.kwargs["messages"] == [
        {"role": "system", "content": "Be concise."},
        {"role": "user", "content": "Hello"},
    ]

    assert result.content == "Hello back"
    assert result.provider == "mistral"
    assert result.model == "mistral-small-latest"
    assert result.usage.input_tokens == 7
    assert result.usage.output_tokens == 3
    assert result.usage.total_tokens == 10
    assert result.finish_reason == "stop"
    assert result.request_id == "mistral-request-123"
    assert result.latency_ms >= 0


async def test_generate_joins_multiple_system_messages():
    client = SimpleNamespace(
        chat=SimpleNamespace(
            complete_async=AsyncMock(return_value=make_response())
        )
    )
    provider = MistralProvider(client=client)
    request = LLMRequest(
        model="mistral-small-latest",
        messages=(
            LLMMessage(role="system", content="Rule one."),
            LLMMessage(role="system", content="Rule two."),
            LLMMessage(role="user", content="Hello"),
        ),
    )

    await provider.generate(request)

    assert client.chat.complete_async.await_args.kwargs["messages"] == [
        {"role": "system", "content": "Rule one.\n\nRule two."},
        {"role": "user", "content": "Hello"},
    ]


async def test_generate_handles_missing_usage():
    response = make_response(prompt_tokens=None, completion_tokens=None)
    response.usage = None
    client = SimpleNamespace(
        chat=SimpleNamespace(complete_async=AsyncMock(return_value=response))
    )

    result = await MistralProvider(client=client).generate(make_request())

    assert result.usage.input_tokens == 0
    assert result.usage.output_tokens == 0


async def test_generate_uses_requested_model_when_response_model_missing():
    response = make_response(model=None)
    client = SimpleNamespace(
        chat=SimpleNamespace(complete_async=AsyncMock(return_value=response))
    )

    result = await MistralProvider(client=client).generate(make_request())

    assert result.model == "mistral-small-latest"


async def test_generate_handles_missing_content_as_empty_string():
    response = make_response(content=None)
    client = SimpleNamespace(
        chat=SimpleNamespace(complete_async=AsyncMock(return_value=response))
    )

    result = await MistralProvider(client=client).generate(make_request())

    assert result.content == ""


async def test_generate_rejects_unsupported_content_format():
    response = make_response(content=[{"type": "text", "text": "Hello"}])
    client = SimpleNamespace(
        chat=SimpleNamespace(complete_async=AsyncMock(return_value=response))
    )

    with pytest.raises(ValueError, match="unsupported message content"):
        await MistralProvider(client=client).generate(make_request())


async def test_generate_rejects_empty_choices():
    response = make_response(choices=[])
    client = SimpleNamespace(
        chat=SimpleNamespace(complete_async=AsyncMock(return_value=response))
    )

    with pytest.raises(ValueError, match="no completion choices"):
        await MistralProvider(client=client).generate(make_request())


async def test_generate_propagates_sdk_errors():
    client = SimpleNamespace(
        chat=SimpleNamespace(
            complete_async=AsyncMock(side_effect=RuntimeError("SDK failure"))
        )
    )

    with pytest.raises(RuntimeError, match="SDK failure"):
        await MistralProvider(client=client).generate(make_request())


def test_api_key_is_required(monkeypatch):
    settings = get_settings().model_copy(update={"mistral_api_key": None})
    monkeypatch.setattr(
        "api.providers.mistral_provider.get_settings",
        lambda: settings,
    )

    with pytest.raises(ValueError, match="MISTRAL_API_KEY is required"):
        MistralProvider()


def test_api_key_is_passed_to_sdk_without_exposing_it(monkeypatch):
    from pydantic import SecretStr

    settings = get_settings().model_copy(
        update={"mistral_api_key": SecretStr("test-secret-key")}
    )
    captured = {}

    class FakeMistral:
        def __init__(self, *, api_key):
            captured["api_key"] = api_key

    monkeypatch.setattr(
        "api.providers.mistral_provider.get_settings",
        lambda: settings,
    )
    monkeypatch.setattr(
        "api.providers.mistral_provider.Mistral",
        FakeMistral,
    )

    provider = MistralProvider()

    assert captured["api_key"] == "test-secret-key"
    assert "test-secret-key" not in repr(settings.mistral_api_key)
    assert provider.name == "mistral"


async def test_aclose_uses_async_context_exit():
    client = SimpleNamespace(
        __aexit__=AsyncMock(return_value=False)
    )
    provider = MistralProvider(client=client)

    await provider.aclose()

    client.__aexit__.assert_awaited_once_with(None, None, None)
