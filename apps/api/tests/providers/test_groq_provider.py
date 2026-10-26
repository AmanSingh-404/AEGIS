from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import SecretStr

from api.config import get_settings
from api.providers import LLMMessage, LLMRequest, LLMResponse, LLMUsage
from api.providers.groq_provider import GroqProvider


pytestmark = pytest.mark.anyio


def make_request(**overrides: object) -> LLMRequest:
    values: dict[str, object] = {
        "model": "test-model",
        "messages": (
            LLMMessage(role="system", content="Be helpful."),
            LLMMessage(role="user", content="Hello"),
        ),
    }
    values.update(overrides)
    return LLMRequest.model_validate(values)


_DEFAULT_USAGE = object()


def make_completion(
    *,
    content: str | None = "Hello back",
    usage: object = _DEFAULT_USAGE,
    finish_reason: str = "stop",
    model: str = "resolved-model",
    request_id: str = "req-test-1",
    choices: list[object] | None = None,
) -> SimpleNamespace:
    if choices is None:
        choices = [
            SimpleNamespace(
                message=SimpleNamespace(content=content),
                finish_reason=finish_reason,
            )
        ]

    if usage is _DEFAULT_USAGE:
        usage = SimpleNamespace(prompt_tokens=3, completion_tokens=2)

    return SimpleNamespace(
        choices=choices,
        usage=usage,
        model=model,
        id=request_id,
    )


@pytest.fixture
def mock_client() -> SimpleNamespace:
    create = AsyncMock(
        return_value=make_completion()
    )
    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create)
        ),
        close=AsyncMock(),
    )


async def test_generate_normalizes_response(mock_client: SimpleNamespace) -> None:
    provider = GroqProvider(client=mock_client)  # type: ignore[arg-type]

    response = await provider.generate(make_request())

    assert isinstance(response, LLMResponse)
    assert response.content == "Hello back"
    assert response.provider == "groq"
    assert response.model == "resolved-model"
    assert response.usage == LLMUsage(input_tokens=3, output_tokens=2)
    assert response.usage.total_tokens == 5
    assert response.finish_reason == "stop"
    assert response.request_id == "req-test-1"
    assert response.latency_ms >= 0


async def test_generate_sends_normalized_request(
    mock_client: SimpleNamespace,
) -> None:
    provider = GroqProvider(client=mock_client)  # type: ignore[arg-type]
    request = make_request(timeout_seconds=12.5, max_tokens=256, temperature=0.7)

    await provider.generate(request)

    mock_client.chat.completions.create.assert_awaited_once_with(
        model="test-model",
        messages=[
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": "Hello"},
        ],
        temperature=0.7,
        max_tokens=256,
        timeout=12.5,
    )


async def test_generate_handles_missing_usage(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.chat.completions.create.return_value = make_completion(usage=None)
    provider = GroqProvider(client=mock_client)  # type: ignore[arg-type]

    response = await provider.generate(make_request())

    assert response.usage.input_tokens == 0
    assert response.usage.output_tokens == 0


async def test_generate_handles_missing_content(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.chat.completions.create.return_value = make_completion(content=None)
    provider = GroqProvider(client=mock_client)  # type: ignore[arg-type]

    response = await provider.generate(make_request())

    assert response.content == ""


async def test_generate_rejects_empty_choices(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.chat.completions.create.return_value = make_completion(choices=[])
    provider = GroqProvider(client=mock_client)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="no completion choices"):
        await provider.generate(make_request())


async def test_generate_propagates_sdk_errors(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.chat.completions.create.side_effect = TimeoutError("simulated timeout")
    provider = GroqProvider(client=mock_client)  # type: ignore[arg-type]

    with pytest.raises(TimeoutError, match="simulated timeout"):
        await provider.generate(make_request())


def test_provider_requires_api_key_when_client_not_injected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "api.providers.groq_provider.get_settings",
        lambda: SimpleNamespace(groq_api_key=None),
    )

    with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
        GroqProvider()


def test_provider_uses_secret_key_without_exposing_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeAsyncGroq:
        def __init__(self, *, api_key: str) -> None:
            captured["api_key"] = api_key

        async def close(self) -> None:
            return None

    monkeypatch.setattr(
        "api.providers.groq_provider.get_settings",
        lambda: SimpleNamespace(groq_api_key=SecretStr("test-secret")),
    )
    monkeypatch.setattr(
        "api.providers.groq_provider.AsyncGroq",
        FakeAsyncGroq,
    )

    provider = GroqProvider()

    assert captured["api_key"] == "test-secret"
    assert "test-secret" not in repr(provider)


async def test_close_closes_sdk_client(mock_client: SimpleNamespace) -> None:
    provider = GroqProvider(client=mock_client)  # type: ignore[arg-type]

    await provider.aclose()

    mock_client.close.assert_awaited_once()
