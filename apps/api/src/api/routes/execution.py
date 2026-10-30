"""Read-only HTTP endpoints for execution resources."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.config import Settings, get_settings
from api.database import get_db
from api.auth import get_current_user
from api.models.identity import User
from api.routes.task_schemas import CreateTaskRequest
from api.services.task_service import (
    ProjectTaskAccessDenied,
    create_task,
)
from api.services.project_access_service import can_read_project
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
    current_user: Annotated[User, Depends(get_current_user)],
) -> Task:
    """Return a task by its identifier."""
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "task_not_found", "message": "Task not found."},
        )
    if not can_read_project(db, current_user, task.project_id):
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
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[Run]:
    """Return the most recent runs for a task."""
    task = db.get(Task, task_id)
    if task is None or not can_read_project(db, current_user, task.project_id):
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
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[RunEvent]:
    """Return lifecycle events for a run in chronological order."""
    run = db.get(Run, run_id)
    task = db.get(Task, run.task_id) if run is not None else None
    if task is None or not can_read_project(db, current_user, task.project_id):
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


def require_execution_writes(
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Allow execution writes only when explicitly enabled in development."""
    if (
        not getattr(settings, "execution_writes_enabled", False)
        or settings.environment != "development"
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Endpoint not found."},
        )

@router.post(
    "/tasks",
    response_model=ExecutionTaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_execution_writes)],
)
def create_task_endpoint(
    request: CreateTaskRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Task:
    """Create a task for a project the authenticated user can modify."""
    try:
        return create_task(
            db=db,
            user=current_user,
            project_id=request.project_id,
            objective=request.objective,
            input_data=request.input_data,
        )
    except ProjectTaskAccessDenied:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "project_access_denied",
                "message": "You cannot create tasks in this project.",
            },
        ) from None
