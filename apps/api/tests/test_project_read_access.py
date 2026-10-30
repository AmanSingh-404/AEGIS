from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from api.services.project_access_service import can_read_project


@pytest.fixture
def read_context():
    return (
        MagicMock(),
        SimpleNamespace(id=uuid4()),
        uuid4(),
    )


def test_project_owner_can_read_without_membership(read_context):
    db, user, project_id = read_context
    db.scalar.return_value = user.id

    assert can_read_project(db, user, project_id) is True
    assert db.scalar.call_count == 1


@pytest.mark.parametrize(
    "role",
    ["owner", "admin", "developer", "reviewer", "viewer"],
)
def test_all_project_member_roles_can_read(read_context, role):
    db, user, project_id = read_context
    db.scalar.side_effect = [uuid4(), role]

    assert can_read_project(db, user, project_id) is True
    assert db.scalar.call_count == 2


def test_non_member_cannot_read_project(read_context):
    db, user, project_id = read_context
    db.scalar.side_effect = [uuid4(), None]

    assert can_read_project(db, user, project_id) is False


def test_nonexistent_project_cannot_be_read(read_context):
    db, user, project_id = read_context
    db.scalar.return_value = None

    assert can_read_project(db, user, project_id) is False
    assert db.scalar.call_count == 1
