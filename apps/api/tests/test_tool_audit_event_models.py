from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB

from api.models import ToolAuditEvent


def test_tool_audit_event_columns_and_defaults() -> None:
    table = ToolAuditEvent.__table__

    assert set(table.columns.keys()) == {
        "id",
        "candidate_id",
        "tool_version_id",
        "event_type",
        "actor_id",
        "details",
        "created_at",
    }
    assert isinstance(table.c.details.type, JSONB)
    assert table.c.details.nullable is False
    assert table.c.details.server_default is not None
    assert table.c.event_type.nullable is False
    assert table.c.created_at.server_default is not None


def test_tool_audit_event_foreign_keys() -> None:
    table = ToolAuditEvent.__table__
    foreign_keys = {
        (fk.parent.name, fk.target_fullname)
        for fk in table.foreign_keys
    }

    assert ("candidate_id", "tool_candidates.id") in foreign_keys
    assert ("tool_version_id", "tool_versions.id") in foreign_keys
    assert ("actor_id", "users.id") in foreign_keys


def test_tool_audit_event_constraints() -> None:
    checks = {
        constraint.name: constraint
        for constraint in ToolAuditEvent.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "tool_audit_events_event_type_check" in checks
    assert "chk_tool_audit_event_has_reference" in checks

    event_sql = str(checks["tool_audit_events_event_type_check"].sqltext)
    for event_type in (
        "candidate_created",
        "static_analysis_completed",
        "sandbox_validation_completed",
        "jev_prescreen_completed",
        "review_approved",
        "promotion_approved",
        "promotion_rejected",
        "version_promoted",
        "version_revoked",
    ):
        assert f"'{event_type}'" in event_sql

    reference_sql = str(checks["chk_tool_audit_event_has_reference"].sqltext)
    assert "candidate_id IS NOT NULL" in reference_sql
    assert "tool_version_id IS NOT NULL" in reference_sql
