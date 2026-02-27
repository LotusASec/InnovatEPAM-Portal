from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import APIError
from app.models.idea import Idea
from app.models.evaluation_comment import EvaluationComment

VALID_STATUSES = {"submitted", "under_review", "accepted", "rejected"}


def update_status(
    db: Session,
    admin_user,
    idea_id: int,
    new_status: str,
    comment: str | None,
) -> Idea:
    """
    Business operation for admin evaluation.
    Unit tests expect this signature:
      update_status(db_session, admin, idea.id, "accepted", "")

    Rules (spec):
    - admin only
    - status must be in VALID_STATUSES
    - comment required when accepting/rejecting (non-empty after strip)
    - persist status change, persist evaluation comment (when provided/required)
    """
    if not getattr(admin_user, "is_admin", False):
        raise APIError(status_code=403, message="permission denied")

    if new_status not in VALID_STATUSES:
        raise APIError(status_code=400, message="invalid status")

    idea = db.get(Idea, idea_id)
    if idea is None:
        raise APIError(status_code=404, message="idea not found")

    normalized_comment = comment.strip() if isinstance(comment, str) else ""

    if new_status in {"accepted", "rejected"} and normalized_comment == "":
        raise APIError(status_code=400, message="comment is required for acceptance or rejection")

    # update idea status
    idea.status = new_status
    db.add(idea)

    # store comment if provided (and for accept/reject it's mandatory anyway)
    if normalized_comment != "":
        ec = EvaluationComment(
            idea_id=idea.id,
            admin_id=admin_user.id,
            comment_text=normalized_comment,
            status_change_to=new_status,
        )
        db.add(ec)

    db.commit()
    db.refresh(idea)
    return idea
