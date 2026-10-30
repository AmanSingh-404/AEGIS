from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from api.services.project_access_service import can_create_tasks


@pytest.fixture
def project_context():
    return SimpleNamespace(
        db=MagicMock(),
        user=SimpleNamespace(id=uuid4()),
        project_id=uuid4(),
    )


def test_project_owner_can_create_tasks(project_context):
    project_context.db.scalar.return_value = project_context.user.id

    assert can_create_tasks(
        project_context.db,
        project_context.user,
        project_context.project_id,
    ) is True

    assert project_context.db.scalar.call_count == 1


@pytest.mark.parametrize("role", ["owner", "admin", "developer"])
def test_allowed_member_roles_can_create_tasks(project_context, role):
    project_context.db.scalar.side_effect = [uuid4(), role]

    assert can_create_tasks(
        project_context.db,
        project_context.user,
        project_context.project_id,
    ) is True

    assert project_context.db.scalar.call_count == 2


@pytest.mark.parametrize("role", ["reviewer", "viewer", "unknown"])
def test_read_only_or_unknown_roles_cannot_create_tasks(
    project_context,
    role,
):
    project_context.db.scalar.side_effect = [uuid4(), role]

    assert can_create_tasks(
        project_context.db,
        project_context.user,
        project_context.project_id,
    ) is False


def test_non_member_cannot_create_tasks(project_context):
    project_context.db.scalar.side_effect = [uuid4(), None]

    assert can_create_tasks(
        project_context.db,
        project_context.user,
        project_context.project_id,
    ) is False


def test_nonexistent_project_denies_access(project_context):
    project_context.db.scalar.return_value = None

    assert can_create_tasks(
        project_context.db,
        project_context.user,
        project_context.project_id,
    ) is False

    assert project_context.db.scalar.call_count == 1
