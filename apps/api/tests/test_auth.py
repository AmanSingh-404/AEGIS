"""Security tests for Google ID-token verification."""

import pytest
from fastapi import HTTPException

from api import auth
from api.auth import AuthenticatedIdentity, verify_google_id_token
from api.config import Settings


CLIENT_ID = "test-client.apps.googleusercontent.com"


def enabled_settings() -> Settings:
    return Settings(
        _env_file=None,
        google_auth_enabled=True,
        google_oauth_client_id=CLIENT_ID,
    )


def valid_claims() -> dict[str, object]:
    return {
        "sub": "google-user-123",
        "email": "user@example.com",
        "email_verified": True,
        "iss": "https://accounts.google.com",
    }


def test_authentication_disabled_returns_not_found(monkeypatch) -> None:
    monkeypatch.setattr(
        auth,
        "get_settings",
        lambda: Settings(_env_file=None, google_auth_enabled=False),
    )

    with pytest.raises(HTTPException) as exc:
        verify_google_id_token("test-token")

    assert exc.value.status_code == 404


def test_missing_client_id_returns_service_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        auth,
        "get_settings",
        lambda: Settings(_env_file=None, google_auth_enabled=True),
    )

    with pytest.raises(HTTPException) as exc:
        verify_google_id_token("test-token")

    assert exc.value.status_code == 503


@pytest.mark.parametrize("token", ["", "x" * 16_385])
def test_empty_or_oversized_token_is_rejected(token, monkeypatch) -> None:
    monkeypatch.setattr(auth, "get_settings", enabled_settings)

    with pytest.raises(HTTPException) as exc:
        verify_google_id_token(token)

    assert exc.value.status_code == 401


def test_valid_google_token_returns_verified_identity(monkeypatch) -> None:
    monkeypatch.setattr(auth, "get_settings", enabled_settings)

    def fake_verify(token, request, audience):
        assert token == "valid-token"
        assert audience == CLIENT_ID
        return valid_claims()

    monkeypatch.setattr(auth.id_token, "verify_oauth2_token", fake_verify)

    identity = verify_google_id_token("valid-token")

    assert identity == AuthenticatedIdentity(
        subject="google-user-123",
        email="user@example.com",
        email_verified=True,
    )


def test_wrong_audience_or_invalid_token_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(auth, "get_settings", enabled_settings)

    def fake_verify(token, request, audience):
        raise ValueError("invalid audience")

    monkeypatch.setattr(auth.id_token, "verify_oauth2_token", fake_verify)

    with pytest.raises(HTTPException) as exc:
        verify_google_id_token("invalid-token")

    assert exc.value.status_code == 401
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "claim,value",
    [
        ("sub", ""),
        ("sub", "   "),
        ("sub", "s" * 256),
        ("email", ""),
        ("email", "   "),
        ("email", "e" * 321),
        ("email_verified", False),
        ("iss", "https://attacker.example"),
    ],
)
def test_untrusted_identity_claims_are_rejected(
    claim, value, monkeypatch
) -> None:
    monkeypatch.setattr(auth, "get_settings", enabled_settings)
    claims = valid_claims()
    claims[claim] = value

    monkeypatch.setattr(
        auth.id_token,
        "verify_oauth2_token",
        lambda token, request, audience: claims,
    )

    with pytest.raises(HTTPException) as exc:
        verify_google_id_token("valid-signature-but-invalid-claims")

    assert exc.value.status_code == 401
