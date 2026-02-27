import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.errors import APIError
from app.models.base import Base
from app.services.auth_service import register_user
from app.services.idea_service import create_idea, get_idea_detail, list_ideas


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


def test_create_idea_success(db_session):
    user = register_user(db_session, "user@example.com", "password123")
    idea = create_idea(db_session, user, "Title", "Description", "Category")
    assert idea.title == "Title"
    assert idea.status.value == "submitted"


def test_list_ideas_for_user(db_session):
    user = register_user(db_session, "user@example.com", "password123")
    other = register_user(db_session, "other@example.com", "password123")
    create_idea(db_session, user, "Idea 1", "Desc 1", "Cat")
    create_idea(db_session, user, "Idea 2", "Desc 2", "Cat")
    create_idea(db_session, other, "Idea 3", "Desc 3", "Cat")

    results = list_ideas(db_session, user)
    assert len(results) == 2


def test_list_ideas_for_admin(db_session):
    user = register_user(db_session, "user@example.com", "password123")
    admin = register_user(db_session, "admin@example.com", "password123")
    admin.is_admin = True
    db_session.commit()

    create_idea(db_session, user, "Idea 1", "Desc 1", "Cat")
    create_idea(db_session, admin, "Idea 2", "Desc 2", "Cat")

    results = list_ideas(db_session, admin)
    assert len(results) == 2


def test_get_idea_permission_denied(db_session):
    user = register_user(db_session, "user@example.com", "password123")
    other = register_user(db_session, "other@example.com", "password123")
    idea = create_idea(db_session, user, "Idea", "Desc", "Cat")

    with pytest.raises(APIError) as exc:
        get_idea_detail(db_session, other, idea.id)
    assert exc.value.status_code == 403
    assert exc.value.message == "permission denied"
