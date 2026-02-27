from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IdeaStatus(str, Enum):
    submitted = "submitted"
    under_review = "under_review"
    accepted = "accepted"
    rejected = "rejected"


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))
    status: Mapped[IdeaStatus] = mapped_column(SqlEnum(IdeaStatus), default=IdeaStatus.submitted)
    submitter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submitter = relationship("User", back_populates="ideas")
    attachment = relationship("Attachment", back_populates="idea", uselist=False)
    evaluations = relationship("EvaluationComment", back_populates="idea")
