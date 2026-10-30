"""HTTP tests for execution route safety, validation, and serialization."""

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from api.config import get_settings
from api.database import get_db
from api.auth import get_current_user
import api.routes.execution as execution_routes
from api.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_dependency_overrides(monkeypatch):
    """Restore the app's original dependency overrides after every test."""
    original = app.dependency_overrides.copy()
    monkeypatch.setattr(execution_routes, 'can_read_project', lambda db, user, project_id: True)
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
            "google_auth_enabled": True,
        }
    )
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())


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
    db.get.return_value = SimpleNamespace(
        id=task_id,
        project_id=uuid4(),
    )
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
    task_id = uuid4()
    project_id = uuid4()
    db = MagicMock()
    db.get.side_effect = [
        SimpleNamespace(id=run_id, task_id=task_id),
        SimpleNamespace(id=task_id, project_id=project_id),
    ]
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
def test_execution_read_rejects_missing_bearer_token():
    settings = get_settings().model_copy(
        update={
            "environment": "development",
            "execution_reads_enabled": True,
            "google_auth_enabled": True,
        }
    )
    app.dependency_overrides[get_settings] = lambda: settings

    response = client.get(
        f"/api/v1/execution/tasks/{uuid4()}"
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_task_read_hides_task_from_non_member(monkeypatch):
    _enable_execution_reads()
    task_id = uuid4()
    task = SimpleNamespace(
        id=task_id,
        project_id=uuid4(),
    )
    db = MagicMock()
    db.get.return_value = task
    _mock_db(db)

    monkeypatch.setattr(
        execution_routes,
        "can_read_project",
        lambda db, user, project_id: False,
    )

    response = client.get(
        f"/api/v1/execution/tasks/{task_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "task_not_found"

def _enable_execution_writes():
    settings = get_settings().model_copy(
        update={
            "environment": "development",
            "execution_writes_enabled": True,
            "google_auth_enabled": True,
        }
    )
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())


def test_task_creation_is_hidden_by_default():
    response = client.post(
        "/api/v1/execution/tasks",
        json={
            "project_id": str(uuid4()),
            "objective": "Create a test task",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_task_creation_rejects_missing_bearer_token():
    settings = get_settings().model_copy(
        update={
            "environment": "development",
            "execution_writes_enabled": True,
            "google_auth_enabled": True,
        }
    )
    app.dependency_overrides[get_settings] = lambda: settings

    response = client.post(
        "/api/v1/execution/tasks",
        json={
            "project_id": str(uuid4()),
            "objective": "Create a test task",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_task_creation_rejects_unauthorized_project(monkeypatch):
    _enable_execution_writes()

    from api.services import task_service

    monkeypatch.setattr(
        task_service,
        "can_create_tasks",
        lambda db, user, project_id: False,
    )

    db = MagicMock()
    _mock_db(db)

    response = client.post(
        "/api/v1/execution/tasks",
        json={
            "project_id": str(uuid4()),
            "objective": "Create a restricted task",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "project_access_denied"



def test_task_creation_returns_created_task(monkeypatch):
    _enable_execution_writes()
    project_id = uuid4()
    user_id = uuid4()
    task_id = uuid4()
    now = datetime.now(UTC)

    task = SimpleNamespace(
        id=task_id,
        project_id=project_id,
        created_by=user_id,
        objective="Create an authorized task",
        status="pending",
        input_data={"source": "test"},
        result=None,
        created_at=now,
        updated_at=now,
    )

    def fake_create_task(db, user, project_id, objective, input_data):
        assert user.id == user_id
        assert project_id == task.project_id
        assert objective == task.objective
        assert input_data == task.input_data
        return task

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user_id)
    monkeypatch.setattr(execution_routes, "create_task", fake_create_task)

    db = MagicMock()
    _mock_db(db)

    response = client.post(
        "/api/v1/execution/tasks",
        json={
            "project_id": str(project_id),
            "objective": "Create an authorized task",
            "input_data": {"source": "test"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == str(task_id)
    assert body["project_id"] == str(project_id)
    assert body["created_by"] == str(user_id)
    assert body["objective"] == "Create an authorized task"
    assert body["status"] == "pending"
    assert body["input_data"] == {"source": "test"}
