import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.errors import APIError
from app.models.base import Base
from app.services.auth_service import login_user, register_user


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


def test_register_success(db_session):
    user = register_user(db_session, "user@example.com", "password123")
    assert user.email == "user@example.com"


def test_register_duplicate_email(db_session):
    register_user(db_session, "user@example.com", "password123")
    with pytest.raises(APIError) as exc:
        register_user(db_session, "user@example.com", "password123")
    assert exc.value.status_code == 409
    assert exc.value.message == "email already registered"


def test_register_invalid_email(db_session):
    with pytest.raises(APIError) as exc:
        register_user(db_session, "notanemail", "password123")
    assert exc.value.status_code == 400
    assert exc.value.message == "invalid email format"


def test_register_weak_password(db_session):
    with pytest.raises(APIError) as exc:
        register_user(db_session, "user@example.com", "short")
    assert exc.value.status_code == 400
    assert exc.value.message == "password must be at least 8 characters"


def test_login_success(db_session):
    register_user(db_session, "user@example.com", "password123")
    token = login_user(db_session, "user@example.com", "password123")
    assert isinstance(token, str)
    assert token


def test_login_invalid_password(db_session):
    register_user(db_session, "user@example.com", "password123")
    with pytest.raises(APIError) as exc:
        login_user(db_session, "user@example.com", "wrongpass")
    assert exc.value.status_code == 401
    assert exc.value.message == "invalid credentials"


def test_login_user_not_found(db_session):
    with pytest.raises(APIError) as exc:
        login_user(db_session, "missing@example.com", "password123")
    assert exc.value.status_code == 404
    assert exc.value.message == "user not found"
