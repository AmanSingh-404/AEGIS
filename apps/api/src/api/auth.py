"""Google OpenID Connect ID-token verification and user authentication."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from api.config import Settings, get_settings
from api.database import get_db
from api.models import User
from api.services.identity_service import get_user_by_google_subject


@dataclass(frozen=True)
class AuthenticatedIdentity:
    """Identity established by a verified Google ID token."""

    subject: str
    email: str
    email_verified: bool


def verify_google_id_token(
    token: str,
    settings: Settings | None = None,
) -> AuthenticatedIdentity:
    """Verify a Google ID token and return its trusted identity claims."""

    if settings is None:
        settings = get_settings()

    if not settings.google_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    if not settings.google_oauth_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        )

    if not token or len(token) > 16_384:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=settings.google_oauth_client_id,
        )
    except (ValueError, GoogleAuthError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    subject = claims.get("sub")
    email = claims.get("email")
    email_verified = claims.get("email_verified") is True
    issuer = claims.get("iss")

    if (
        not isinstance(subject, str)
        or not subject.strip()
        or len(subject) > 255
        or not isinstance(email, str)
        or not email.strip()
        or len(email) > 320
        or not email_verified
        or issuer not in {"accounts.google.com", "https://accounts.google.com"}
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedIdentity(
        subject=subject,
        email=email,
        email_verified=email_verified,
    )


_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """Authenticate a Google bearer token and resolve its linked AEGIS user."""

    if not settings.google_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    identity = verify_google_id_token(credentials.credentials, settings)
    user = get_user_by_google_subject(db, identity.subject)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No AEGIS account is linked to this identity",
        )

    return user
