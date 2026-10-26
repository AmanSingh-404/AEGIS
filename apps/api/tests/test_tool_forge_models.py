from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB

from api.models import CapabilityGap, ToolCandidate


def test_capability_gap_columns_defaults_and_indexes() -> None:
    table = CapabilityGap.__table__

    assert set(table.columns.keys()) == {
        "id",
        "task_id",
        "run_id",
        "description",
        "task_context",
        "status",
        "priority_score",
        "created_at",
        "resolved_at",
    }

    assert isinstance(table.c.task_context.type, JSONB)
    assert table.c.task_context.server_default is not None
    assert str(table.c.status.server_default.arg) == "'detected'"

    foreign_keys = {
        (fk.parent.name, fk.target_fullname)
        for fk in table.foreign_keys
    }
    assert foreign_keys == {
        ("task_id", "tasks.id"),
        ("run_id", "runs.id"),
    }

    assert {index.name for index in table.indexes} == {
        "idx_capability_gaps_status",
        "idx_capability_gaps_task",
        "idx_capability_gaps_run",
    }


def test_capability_gap_status_constraint() -> None:
    constraints = [
        constraint
        for constraint in CapabilityGap.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    ]

    expected_statuses = (
        "detected",
        "investigating",
        "tool_candidate_created",
        "resolved",
        "unresolved",
        "dismissed",
    )

    assert any(
        constraint.name == "chk_capability_gaps_status"
        and all(status in str(constraint.sqltext) for status in expected_statuses)
        for constraint in constraints
    )


def test_tool_candidate_columns_defaults_and_jsonb_fields() -> None:
    table = ToolCandidate.__table__

    assert set(table.columns.keys()) == {
        "id",
        "capability_gap_id",
        "name",
        "implementation",
        "schema",
        "status",
        "sandbox_results",
        "static_analysis_results",
        "jev_prescreen",
        "promotion_decision",
        "created_at",
        "reviewed_at",
    }

    assert isinstance(table.c.schema.type, JSONB)
    assert table.c.schema.nullable is False
    assert str(table.c.status.server_default.arg) == "'drafted'"

    for column_name in (
        "sandbox_results",
        "static_analysis_results",
        "jev_prescreen",
        "promotion_decision",
    ):
        assert isinstance(table.c[column_name].type, JSONB)
        assert table.c[column_name].nullable is True


def test_tool_candidate_foreign_key_index_and_status_constraint() -> None:
    table = ToolCandidate.__table__

    assert table.c.capability_gap_id.nullable is False
    assert any(
        fk.parent.name == "capability_gap_id"
        and fk.target_fullname == "capability_gaps.id"
        for fk in table.foreign_keys
    )

    assert {index.name for index in table.indexes} == {"idx_candidates_gap"}

    constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    ]

    expected_statuses = (
        "drafted",
        "sandboxed",
        "screened",
        "pending-approval",
        "promoted",
        "rejected",
    )

    assert any(
        constraint.name == "chk_tool_candidates_status"
        and all(status in str(constraint.sqltext) for status in expected_statuses)
        for constraint in constraints
    )
