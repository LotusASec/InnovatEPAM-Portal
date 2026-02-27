from sqlalchemy.orm import Session

from app.core.errors import APIError
from app.models.idea import IdeaStatus
from app.models.user import User
from app.repositories.idea_repository import IdeaRepository

_repo = IdeaRepository()


def _require_value(value: str, field: str) -> str:
    if not value or not value.strip():
        raise APIError(f"{field} is required", status_code=400)
    return value.strip()


def create_idea(db: Session, user: User, title: str, description: str, category: str):
    title = _require_value(title, "title")
    description = _require_value(description, "description")
    category = _require_value(category, "category")
    return _repo.create(db, submitter_id=user.id, title=title, description=description, category=category)


def list_ideas(db: Session, user: User):
    if user.is_admin:
        return _repo.list_all(db)
    return _repo.list_by_user(db, user.id)


def get_idea_detail(db: Session, user: User, idea_id: int):
    idea = _repo.get_by_id(db, idea_id)
    if not idea:
        raise APIError("idea not found", status_code=404)
    if not user.is_admin and idea.submitter_id != user.id:
        raise APIError("permission denied", status_code=403)
    return idea

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

def validate_attachment(filename: str, content_type: str, file_size: int) -> None:
    # Size validation
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError("file size exceeds 5MB limit")

    # Extension validation
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("file type not allowed")


def update_idea_status(db: Session, user: User, idea_id: int, new_status: str):
    """Update idea status (admin only)"""
    # Validate status
    try:
        status_enum = IdeaStatus(new_status)
    except ValueError:
        raise APIError("invalid status value", status_code=400)
    
    # Get idea
    idea = _repo.get_by_id(db, idea_id)
    if not idea:
        raise APIError("idea not found", status_code=404)
    
    # Update status
    idea.status = status_enum
    db.commit()
    db.refresh(idea)
    return idea