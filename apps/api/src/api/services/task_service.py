from uuid import uuid4

from sqlalchemy.orm import Session

from api.models import Task, User
from api.services.project_access_service import can_create_tasks


class ProjectTaskAccessDenied(Exception):
    """Raised when a user cannot create tasks in a project."""


def create_task(
    db: Session,
    user: User,
    project_id,
    objective: str,
    input_data: dict,
) -> Task:
    """Create a pending task for an authorized project member."""
    if not can_create_tasks(db, user, project_id):
        raise ProjectTaskAccessDenied("Project access denied")

    task = Task(
        id=uuid4(),
        project_id=project_id,
        created_by=user.id,
        objective=objective,
        status="pending",
        input_data=input_data,
    )

    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except Exception:
        db.rollback()
        raise
