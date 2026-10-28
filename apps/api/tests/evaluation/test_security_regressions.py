"""Security regression tests for AEGIS LLM API behavior."""

from unittest.mock import AsyncMock

import anyio
import httpx

from api.config import Settings, get_settings
from api.main import app
from api.routes.llm import get_llm_service


async def _post_generation() -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.post(
            "/api/v1/llm/generate",
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )


def test_provider_exception_details_are_not_exposed_to_client_or_logs(
    capsys,
) -> None:
    secret_detail = "credential=super-secret-value prompt=private-user-content"
    settings = Settings(_env_file=None, llm_generation_enabled=True)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_settings] = lambda: settings

    service = type("FakeService", (), {})()
    service.generate = AsyncMock(side_effect=RuntimeError(secret_detail))
    service.aclose = AsyncMock()
    service.provider_name = "fake"
    app.dependency_overrides[get_llm_service] = lambda: service

    try:
        response = anyio.run(_post_generation)
        logs = capsys.readouterr().out
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "super-secret-value" not in response.text
    assert "private-user-content" not in response.text
    assert "super-secret-value" not in logs
    assert "private-user-content" not in logs
    assert "RuntimeError" in logs
