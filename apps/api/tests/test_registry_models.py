from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from api.models import Agent, Base, Tool


def test_registry_models_register_expected_tables() -> None:
    assert "agents" in Base.metadata.tables
    assert "tools" in Base.metadata.tables


def test_agent_columns_defaults_and_unique_constraint() -> None:
    table = Agent.__table__

    assert set(table.columns.keys()) == {
        "id",
        "name",
        "version",
        "description",
        "configuration",
        "enabled",
        "created_at",
    }

    assert isinstance(table.c.configuration.type, JSONB)
    assert table.c.configuration.server_default is not None
    assert table.c.enabled.server_default is not None

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert any(
        {column.name for column in constraint.columns} == {"name", "version"}
        for constraint in unique_constraints
    )


def test_tool_columns_and_jsonb_fields() -> None:
    table = Tool.__table__

    assert set(table.columns.keys()) == {
        "id",
        "name",
        "description",
        "input_schema",
        "output_schema",
        "permissions",
        "risk_level",
        "timeout_seconds",
        "audit_metadata",
        "origin",
        "version",
        "enabled",
        "created_at",
    }

    for column_name in (
        "input_schema",
        "output_schema",
        "permissions",
        "audit_metadata",
    ):
        assert isinstance(table.c[column_name].type, JSONB)

    assert table.c.permissions.server_default is not None
    assert table.c.audit_metadata.server_default is not None


def test_tool_constraints() -> None:
    table = Tool.__table__

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert any(
        constraint.name == "uq_tools_name_version"
        and {column.name for column in constraint.columns} == {"name", "version"}
        for constraint in unique_constraints
    )

    check_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    ]
    check_sql = {str(constraint.sqltext) for constraint in check_constraints}

    assert any("timeout_seconds > 0" in expression for expression in check_sql)
    assert any(
        "registered" in expression and "forged" in expression
        for expression in check_sql
    )
