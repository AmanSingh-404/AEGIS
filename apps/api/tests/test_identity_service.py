from unittest.mock import MagicMock

from api.models import User
from api.services.identity_service import get_user_by_google_subject


def test_get_user_by_google_subject_returns_matching_user():
    db = MagicMock()
    expected_user = MagicMock(spec=User)
    db.scalar.return_value = expected_user

    result = get_user_by_google_subject(db, "google-subject-123")

    assert result is expected_user
    db.scalar.assert_called_once()


def test_get_user_by_google_subject_returns_none_when_not_found():
    db = MagicMock()
    db.scalar.return_value = None

    result = get_user_by_google_subject(db, "unknown-google-subject")

    assert result is None
    db.scalar.assert_called_once()


def test_get_user_by_google_subject_skips_empty_subject():
    db = MagicMock()

    result = get_user_by_google_subject(db, "")

    assert result is None
    db.scalar.assert_not_called()
