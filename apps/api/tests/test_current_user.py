from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

import api.auth as auth
import api.config as config
from api.auth import AuthenticatedIdentity, get_current_user


def test_current_user_hides_endpoint_when_google_auth_disabled(monkeypatch):
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: SimpleNamespace(google_auth_enabled=False),
    )

    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=None, db=MagicMock(), settings=SimpleNamespace(google_auth_enabled=False))

    assert exc.value.status_code == 404


def test_current_user_requires_bearer_token(monkeypatch):
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: SimpleNamespace(google_auth_enabled=True),
    )

    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=None, db=MagicMock(), settings=SimpleNamespace(google_auth_enabled=True))

    assert exc.value.status_code == 401
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"


def test_current_user_rejects_unlinked_google_identity(monkeypatch):
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: SimpleNamespace(google_auth_enabled=True),
    )
    monkeypatch.setattr(
        auth,
        "verify_google_id_token",
        lambda token, settings=None: AuthenticatedIdentity(
            subject="google-subject-123",
            email="person@example.com",
            email_verified=True,
        ),
    )
    monkeypatch.setattr(auth, "get_user_by_google_subject", lambda db, subject: None)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-test-token",
    )

    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=credentials, db=MagicMock(), settings=SimpleNamespace(google_auth_enabled=True))

    assert exc.value.status_code == 403


def test_current_user_returns_linked_user(monkeypatch):
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: SimpleNamespace(google_auth_enabled=True),
    )
    expected_user = MagicMock()
    monkeypatch.setattr(
        auth,
        "verify_google_id_token",
        lambda token, settings=None: AuthenticatedIdentity(
            subject="google-subject-123",
            email="person@example.com",
            email_verified=True,
        ),
    )
    monkeypatch.setattr(
        auth,
        "get_user_by_google_subject",
        lambda db, subject: expected_user,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-test-token",
    )

    result = get_current_user(credentials=credentials, db=MagicMock(), settings=SimpleNamespace(google_auth_enabled=True))

    assert result is expected_user
