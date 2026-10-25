import anyio
from unittest.mock import patch

import httpx
from sqlalchemy.exc import SQLAlchemyError

from api.main import app


async def request(method: str, path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.request(method, path)


def test_liveness_returns_ok() -> None:
    response = anyio.run(request, "GET", "/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_returns_ready_when_database_is_available() -> None:
    with patch("api.main.engine.connect") as mock_connect:
        response = anyio.run(request, "GET", "/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}
    mock_connect.assert_called_once()


def test_readiness_returns_503_when_database_fails() -> None:
    with patch(
        "api.main.engine.connect",
        side_effect=SQLAlchemyError("Simulated database failure"),
    ):
        response = anyio.run(request, "GET", "/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "status": "not_ready",
            "dependency": "postgres",
        }
    }
