from unittest.mock import MagicMock, patch

import anyio
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


def test_database_session_endpoint_uses_injected_session() -> None:
    mock_session = MagicMock()
    app.dependency_overrides.clear()
    app.dependency_overrides.clear()
    from api.database import get_db

    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = anyio.run(request, "GET", "/api/v1/health/db-session")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_session.execute.assert_called_once()


def test_database_session_endpoint_returns_503_on_query_failure() -> None:
    mock_session = MagicMock()
    mock_session.execute.side_effect = SQLAlchemyError("Simulated query failure")
    from api.database import get_db

    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = anyio.run(request, "GET", "/api/v1/health/db-session")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "status": "not_ready",
            "dependency": "postgres",
        }
    }
