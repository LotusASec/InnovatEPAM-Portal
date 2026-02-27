import re

from sqlalchemy.orm import Session

from app.core.errors import APIError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository

_email_regex = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


_repo = UserRepository()


def register_user(db: Session, email: str, password: str):
    if not _email_regex.match(email):
        raise APIError("invalid email format", status_code=400)
    if len(password) < 8:
        raise APIError("password must be at least 8 characters", status_code=400)

    existing = _repo.get_by_email(db, email)
    if existing:
        raise APIError("email already registered", status_code=409)

    password_hash = hash_password(password)
    return _repo.create_user(db, email=email, password_hash=password_hash)


def login_user(db: Session, email: str, password: str) -> str:
    user = _repo.get_by_email(db, email)
    if not user:
        raise APIError("user not found", status_code=404)
    if not verify_password(password, user.password_hash):
        raise APIError("invalid credentials", status_code=401)
    return create_access_token(str(user.id))
