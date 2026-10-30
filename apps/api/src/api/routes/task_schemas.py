import json
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


MAX_INPUT_DATA_BYTES = 65_536


class CreateTaskRequest(BaseModel):
    """Validated request body for task creation."""

    model_config = ConfigDict(extra="forbid")

    project_id: UUID
    objective: str = Field(min_length=1, max_length=10_000)
    input_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Objective cannot be empty or whitespace")
        return value

    @field_validator("input_data")
    @classmethod
    def validate_input_data_size(
        cls,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            serialized = json.dumps(
                value,
                allow_nan=False,
                separators=(",", ":"),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Input data must contain valid JSON values") from exc

        if len(serialized.encode("utf-8")) > MAX_INPUT_DATA_BYTES:
            raise ValueError("Input data exceeds the 65536-byte limit")

        return value
