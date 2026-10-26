import time
from groq import AsyncGroq
from groq.types.chat import ChatCompletion

from api.config import get_settings
from api.providers.base import LLMProvider
from api.providers.schemas import LLMRequest, LLMResponse, LLMUsage


class GroqProvider:
    """Groq adapter implementing the AEGIS provider contract."""

    name = "groq"

    def __init__(self, client: AsyncGroq | None = None) -> None:
        if client is None:
            api_key = get_settings().groq_api_key
            if api_key is None or not api_key.get_secret_value().strip():
                raise ValueError("GROQ_API_KEY is required to initialize GroqProvider.")

            client = AsyncGroq(api_key=api_key.get_secret_value())

        self._client = client

    async def generate(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()

        completion: ChatCompletion = await self._client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            timeout=request.timeout_seconds,
        )

        if not completion.choices:
            raise ValueError("Groq returned no completion choices.")

        choice = completion.choices[0]
        message_content = choice.message.content
        if message_content is None:
            content = ""
        elif isinstance(message_content, str):
            content = message_content
        else:
            raise ValueError("Groq returned an unsupported message content format.")

        usage = completion.usage
        input_tokens = usage.prompt_tokens if usage is not None else 0
        output_tokens = usage.completion_tokens if usage is not None else 0

        return LLMResponse(
            content=content,
            provider=self.name,
            model=completion.model or request.model,
            usage=LLMUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
            finish_reason=choice.finish_reason,
            latency_ms=(time.perf_counter() - started) * 1000,
            request_id=completion.id,
        )

    async def aclose(self) -> None:
        """Close the underlying async client."""
        await self._client.close()
