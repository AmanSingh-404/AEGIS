from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import User


def get_user_by_google_subject(
    db: Session,
    google_subject: str,
) -> User | None:
    """Return the existing AEGIS user linked to a verified Google subject."""
    if not google_subject:
        return None

    return db.scalar(
        select(User).where(User.google_subject == google_subject)
    )
