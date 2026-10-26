from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB

from api.models import DecisionLog


def test_decision_log_columns_and_jsonb_fields() -> None:
    table = DecisionLog.__table__

    assert set(table.columns.keys()) == {
        "id",
        "run_id",
        "state_summary",
        "question_type",
        "question",
        "answer",
        "confidence",
        "escalated",
        "escalation_outcome",
        "agreement",
        "provider",
        "latency_ms",
        "created_at",
    }

    for name in ("state_summary", "question", "answer", "escalation_outcome"):
        assert isinstance(table.c[name].type, JSONB)

    assert table.c.state_summary.nullable is False
    assert table.c.question.nullable is False
    assert table.c.answer.nullable is False
    assert str(table.c.escalated.server_default.arg) == "false"


def test_decision_log_run_foreign_key_and_checks() -> None:
    table = DecisionLog.__table__

    assert any(
        fk.parent.name == "run_id" and fk.target_fullname == "runs.id"
        for fk in table.foreign_keys
    )

    checks = {
        constraint.name: constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "decision_log_question_type_check" in checks
    assert "decision_log_confidence_check" in checks

    question_sql = str(checks["decision_log_question_type_check"].sqltext)
    assert "'choice'" in question_sql
    assert "'score'" in question_sql
    assert "'noul'" in question_sql

    confidence_sql = str(checks["decision_log_confidence_check"].sqltext)
    assert "confidence >= 0" in confidence_sql
    assert "confidence <= 1" in confidence_sql
