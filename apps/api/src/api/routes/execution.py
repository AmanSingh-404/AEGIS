"""Read-only HTTP endpoints for execution resources."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.config import Settings, get_settings
from api.database import get_db
from api.models.execution import Run, RunEvent, Task
from api.routes.execution_schemas import (
    ExecutionRunEventResponse,
    ExecutionRunResponse,
    ExecutionTaskResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/execution", tags=["Execution"])


def require_execution_reads(
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Keep execution reads unavailable outside explicitly enabled development."""
    if (
        not getattr(settings, "execution_reads_enabled", False)
        or settings.environment != "development"
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Endpoint not found."},
        )


@router.get(
    "/tasks/{task_id}",
    response_model=ExecutionTaskResponse,
    dependencies=[Depends(require_execution_reads)],
)
def get_task(
    task_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> Task:
    """Return a task by its identifier."""
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "task_not_found", "message": "Task not found."},
        )
    return task


@router.get(
    "/tasks/{task_id}/runs",
    response_model=list[ExecutionRunResponse],
    dependencies=[Depends(require_execution_reads)],
)
def list_task_runs(
    task_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[Run]:
    """Return the most recent runs for a task."""
    if db.get(Task, task_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "task_not_found", "message": "Task not found."},
        )

    statement = (
        select(Run)
        .where(Run.task_id == task_id)
        .order_by(Run.attempt.desc(), Run.id.desc())
        .limit(limit)
    )
    return list(db.scalars(statement).all())


@router.get(
    "/runs/{run_id}/events",
    response_model=list[ExecutionRunEventResponse],
    dependencies=[Depends(require_execution_reads)],
)
def list_run_events(
    run_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[RunEvent]:
    """Return lifecycle events for a run in chronological order."""
    if db.get(Run, run_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "run_not_found", "message": "Run not found."},
        )

    statement = (
        select(RunEvent)
        .where(RunEvent.run_id == run_id)
        .order_by(RunEvent.created_at.asc(), RunEvent.id.asc())
        .limit(limit)
    )
    return list(db.scalars(statement).all())
