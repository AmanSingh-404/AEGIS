from uuid import uuid4

import pytest
from pydantic import ValidationError

from api.routes.task_schemas import CreateTaskRequest


def test_valid_task_request():
    project_id = uuid4()
    request = CreateTaskRequest(
        project_id=project_id,
        objective="  Build a test agent  ",
        input_data={"priority": "high"},
    )

    assert request.project_id == project_id
    assert request.objective == "Build a test agent"
    assert request.input_data == {"priority": "high"}


def test_task_request_defaults_input_data():
    request = CreateTaskRequest(
        project_id=uuid4(),
        objective="Build an agent",
    )

    assert request.input_data == {}


@pytest.mark.parametrize("objective", ["", " ", "   \n\t"])
def test_task_request_rejects_empty_objective(objective):
    with pytest.raises(ValidationError):
        CreateTaskRequest(
            project_id=uuid4(),
            objective=objective,
        )


def test_task_request_rejects_invalid_project_uuid():
    with pytest.raises(ValidationError):
        CreateTaskRequest(
            project_id="not-a-uuid",
            objective="Build an agent",
        )


def test_task_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        CreateTaskRequest(
            project_id=uuid4(),
            objective="Build an agent",
            created_by=str(uuid4()),
        )


def test_task_request_rejects_oversized_input_data():
    with pytest.raises(ValidationError):
        CreateTaskRequest(
            project_id=uuid4(),
            objective="Build an agent",
            input_data={"payload": "x" * 65_536},
        )


def test_task_request_rejects_non_finite_json_numbers():
    with pytest.raises(ValidationError):
        CreateTaskRequest(
            project_id=uuid4(),
            objective="Build an agent",
            input_data={"score": float("nan")},
        )
