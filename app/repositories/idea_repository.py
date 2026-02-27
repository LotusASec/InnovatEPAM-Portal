from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.idea import Idea


class IdeaRepository:
    def create(self, db: Session, submitter_id: int, title: str, description: str, category: str) -> Idea:
        idea = Idea(
            submitter_id=submitter_id,
            title=title,
            description=description,
            category=category,
        )
        db.add(idea)
        db.commit()
        db.refresh(idea)
        return idea

    def list_by_user(self, db: Session, user_id: int) -> list[Idea]:
        return list(db.execute(select(Idea).where(Idea.submitter_id == user_id)).scalars().all())

    def list_all(self, db: Session) -> list[Idea]:
        return list(db.execute(select(Idea)).scalars().all())

    def get_by_id(self, db: Session, idea_id: int) -> Idea | None:
        return db.get(Idea, idea_id)
