"""Validated HTTP schemas for execution lifecycle resources."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExecutionTaskResponse(BaseModel):
    """Public representation of a task."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    project_id: UUID
    created_by: UUID
    objective: str
    status: str
    input_data: dict[str, Any]
    result: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class ExecutionRunResponse(BaseModel):
    """Public representation of a run."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    task_id: UUID
    status: str
    attempt: int
    state: dict[str, Any]
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: dict[str, Any] | None = None


class ExecutionRunEventResponse(BaseModel):
    """Public representation of a run lifecycle event."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    run_id: UUID
    event_type: str
    event_data: dict[str, Any]
    model_id: UUID | None = None
    tokens_input: int | None = Field(default=None, ge=0)
    tokens_output: int | None = Field(default=None, ge=0)
    created_at: datetime
