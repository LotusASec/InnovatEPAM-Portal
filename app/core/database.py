from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base  # noqa: F401


def _build_engine_url() -> str:
    return settings.database_url


def _build_connect_args(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    _build_engine_url(),
    connect_args=_build_connect_args(settings.database_url),
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
