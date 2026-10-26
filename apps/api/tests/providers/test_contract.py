import pytest
from pydantic import ValidationError

from api.providers.base import LLMProvider
from api.providers.schemas import LLMMessage, LLMRequest, LLMResponse, LLMUsage


def make_request(**overrides: object) -> LLMRequest:
    values: dict[str, object] = {
        "model": "test-model",
        "messages": (LLMMessage(role="user", content="Hello"),),
    }
    values.update(overrides)
    return LLMRequest.model_validate(values)


def test_request_defaults_and_message() -> None:
    request = make_request()

    assert request.model == "test-model"
    assert request.messages[0].content == "Hello"
    assert request.temperature == 0.2
    assert request.max_tokens == 1024
    assert request.timeout_seconds == 60.0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model", ""),
        ("messages", ()),
        ("temperature", -0.1),
        ("temperature", 2.1),
        ("max_tokens", 0),
        ("timeout_seconds", 0),
        ("timeout_seconds", 601),
    ],
)
def test_invalid_request_values_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        make_request(**{field: value})


def test_usage_total_tokens() -> None:
    usage = LLMUsage(input_tokens=12, output_tokens=8)

    assert usage.total_tokens == 20


def test_response_validates_provider_metadata() -> None:
    response = LLMResponse(
        content="Hello back",
        provider="test-provider",
        model="test-model",
        usage=LLMUsage(input_tokens=3, output_tokens=2),
        finish_reason="stop",
        latency_ms=14.5,
        request_id="req-test-1",
    )

    assert response.usage.total_tokens == 5
    assert response.provider == "test-provider"


def test_response_rejects_negative_usage_and_latency() -> None:
    with pytest.raises(ValidationError):
        LLMUsage(input_tokens=-1, output_tokens=0)

    with pytest.raises(ValidationError):
        LLMResponse(
            content="x",
            provider="test-provider",
            model="test-model",
            usage=LLMUsage(input_tokens=0, output_tokens=0),
            latency_ms=-1,
        )


def test_request_is_immutable() -> None:
    request = make_request()

    with pytest.raises(ValidationError):
        request.model = "changed"  # type: ignore[misc]


def test_provider_protocol_requires_name_and_generate() -> None:
    class ExampleProvider:
        name = "example"

        async def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                content="ok",
                provider=self.name,
                model=request.model,
                usage=LLMUsage(input_tokens=1, output_tokens=1),
                latency_ms=1.0,
            )

    provider = ExampleProvider()

    assert isinstance(provider, LLMProvider)


def test_response_rejects_empty_provider_and_model_names() -> None:
    base_values = {
        "content": "ok",
        "provider": "fake",
        "model": "test-model",
        "usage": LLMUsage(input_tokens=1, output_tokens=1),
        "latency_ms": 1.0,
    }

    with pytest.raises(ValidationError):
        LLMResponse(**{**base_values, "provider": ""})

    with pytest.raises(ValidationError):
        LLMResponse(**{**base_values, "model": ""})
