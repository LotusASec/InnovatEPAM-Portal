from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin, get_current_user
from app.core.database import get_db
from app.schemas.ideas import IdeaDetail, IdeaSummary, StatusUpdate
from app.services.idea_service import create_idea, get_idea_detail, list_ideas, update_idea_status

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("", response_model=IdeaDetail, status_code=status.HTTP_201_CREATED)
def create_idea_endpoint(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return create_idea(db, user, title, description, category)


@router.get("", response_model=list[IdeaSummary])
def list_ideas_endpoint(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return list_ideas(db, user)


@router.get("/{idea_id}", response_model=IdeaDetail)
def get_idea_detail_endpoint(
    idea_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_idea_detail(db, user, idea_id)


@router.patch("/{idea_id}/status", response_model=IdeaDetail)
def update_idea_status_endpoint(
    idea_id: int,
    status_update: StatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin),
):
    return update_idea_status(db, user, idea_id, status_update.status)
