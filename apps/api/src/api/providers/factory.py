"""Factory for creating configured LLM provider adapters."""

from api.config import get_settings
from api.providers.base import LLMProvider
from api.providers.gemini_provider import GeminiProvider
from api.providers.groq_provider import GroqProvider
from api.providers.mistral_provider import MistralProvider


def create_llm_provider(provider_name: str | None = None) -> LLMProvider:
    """Create an LLM provider using an explicit name or application settings.

    Raises:
        ValueError: If the provider name is unsupported or its API key is missing.
    """
    settings = get_settings()
    selected_provider = (
        provider_name if provider_name is not None else settings.llm_provider
    ).strip().lower()

    providers: dict[str, type[LLMProvider]] = {
        "groq": GroqProvider,
        "gemini": GeminiProvider,
        "mistral": MistralProvider,
    }

    provider_class = providers.get(selected_provider)
    if provider_class is None:
        supported = ", ".join(sorted(providers))
        raise ValueError(
            f"Unsupported LLM provider '{selected_provider}'. "
            f"Supported providers: {supported}."
        )

    return provider_class()
