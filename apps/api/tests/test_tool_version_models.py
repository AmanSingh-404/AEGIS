from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

from api.models import ToolVersion


def test_tool_version_columns_and_jsonb_defaults() -> None:
    table = ToolVersion.__table__

    assert set(table.columns.keys()) == {
        "id",
        "tool_id",
        "candidate_id",
        "version",
        "implementation",
        "schema",
        "test_results",
        "static_analysis_results",
        "promotion_status",
        "revoked_at",
        "created_at",
    }

    assert isinstance(table.c.schema.type, JSONB)
    assert isinstance(table.c.test_results.type, JSONB)
    assert isinstance(table.c.static_analysis_results.type, JSONB)
    assert table.c.test_results.server_default is not None
    assert table.c.static_analysis_results.server_default is not None
    assert isinstance(table.c.created_at.type, TIMESTAMP)


def test_tool_version_foreign_keys_and_unique_constraints() -> None:
    table = ToolVersion.__table__

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname)
        for foreign_key in table.foreign_keys
    }
    assert ("tool_id", "tools.id") in foreign_keys
    assert ("candidate_id", "tool_candidates.id") in foreign_keys

    unique_constraints = {
        constraint.name: constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert "uq_tool_versions_tool_version" in unique_constraints
    assert unique_constraints["uq_tool_versions_tool_version"].columns.keys() == [
        "tool_id",
        "version",
    ]
    assert table.c.candidate_id.unique is True


def test_tool_version_promotion_and_revocation_constraints() -> None:
    constraints = {
        constraint.name: constraint
        for constraint in ToolVersion.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "chk_tool_versions_promotion_status" in constraints
    assert "chk_tool_versions_revocation_timestamp" in constraints

    promotion_sql = str(constraints["chk_tool_versions_promotion_status"].sqltext)
    assert "'pending'" in promotion_sql
    assert "'approved'" in promotion_sql
    assert "'promoted'" in promotion_sql
    assert "'rejected'" in promotion_sql
    assert "'revoked'" in promotion_sql

    revocation_sql = str(
        constraints["chk_tool_versions_revocation_timestamp"].sqltext
    )
    assert "revoked_at IS NOT NULL" in revocation_sql
    assert "revoked_at IS NULL" in revocation_sql


def test_tools_current_version_composite_foreign_key():
    from sqlalchemy import ForeignKeyConstraint
    from api.models import Base

    tools = Base.metadata.tables["tools"]
    constraints = [
        constraint
        for constraint in tools.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        and constraint.name == "fk_tools_current_version"
    ]

    assert len(constraints) == 1
    constraint = constraints[0]
    assert [column.name for column in constraint.columns] == ["id", "version"]
    assert [
        element.target_fullname for element in constraint.elements
    ] == ["tool_versions.tool_id", "tool_versions.version"]
    assert constraint.deferrable is True
    assert constraint.initially == "DEFERRED"
