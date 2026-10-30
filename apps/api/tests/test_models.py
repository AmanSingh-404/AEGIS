from sqlalchemy.dialects import postgresql

from api.models import Base, Project, ProjectMember, User


def test_identity_models_register_expected_tables() -> None:
    assert {
        "users",
        "projects",
        "project_members",
    } <= set(Base.metadata.tables)


def test_user_columns_match_schema() -> None:
    table = User.__table__

    assert table.c.id.primary_key
    assert table.c.email.nullable is False
    assert table.c.email.unique is True
    assert table.c.display_name.nullable is True
    assert table.c.identity_provider.nullable is True
    assert table.c.created_at.nullable is False
    assert table.c.created_at.server_default is not None


def test_project_foreign_key_defaults_and_index() -> None:
    table = Project.__table__

    assert table.c.owner_id.nullable is False
    assert any(
        fk.target_fullname == "users.id"
        for fk in table.c.owner_id.foreign_keys
    )
    assert table.c.settings.server_default is not None
    assert "idx_projects_owner" in {index.name for index in table.indexes}


def test_project_member_composite_primary_key_and_role_constraint() -> None:
    table = ProjectMember.__table__

    assert {column.name for column in table.primary_key.columns} == {
        "project_id",
        "user_id",
    }
    assert table.c.role.nullable is False
    assert any(
        constraint.name == "project_members_role_check"
        for constraint in table.constraints
    )
    assert "idx_project_members_user" in {
        index.name for index in table.indexes
    }


def test_project_settings_uses_postgresql_jsonb() -> None:
    column_type = Project.__table__.c.settings.type
    assert isinstance(column_type, postgresql.JSONB)

def test_user_google_subject_is_nullable_and_unique() -> None:
    table = User.__table__

    assert table.c.google_subject.nullable is True
    assert any(
        index.name == "uq_users_google_subject" and index.unique
        for index in table.indexes
    )
