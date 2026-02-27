from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EvaluationStatus(str, Enum):
    accepted = "accepted"
    rejected = "rejected"


class EvaluationComment(Base):
    __tablename__ = "evaluation_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    idea_id: Mapped[int] = mapped_column(ForeignKey("ideas.id"))
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment_text: Mapped[str] = mapped_column(Text)
    status_change_to: Mapped[EvaluationStatus] = mapped_column(SqlEnum(EvaluationStatus))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    idea = relationship("Idea", back_populates="evaluations")
    admin = relationship("User", back_populates="evaluations")
