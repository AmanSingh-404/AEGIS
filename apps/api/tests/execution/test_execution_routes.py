"""HTTP tests for execution route safety, validation, and serialization."""

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from api.config import get_settings
from api.database import get_db
from api.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_dependency_overrides():
    """Restore the app's original dependency overrides after every test."""
    original = app.dependency_overrides.copy()
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original)


def _enable_execution_reads():
    settings = get_settings().model_copy(
        update={
            "environment": "development",
            "execution_reads_enabled": True,
        }
    )
    app.dependency_overrides[get_settings] = lambda: settings


def _mock_db(db):
    app.dependency_overrides[get_db] = lambda: db


def test_execution_task_route_is_hidden_by_default():
    response = client.get(
        "/api/v1/execution/tasks/00000000-0000-0000-0000-000000000001"
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_execution_runs_route_is_hidden_by_default():
    response = client.get(
        "/api/v1/execution/tasks/00000000-0000-0000-0000-000000000001/runs"
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_execution_events_route_is_hidden_by_default():
    response = client.get(
        "/api/v1/execution/runs/00000000-0000-0000-0000-000000000001/events"
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_execution_task_route_rejects_invalid_uuid_while_disabled():
    response = client.get("/api/v1/execution/tasks/not-a-uuid")
    assert response.status_code == 404


def test_task_read_returns_not_found_without_database_match():
    _enable_execution_reads()
    db = MagicMock()
    db.get.return_value = None
    _mock_db(db)

    response = client.get(f"/api/v1/execution/tasks/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "task_not_found"


def test_task_read_returns_serialized_task():
    _enable_execution_reads()
    task_id = uuid4()
    now = datetime.now(UTC)
    task = SimpleNamespace(
        id=task_id,
        project_id=uuid4(),
        created_by=uuid4(),
        objective="Test objective",
        status="pending",
        input_data={},
        result=None,
        created_at=now,
        updated_at=now,
    )
    db = MagicMock()
    db.get.return_value = task
    _mock_db(db)

    response = client.get(f"/api/v1/execution/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(task_id)
    assert response.json()["objective"] == "Test objective"


def test_task_runs_returns_serialized_runs():
    _enable_execution_reads()
    task_id = uuid4()
    run_id = uuid4()
    run = SimpleNamespace(
        id=run_id,
        task_id=task_id,
        status="running",
        attempt=1,
        state={},
        started_at=datetime.now(UTC),
        finished_at=None,
        error=None,
    )
    db = MagicMock()
    db.get.return_value = SimpleNamespace(id=task_id)
    db.scalars.return_value.all.return_value = [run]
    _mock_db(db)

    response = client.get(f"/api/v1/execution/tasks/{task_id}/runs")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(run_id)
    assert response.json()[0]["status"] == "running"


def test_run_events_returns_serialized_events():
    _enable_execution_reads()
    run_id = uuid4()
    event = SimpleNamespace(
        id=1,
        run_id=run_id,
        event_type="run_started",
        event_data={"attempt": 1},
        model_id=None,
        tokens_input=None,
        tokens_output=None,
        created_at=datetime.now(UTC),
    )
    db = MagicMock()
    db.get.return_value = SimpleNamespace(id=run_id)
    db.scalars.return_value.all.return_value = [event]
    _mock_db(db)

    response = client.get(f"/api/v1/execution/runs/{run_id}/events")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["event_type"] == "run_started"


def test_run_events_rejects_limit_above_maximum():
    _enable_execution_reads()

    response = client.get(
        f"/api/v1/execution/runs/{uuid4()}/events?limit=201"
    )

    assert response.status_code == 422


def test_task_runs_rejects_limit_above_maximum():
    _enable_execution_reads()

    response = client.get(
        f"/api/v1/execution/tasks/{uuid4()}/runs?limit=101"
    )

    assert response.status_code == 422
