"""Unit tests for the controlled execution service."""

from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from api.models.execution import Run, RunEvent, Task
from api.services.execution_service import (
    ExecutionService,
    InvalidRunTransition,
)


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    return ExecutionService(db)


def test_start_run_creates_running_run_and_event(service, db):
    task_id = uuid4()
    task = SimpleNamespace(id=task_id, status="pending")
    db.get.return_value = task

    run = service.start_run(task_id)

    assert isinstance(run, Run)
    assert run.id is not None
    assert run.task_id == task_id
    assert run.status == "running"
    assert run.attempt == 1
    assert run.started_at is not None
    assert task.status == "running"

    added = [call.args[0] for call in db.add.call_args_list]
    assert any(isinstance(item, Run) for item in added)
    event = next(item for item in added if isinstance(item, RunEvent))
    assert event.event_type == "run_started"
    assert event.event_data == {"attempt": 1}

    db.flush.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(run)


def test_start_run_rejects_missing_task(service, db):
    db.get.return_value = None

    with pytest.raises(LookupError, match="Task not found"):
        service.start_run(uuid4())

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_start_run_rejects_task_that_is_not_pending(service, db):
    task = SimpleNamespace(id=uuid4(), status="running")
    db.get.return_value = task

    with pytest.raises(InvalidRunTransition, match="Cannot start a run"):
        service.start_run(task.id)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_transition_run_marks_completed_and_records_event(service, db):
    task_id = uuid4()
    run = SimpleNamespace(
        id=uuid4(),
        task_id=task_id,
        status="running",
        started_at=None,
        finished_at=None,
    )
    task = SimpleNamespace(id=task_id, status="running")
    db.get.side_effect = [run, task, run]

    result = service.transition_run(
        run.id,
        "completed",
        event_data={"summary": "test completed"},
    )

    assert result is run
    assert run.status == "completed"
    assert run.finished_at is not None
    assert task.status == "completed"

    added = [call.args[0] for call in db.add.call_args_list]
    event = next(item for item in added if isinstance(item, RunEvent))
    assert event.event_type == "run_completed"
    assert event.event_data == {
        "from_status": "running",
        "to_status": "completed",
        "details": {"summary": "test completed"},
    }

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(run)


def test_transition_run_rejects_invalid_transition(service, db):
    run = SimpleNamespace(
        id=uuid4(),
        task_id=uuid4(),
        status="completed",
        started_at=None,
        finished_at=None,
    )
    db.get.return_value = run

    with pytest.raises(InvalidRunTransition, match="Cannot transition run"):
        service.transition_run(run.id, "running")

    db.commit.assert_not_called()


def test_transition_run_rejects_missing_run(service, db):
    db.get.return_value = None

    with pytest.raises(LookupError, match="Run not found"):
        service.transition_run(uuid4(), "completed")

    db.commit.assert_not_called()


def test_transition_run_rejects_missing_task(service, db):
    run = SimpleNamespace(
        id=uuid4(),
        task_id=uuid4(),
        status="running",
        started_at=None,
        finished_at=None,
    )
    db.get.side_effect = [run, None]

    with pytest.raises(LookupError, match="Task not found for run"):
        service.transition_run(run.id, "completed")

    db.commit.assert_not_called()


def test_transition_to_awaiting_approval_updates_task(service, db):
    task_id = uuid4()
    run = SimpleNamespace(
        id=uuid4(),
        task_id=task_id,
        status="running",
        started_at=None,
        finished_at=None,
    )
    task = SimpleNamespace(id=task_id, status="running")
    db.get.side_effect = [run, task, run]

    service.transition_run(run.id, "awaiting_approval")

    assert run.status == "awaiting_approval"
    assert task.status == "awaiting_approval"
    db.commit.assert_called_once()


def test_transition_rejects_unknown_target_status(service, db):
    run = SimpleNamespace(
        id=uuid4(),
        task_id=uuid4(),
        status="running",
        started_at=None,
        finished_at=None,
    )
    db.get.return_value = run

    with pytest.raises(InvalidRunTransition):
        service.transition_run(run.id, "unknown-status")

    db.commit.assert_not_called()


def test_start_run_rolls_back_when_commit_fails(service, db):
    task = SimpleNamespace(id=uuid4(), status="pending")
    db.get.return_value = task
    db.commit.side_effect = RuntimeError("simulated database failure")

    with pytest.raises(RuntimeError, match="simulated database failure"):
        service.start_run(task.id)

    db.rollback.assert_called_once()


def test_transition_run_rolls_back_when_commit_fails(service, db):
    task_id = uuid4()
    run = SimpleNamespace(
        id=uuid4(),
        task_id=task_id,
        status="running",
        started_at=None,
        finished_at=None,
    )
    task = SimpleNamespace(id=task_id, status="running")
    db.get.side_effect = [run, task, run]
    db.commit.side_effect = RuntimeError("simulated database failure")

    with pytest.raises(RuntimeError, match="simulated database failure"):
        service.transition_run(run.id, "completed")

    db.rollback.assert_called_once()


def test_transition_rejects_unapproved_event_data(service, db):
    task_id = uuid4()
    run = SimpleNamespace(
        id=uuid4(),
        task_id=task_id,
        status="running",
        started_at=None,
        finished_at=None,
    )
    task = SimpleNamespace(id=task_id, status="running")
    db.get.side_effect = [run, task, run]

    with pytest.raises(ValueError, match="Unsupported lifecycle event detail fields"):
        service.transition_run(
            run.id,
            "completed",
            event_data={"prompt": "private user content"},
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_transition_rejects_overlong_event_summary(service, db):
    task_id = uuid4()
    run = SimpleNamespace(
        id=uuid4(),
        task_id=task_id,
        status="running",
        started_at=None,
        finished_at=None,
    )
    task = SimpleNamespace(id=task_id, status="running")
    db.get.side_effect = [run, task, run]

    with pytest.raises(ValueError, match="at most 500 characters"):
        service.transition_run(
            run.id,
            "completed",
            event_data={"summary": "x" * 501},
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
