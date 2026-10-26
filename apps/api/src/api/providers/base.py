from typing import Protocol, runtime_checkable

from api.providers.schemas import LLMRequest, LLMResponse


@runtime_checkable
class LLMProvider(Protocol):
    """Interface every AEGIS LLM provider adapter must implement."""

    @property
    def name(self) -> str:
        """Return the stable provider identifier."""
        ...

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response using the normalized request contract."""
        ...
