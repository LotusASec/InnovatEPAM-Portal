from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def create_user(self, db: Session, email: str, password_hash: str, is_admin: bool = False) -> User:
        user = User(email=email, password_hash=password_hash, is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
