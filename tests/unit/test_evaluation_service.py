import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.errors import APIError
from app.models.base import Base
from app.services.auth_service import register_user
from app.services.evaluation_service import update_status
from app.services.idea_service import create_idea


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_accept_requires_comment(db_session):
    user = register_user(db_session, "user@example.com", "password123")
    admin = register_user(db_session, "admin@example.com", "password123")
    admin.is_admin = True
    db_session.commit()

    idea = create_idea(db_session, user, "Idea", "Desc", "Cat")

    with pytest.raises(APIError) as exc:
        update_status(db_session, admin, idea.id, "accepted", "")
    assert exc.value.status_code == 400
    assert exc.value.message == "comment is required for acceptance or rejection"
