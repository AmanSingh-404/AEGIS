from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import Project, ProjectMember, User


TASK_CREATION_ROLES = frozenset({"owner", "admin", "developer"})
PROJECT_READ_ROLES = frozenset(
    {"owner", "admin", "developer", "reviewer", "viewer"}
)


def can_read_project(
    db: Session,
    user: User,
    project_id: UUID,
) -> bool:
    """Check whether a user can read a project's resources."""
    project_owner_id = db.scalar(
        select(Project.owner_id).where(Project.id == project_id)
    )

    if project_owner_id is None:
        return False

    if project_owner_id == user.id:
        return True

    member_role = db.scalar(
        select(ProjectMember.role).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
    )

    return member_role in PROJECT_READ_ROLES


def can_create_tasks(
    db: Session,
    user: User,
    project_id: UUID,
) -> bool:
    """Check whether a user can create tasks in a project."""
    project_owner_id = db.scalar(
        select(Project.owner_id).where(Project.id == project_id)
    )

    if project_owner_id is None:
        return False

    if project_owner_id == user.id:
        return True

    member_role = db.scalar(
        select(ProjectMember.role).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
    )

    return member_role in TASK_CREATION_ROLES
