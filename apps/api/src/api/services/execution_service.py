"""Controlled lifecycle operations for AEGIS task runs."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from api.models.execution import Run, RunEvent, Task


class InvalidRunTransition(ValueError):
    """Raised when a run cannot move to the requested status."""


_ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"running", "failed", "cancelled"}),
    "running": frozenset(
        {"awaiting_approval", "completed", "failed", "cancelled"}
    ),
    "awaiting_approval": frozenset({"running", "failed", "cancelled"}),
    "completed": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}

_TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled"})


class ExecutionService:
    """Manage run lifecycle changes using a caller-provided DB session."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def start_run(self, task_id: UUID) -> Run:
        """Create and start a run for a pending task."""
        try:
            task = self._db.get(Task, task_id, with_for_update=True)

            if task is None:
                raise LookupError("Task not found")

            if task.status != "pending":
                raise InvalidRunTransition(
                    f"Cannot start a run for a task in status '{task.status}'"
                )

            run = Run(
                id=uuid4(),
                task_id=task.id,
                status="running",
                attempt=1,
                state={},
                started_at=datetime.now(UTC),
            )
            task.status = "running"

            self._db.add(run)
            self._db.flush()
            self._db.add(
                RunEvent(
                    run_id=run.id,
                    event_type="run_started",
                    event_data={"attempt": run.attempt},
                )
            )
            self._db.commit()
            self._db.refresh(run)
            return run
        except Exception:
            self._db.rollback()
            raise

    def transition_run(
        self,
        run_id: UUID,
        target_status: str,
        *,
        event_data: dict[str, Any] | None = None,
    ) -> Run:
        """Transition a run and record the corresponding lifecycle event."""
        try:
            # Read the run to validate the requested transition and discover
            # its task before acquiring locks.
            run_ref = self._db.get(Run, run_id)
            if run_ref is None:
                raise LookupError("Run not found")

            allowed = _ALLOWED_TRANSITIONS.get(run_ref.status)
            if allowed is None or target_status not in allowed:
                raise InvalidRunTransition(
                    f"Cannot transition run from '{run_ref.status}' "
                    f"to '{target_status}'"
                )

            task = self._db.get(
                Task, run_ref.task_id, with_for_update=True
            )
            if task is None:
                raise LookupError("Task not found for run")

            # Acquire the run lock only after the task lock.
            run = self._db.get(Run, run_id, with_for_update=True)
            if run is None:
                raise LookupError("Run not found")

            if run.task_id != task.id:
                raise InvalidRunTransition(
                    "Run task relationship changed during transition"
                )

            # Revalidate after acquiring locks because the initial read
            # may have become stale while waiting for the task lock.
            allowed = _ALLOWED_TRANSITIONS.get(run.status)
            if allowed is None or target_status not in allowed:
                raise InvalidRunTransition(
                    f"Cannot transition run from '{run.status}' "
                    f"to '{target_status}'"
                )

            expected_task_status = (
                "awaiting_approval"
                if run.status == "awaiting_approval"
                else "running"
            )
            if task.status != expected_task_status:
                raise InvalidRunTransition(
                    "Task status conflicts with the run's current status"
                )

            previous_status = run.status
            run.status = target_status

            if target_status == "running" and run.started_at is None:
                run.started_at = datetime.now(UTC)

            if target_status in _TERMINAL_STATUSES:
                run.finished_at = datetime.now(UTC)

            if target_status == "awaiting_approval":
                task.status = "awaiting_approval"
            elif target_status == "running":
                task.status = "running"
            elif target_status in _TERMINAL_STATUSES:
                task.status = target_status

            safe_event_data: dict[str, Any] = {
                "from_status": previous_status,
                "to_status": target_status,
            }
            if event_data:
                unknown_keys = set(event_data) - {"summary"}
                if unknown_keys:
                    raise ValueError(
                        "Unsupported lifecycle event detail fields"
                    )

                summary = event_data.get("summary")
                if summary is not None:
                    if not isinstance(summary, str) or len(summary) > 500:
                        raise ValueError(
                            "Lifecycle event summary must be a string "
                            "of at most 500 characters"
                        )
                    safe_event_data["details"] = {"summary": summary}

            self._db.add(
                RunEvent(
                    run_id=run.id,
                    event_type=f"run_{target_status}",
                    event_data=safe_event_data,
                )
            )
            self._db.commit()
            self._db.refresh(run)
            return run
        except Exception:
            self._db.rollback()
            raise
