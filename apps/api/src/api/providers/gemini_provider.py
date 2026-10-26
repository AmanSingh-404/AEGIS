import asyncio
import time
from typing import Any

from google import genai
from google.genai import types

from api.config import get_settings
from api.providers.schemas import LLMRequest, LLMResponse, LLMUsage


class GeminiProvider:
    """Google Gemini adapter implementing the AEGIS LLM response contract."""

    name = "gemini"

    def __init__(self, client: Any | None = None) -> None:
        if client is None:
            api_key = get_settings().gemini_api_key
            if api_key is None or not api_key.get_secret_value().strip():
                raise ValueError(
                    "GEMINI_API_KEY is required to initialize GeminiProvider."
                )

            client = genai.Client(api_key=api_key.get_secret_value())

        self._client = client

    async def generate(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()

        system_parts: list[str] = []
        contents: list[types.Content] = []

        for message in request.messages:
            if message.role == "system":
                system_parts.append(message.content)
                continue

            role = "model" if message.role == "assistant" else "user"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=message.content)],
                )
            )

        config = types.GenerateContentConfig(
            system_instruction="\n\n".join(system_parts) or None,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
            http_options=types.HttpOptions(
                timeout=int(request.timeout_seconds * 1000)
            ),
        )

        response = await asyncio.wait_for(
            asyncio.to_thread(
                self._client.models.generate_content,
                model=request.model,
                contents=contents,
                config=config,
            ),
            timeout=request.timeout_seconds,
        )

        usage_metadata = response.usage_metadata
        input_tokens = (
            usage_metadata.prompt_token_count
            if usage_metadata is not None
            and usage_metadata.prompt_token_count is not None
            else 0
        )
        output_tokens = (
            usage_metadata.candidates_token_count
            if usage_metadata is not None
            and usage_metadata.candidates_token_count is not None
            else 0
        )

        candidates = response.candidates or []
        finish_reason = (
            str(candidates[0].finish_reason)
            if candidates and candidates[0].finish_reason is not None
            else None
        )

        return LLMResponse(
            content=response.text or "",
            provider=self.name,
            model=request.model,
            usage=LLMUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
            finish_reason=finish_reason,
            latency_ms=(time.perf_counter() - started) * 1000,
            request_id=None,
        )

    async def aclose(self) -> None:
        """Close the synchronous Google client without blocking the event loop."""
        await asyncio.to_thread(self._client.close)
