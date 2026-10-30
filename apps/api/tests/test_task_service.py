from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

import api.services.task_service as task_service
from api.services.task_service import (
    ProjectTaskAccessDenied,
    create_task,
)


@pytest.fixture
def task_context(monkeypatch):
    db = MagicMock()
    user = SimpleNamespace(id=uuid4())
    project_id = uuid4()

    monkeypatch.setattr(
        task_service,
        "can_create_tasks",
        lambda db, user, project_id: True,
    )

    return db, user, project_id


def test_create_task_uses_authenticated_user(task_context):
    db, user, project_id = task_context
    db.refresh.side_effect = lambda task: None

    result = create_task(
        db,
        user,
        project_id,
        "Build an agent",
        {"priority": "high"},
    )

    created_task = db.add.call_args.args[0]

    assert result is created_task
    assert created_task.created_by == user.id
    assert created_task.project_id == project_id
    assert created_task.objective == "Build an agent"
    assert created_task.input_data == {"priority": "high"}
    assert created_task.status == "pending"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_task)


def test_create_task_denies_unauthorized_project(monkeypatch):
    db = MagicMock()
    user = SimpleNamespace(id=uuid4())

    monkeypatch.setattr(
        task_service,
        "can_create_tasks",
        lambda db, user, project_id: False,
    )

    with pytest.raises(ProjectTaskAccessDenied):
        create_task(
            db,
            user,
            uuid4(),
            "Build an agent",
            {},
        )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_create_task_rolls_back_when_commit_fails(task_context):
    db, user, project_id = task_context
    db.commit.side_effect = RuntimeError("database failure")

    with pytest.raises(RuntimeError):
        create_task(
            db,
            user,
            project_id,
            "Build an agent",
            {},
        )

    db.rollback.assert_called_once()


def test_create_task_rolls_back_when_refresh_fails(task_context):
    db, user, project_id = task_context
    db.refresh.side_effect = RuntimeError("refresh failure")

    with pytest.raises(RuntimeError):
        create_task(
            db,
            user,
            project_id,
            "Build an agent",
            {},
        )

    db.commit.assert_called_once()
    db.rollback.assert_called_once()
