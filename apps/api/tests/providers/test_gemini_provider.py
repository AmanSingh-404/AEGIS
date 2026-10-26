from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import SecretStr

from api.providers import LLMMessage, LLMRequest, LLMResponse, LLMUsage
from api.providers.gemini_provider import GeminiProvider


pytestmark = pytest.mark.anyio


def make_request(**overrides: object) -> LLMRequest:
    values: dict[str, object] = {
        "model": "gemini-test-model",
        "messages": (
            LLMMessage(role="system", content="Be helpful."),
            LLMMessage(role="user", content="Hello"),
        ),
    }
    values.update(overrides)
    return LLMRequest.model_validate(values)


def make_response(
    *,
    text: str | None = "Hello back",
    prompt_tokens: int | None = 4,
    output_tokens: int | None = 3,
    finish_reason: object = "STOP",
) -> SimpleNamespace:
    return SimpleNamespace(
        text=text,
        usage_metadata=SimpleNamespace(
            prompt_token_count=prompt_tokens,
            candidates_token_count=output_tokens,
        ),
        candidates=[
            SimpleNamespace(finish_reason=finish_reason),
        ],
    )


@pytest.fixture
def mock_client() -> SimpleNamespace:
    generate_content = Mock(return_value=make_response())
    close = Mock()
    return SimpleNamespace(
        models=SimpleNamespace(generate_content=generate_content),
        close=close,
    )


async def test_generate_normalizes_response(mock_client: SimpleNamespace) -> None:
    provider = GeminiProvider(client=mock_client)

    response = await provider.generate(make_request())

    assert isinstance(response, LLMResponse)
    assert response.content == "Hello back"
    assert response.provider == "gemini"
    assert response.model == "gemini-test-model"
    assert response.usage == LLMUsage(input_tokens=4, output_tokens=3)
    assert response.usage.total_tokens == 7
    assert response.finish_reason == "STOP"
    assert response.latency_ms >= 0
    assert response.request_id is None


async def test_generate_converts_messages_and_options(
    mock_client: SimpleNamespace,
) -> None:
    provider = GeminiProvider(client=mock_client)

    await provider.generate(
        make_request(
            messages=(
                LLMMessage(role="system", content="System instruction."),
                LLMMessage(role="user", content="First question."),
                LLMMessage(role="assistant", content="Previous answer."),
                LLMMessage(role="user", content="Follow-up."),
            ),
            temperature=0.7,
            max_tokens=256,
            timeout_seconds=12.5,
        )
    )

    mock_client.models.generate_content.assert_called_once()
    call = mock_client.models.generate_content.call_args
    assert call.kwargs["model"] == "gemini-test-model"

    contents = call.kwargs["contents"]
    assert [content.role for content in contents] == [
        "user",
        "model",
        "user",
    ]
    assert [content.parts[0].text for content in contents] == [
        "First question.",
        "Previous answer.",
        "Follow-up.",
    ]

    config = call.kwargs["config"]
    assert config.system_instruction == "System instruction."
    assert config.temperature == 0.7
    assert config.max_output_tokens == 256
    assert config.http_options.timeout == 12500


async def test_generate_handles_missing_usage(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.models.generate_content.return_value = SimpleNamespace(
        text="Hello",
        usage_metadata=None,
        candidates=[],
    )
    provider = GeminiProvider(client=mock_client)

    response = await provider.generate(make_request())

    assert response.usage == LLMUsage(input_tokens=0, output_tokens=0)
    assert response.finish_reason is None


async def test_generate_handles_partial_usage(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.models.generate_content.return_value = make_response(
        prompt_tokens=5,
        output_tokens=None,
    )
    provider = GeminiProvider(client=mock_client)

    response = await provider.generate(make_request())

    assert response.usage == LLMUsage(input_tokens=5, output_tokens=0)


async def test_generate_handles_missing_text(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.models.generate_content.return_value = make_response(text=None)
    provider = GeminiProvider(client=mock_client)

    response = await provider.generate(make_request())

    assert response.content == ""


async def test_generate_enforces_request_timeout(
    mock_client: SimpleNamespace,
) -> None:
    import time

    def slow_generate_content(**kwargs: object) -> SimpleNamespace:
        time.sleep(0.2)
        return make_response()

    mock_client.models.generate_content.side_effect = slow_generate_content
    provider = GeminiProvider(client=mock_client)

    with pytest.raises(TimeoutError):
        await provider.generate(
            make_request(timeout_seconds=0.01)
        )


async def test_generate_propagates_sdk_errors(
    mock_client: SimpleNamespace,
) -> None:
    mock_client.models.generate_content.side_effect = TimeoutError("simulated timeout")
    provider = GeminiProvider(client=mock_client)

    with pytest.raises(TimeoutError, match="simulated timeout"):
        await provider.generate(make_request())


def test_provider_requires_api_key_without_injected_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "api.providers.gemini_provider.get_settings",
        lambda: SimpleNamespace(gemini_api_key=None),
    )

    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        GeminiProvider()


def test_provider_uses_secret_key_without_exposing_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def __init__(self, *, api_key: str) -> None:
            captured["api_key"] = api_key

        def close(self) -> None:
            pass

    monkeypatch.setattr(
        "api.providers.gemini_provider.get_settings",
        lambda: SimpleNamespace(gemini_api_key=SecretStr("test-gemini-secret")),
    )
    monkeypatch.setattr(
        "api.providers.gemini_provider.genai.Client",
        FakeClient,
    )

    provider = GeminiProvider()

    assert captured["api_key"] == "test-gemini-secret"
    assert "test-gemini-secret" not in repr(provider)


async def test_close_closes_sdk_client(mock_client: SimpleNamespace) -> None:
    provider = GeminiProvider(client=mock_client)

    await provider.aclose()

    mock_client.close.assert_called_once_with()
