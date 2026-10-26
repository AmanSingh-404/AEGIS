from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from api.models import Approval, ApprovalEvent


def test_approval_columns_and_status_default() -> None:
    table = Approval.__table__

    assert set(table.columns.keys()) == {
        "id",
        "run_id",
        "requested_by",
        "reviewed_by",
        "action_type",
        "action_payload",
        "status",
        "decision_reason",
        "created_at",
        "reviewed_at",
    }

    assert isinstance(table.c.action_payload.type, JSONB)
    assert table.c.status.server_default is not None
    assert str(table.c.status.server_default.arg) == "'pending'"


def test_approval_foreign_keys_and_indexes() -> None:
    table = Approval.__table__

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname)
        for foreign_key in table.foreign_keys
    }

    assert foreign_keys == {
        ("run_id", "runs.id"),
        ("requested_by", "users.id"),
        ("reviewed_by", "users.id"),
    }

    assert {
        index.name for index in table.indexes
    } == {
        "idx_approvals_status",
        "idx_approvals_run",
        "idx_approvals_requested_by",
        "idx_approvals_reviewed_by",
    }


def test_approval_status_constraint() -> None:
    constraints = [
        constraint
        for constraint in Approval.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    ]

    assert any(
        constraint.name == "chk_approvals_status"
        and all(
            status in str(constraint.sqltext)
            for status in ("pending", "approved", "rejected", "cancelled")
        )
        for constraint in constraints
    )


def test_approval_event_columns_and_jsonb_default() -> None:
    table = ApprovalEvent.__table__

    assert set(table.columns.keys()) == {
        "id",
        "approval_id",
        "event_type",
        "actor_id",
        "reason",
        "event_data",
        "created_at",
    }

    assert isinstance(table.c.event_data.type, JSONB)
    assert table.c.event_data.server_default is not None


def test_approval_event_foreign_keys_indexes_and_constraint() -> None:
    table = ApprovalEvent.__table__

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname)
        for foreign_key in table.foreign_keys
    }

    assert foreign_keys == {
        ("approval_id", "approvals.id"),
        ("actor_id", "users.id"),
    }

    assert {
        index.name for index in table.indexes
    } == {
        "idx_approval_events_approval",
        "idx_approval_events_created_at",
    }

    constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    ]

    assert any(
        constraint.name == "approval_events_event_type_check"
        and all(
            event_type in str(constraint.sqltext)
            for event_type in (
                "requested",
                "approved",
                "rejected",
                "cancelled",
                "reassigned",
            )
        )
        for constraint in constraints
    )
