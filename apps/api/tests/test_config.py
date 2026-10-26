"""Tests for central application configuration."""

import pytest
from pydantic import ValidationError

from api.config import Settings


def test_llm_provider_defaults_to_groq() -> None:
    settings = Settings(_env_file=None)

    assert settings.llm_provider == "groq"


@pytest.mark.parametrize("provider", ["groq", "gemini", "mistral"])
def test_supported_llm_providers_are_accepted(provider: str) -> None:
    settings = Settings(_env_file=None, llm_provider=provider)

    assert settings.llm_provider == provider


@pytest.mark.parametrize("provider", ["", "openrouter", "unknown", "Groq "])
def test_unsupported_llm_provider_is_rejected(provider: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_provider=provider)


def test_provider_credentials_are_optional() -> None:
    settings = Settings(
        _env_file=None,
        groq_api_key=None,
        gemini_api_key=None,
        mistral_api_key=None,
    )

    assert settings.groq_api_key is None
    assert settings.gemini_api_key is None
    assert settings.mistral_api_key is None


def test_provider_secret_is_not_rendered_in_plain_text() -> None:
    secret_value = "test-secret-do-not-leak"
    settings = Settings(_env_file=None, groq_api_key=secret_value)

    assert secret_value not in str(settings.groq_api_key)
    assert secret_value not in repr(settings.groq_api_key)
