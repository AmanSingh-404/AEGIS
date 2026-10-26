from sqlalchemy import BigInteger, Numeric, UniqueConstraint

from api.models import Base, Model, Run, RunEvent, Task


def test_execution_models_register_expected_tables() -> None:
    assert {"tasks", "runs", "models", "run_events"} <= set(
        Base.metadata.tables
    )


def test_task_status_constraint_and_indexes() -> None:
    table = Task.__table__

    assert any(
        constraint.name == "chk_tasks_status"
        for constraint in table.constraints
    )
    assert {"idx_tasks_project", "idx_tasks_creator"} == {
        index.name for index in table.indexes
    }
    assert table.c.input_data.server_default is not None


def test_run_constraints_and_task_foreign_key() -> None:
    table = Run.__table__

    assert any(
        constraint.name == "chk_runs_status"
        for constraint in table.constraints
    )
    assert any(
        fk.target_fullname == "tasks.id"
        for fk in table.c.task_id.foreign_keys
    )
    assert table.c.attempt.server_default is not None


def test_model_registry_unique_provider_and_model_name() -> None:
    table = Model.__table__

    assert any(
        isinstance(constraint, UniqueConstraint)
        and {column.name for column in constraint.columns}
        == {"provider", "model_name"}
        for constraint in table.constraints
    )


def test_run_event_identity_type_cost_precision_and_indexes() -> None:
    table = RunEvent.__table__

    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert table.c.id.autoincrement is True
    assert isinstance(table.c.estimated_cost.type, Numeric)
    assert table.c.estimated_cost.type.precision == 14
    assert table.c.estimated_cost.type.scale == 8
    assert {
        "idx_run_events_run_time",
        "idx_run_events_model",
    } == {index.name for index in table.indexes}
