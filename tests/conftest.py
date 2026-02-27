import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.models.base import Base
import app.models  # noqa: F401
import app.main as main

@pytest.fixture()
def client():
    fastapi_app = main.app

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db

    with TestClient(fastapi_app) as c:
        yield c, TestingSessionLocal  # ← BURASI DEĞİŞTİ: tuple döndür

    fastapi_app.dependency_overrides.clear()