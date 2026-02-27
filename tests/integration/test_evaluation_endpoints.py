import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models.base import Base
from app.repositories.user_repository import UserRepository



def _register_and_login(client, email, password):
    client.post("/api/auth/register", json={"email": email, "password": password})
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_admin(SessionLocal):
    db = SessionLocal()
    try:
        repo = UserRepository()
        admin = repo.create_user(db, "admin@example.com", hash_password("password123"), is_admin=True)
        return admin
    finally:
        db.close()


def test_admin_can_update_status(client):
    client, SessionLocal = client
    headers_user = _register_and_login(client, "user@example.com", "password123")
    _create_admin(SessionLocal)
    headers_admin = _register_and_login(client, "admin@example.com", "password123")

    create_response = client.post(
        "/api/ideas",
        headers=headers_user,
        data={"title": "Idea", "description": "Desc", "category": "Cat"},
    )
    idea_id = create_response.json()["id"]

    response = client.patch(
        f"/api/ideas/{idea_id}/status",
        headers=headers_admin,
        json={"status": "under_review", "comment": None},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "under_review"
