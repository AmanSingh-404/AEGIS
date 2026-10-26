"""Tests for configured LLM provider selection."""

import pytest

from api.config import get_settings
from api.providers import (
    GeminiProvider,
    GroqProvider,
    MistralProvider,
    create_llm_provider,
)


@pytest.mark.parametrize(
    ("provider_name", "expected_class"),
    [
        ("groq", GroqProvider),
        ("gemini", GeminiProvider),
        ("mistral", MistralProvider),
    ],
)
def test_factory_creates_requested_provider(
    monkeypatch: pytest.MonkeyPatch,
    provider_name: str,
    expected_class: type,
) -> None:
    monkeypatch.setattr(
        expected_class,
        "__init__",
        lambda self: None,
    )

    provider = create_llm_provider(provider_name)

    assert isinstance(provider, expected_class)


@pytest.mark.parametrize("provider_name", ["", "openrouter", "unknown"])
def test_factory_rejects_unsupported_provider(
    provider_name: str,
) -> None:
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        create_llm_provider(provider_name)


def test_factory_normalizes_provider_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(GroqProvider, "__init__", lambda self: None)

    provider = create_llm_provider(" GROQ ")

    assert isinstance(provider, GroqProvider)


def test_factory_uses_configured_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(get_settings(), "llm_provider", "gemini")
    monkeypatch.setattr(GeminiProvider, "__init__", lambda self: None)

    provider = create_llm_provider()

    assert isinstance(provider, GeminiProvider)


def test_factory_rejects_missing_provider_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(get_settings(), "groq_api_key", None)

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        create_llm_provider("groq")


@pytest.mark.parametrize(
    ("provider_name", "setting_name", "environment_key"),
    [
        ("groq", "groq_api_key", "GROQ_API_KEY"),
        ("gemini", "gemini_api_key", "GEMINI_API_KEY"),
        ("mistral", "mistral_api_key", "MISTRAL_API_KEY"),
    ],
)
def test_factory_rejects_missing_credentials_for_each_provider(
    monkeypatch: pytest.MonkeyPatch,
    provider_name: str,
    setting_name: str,
    environment_key: str,
) -> None:
    monkeypatch.setattr(get_settings(), setting_name, None)

    with pytest.raises(ValueError, match=environment_key):
        create_llm_provider(provider_name)
