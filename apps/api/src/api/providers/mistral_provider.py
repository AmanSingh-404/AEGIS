import time
from typing import Any

from mistralai.client import Mistral

from api.config import get_settings
from api.providers.schemas import LLMRequest, LLMResponse, LLMUsage


class MistralProvider:
    """Mistral adapter implementing the AEGIS LLM response contract."""

    name = "mistral"

    def __init__(self, client: Any | None = None) -> None:
        if client is None:
            api_key = get_settings().mistral_api_key
            if api_key is None or not api_key.get_secret_value().strip():
                raise ValueError(
                    "MISTRAL_API_KEY is required to initialize MistralProvider."
                )

            client = Mistral(api_key=api_key.get_secret_value())

        self._client = client

    async def generate(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()

        system_parts = [
            message.content for message in request.messages
            if message.role == "system"
        ]
        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
            if message.role != "system"
        ]

        if system_parts:
            messages.insert(
                0,
                {"role": "system", "content": "\n\n".join(system_parts)},
            )

        response = await self._client.chat.complete_async(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            timeout_ms=int(request.timeout_seconds * 1000),
        )

        choices = response.choices or []
        if not choices:
            raise ValueError("Mistral returned no completion choices.")

        choice = choices[0]
        message_content = choice.message.content

        if message_content is None:
            content = ""
        elif isinstance(message_content, str):
            content = message_content
        else:
            raise ValueError("Mistral returned an unsupported message content format.")

        usage = response.usage
        input_tokens = usage.prompt_tokens if usage is not None else 0
        output_tokens = usage.completion_tokens if usage is not None else 0

        return LLMResponse(
            content=content,
            provider=self.name,
            model=response.model or request.model,
            usage=LLMUsage(
                input_tokens=input_tokens or 0,
                output_tokens=output_tokens or 0,
            ),
            finish_reason=choice.finish_reason,
            latency_ms=(time.perf_counter() - started) * 1000,
            request_id=response.id,
        )

    async def aclose(self) -> None:
        """Close the underlying asynchronous Mistral client."""
        await self._client.__aexit__(None, None, None)
