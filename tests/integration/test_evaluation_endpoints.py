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


@pytest.fixture
def setup_test_data(client):
    """Setup helper for all evaluation endpoint tests"""
    test_client, SessionLocal = client
    headers_user = _register_and_login(test_client, "user@example.com", "password123")
    _create_admin(SessionLocal)
    headers_admin = _register_and_login(test_client, "admin@example.com", "password123")

    create_response = test_client.post(
        "/api/ideas",
        headers=headers_user,
        data={"title": "Test Idea", "description": "Test Description", "category": "Test"},
    )
    idea_id = create_response.json()["id"]
    
    return test_client, headers_user, headers_admin, idea_id


def test_admin_under_review_without_comment_succeeds(setup_test_data):
    """T003: Admin can set status to under_review without comment (200 OK)"""
    client, _, headers_admin, idea_id = setup_test_data

    response = client.patch(
        f"/api/ideas/{idea_id}/status",
        headers=headers_admin,
        json={"status": "under_review", "comment": None},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "under_review"


def test_admin_accepted_without_comment_fails(setup_test_data):
    """T004: Admin cannot set status to accepted without comment (400 Bad Request)"""
    client, _, headers_admin, idea_id = setup_test_data

    response = client.patch(
        f"/api/ideas/{idea_id}/status",
        headers=headers_admin,
        json={"status": "accepted", "comment": None},
    )
    assert response.status_code == 400
    payload = response.json()
    assert "comment" in payload.get("detail", [{}])[0].get("msg", "").lower() or \
           "comment" in payload.get("error", "").lower()


def test_admin_accepted_with_blank_comment_fails(setup_test_data):
    """T004b: Admin cannot set status to accepted with blank comment (400 Bad Request)"""
    client, _, headers_admin, idea_id = setup_test_data

    response = client.patch(
        f"/api/ideas/{idea_id}/status",
        headers=headers_admin,
        json={"status": "accepted", "comment": "   "},
    )
    assert response.status_code == 400


def test_admin_rejected_without_comment_fails(setup_test_data):
    """T005: Admin cannot set status to rejected without comment (400 Bad Request)"""
    client, _, headers_admin, idea_id = setup_test_data

    response = client.patch(
        f"/api/ideas/{idea_id}/status",
        headers=headers_admin,
        json={"status": "rejected", "comment": None},
    )
    assert response.status_code == 400
    payload = response.json()
    assert "comment" in payload.get("detail", [{}])[0].get("msg", "").lower() or \
           "comment" in payload.get("error", "").lower()


def test_admin_rejected_with_blank_comment_fails(setup_test_data):
    """T005b: Admin cannot set status to rejected with blank comment (400 Bad Request)"""
    client, _, headers_admin, idea_id = setup_test_data

    response = client.patch(
        f"/api/ideas/{idea_id}/status",
        headers=headers_admin,
        json={"status": "rejected", "comment": "   "},
    )
    assert response.status_code == 400


def test_non_admin_cannot_update_status(setup_test_data):
    """T006: Non-admin user cannot update idea status (403 Forbidden)"""
    client, headers_user, _, idea_id = setup_test_data

    response = client.patch(
        f"/api/ideas/{idea_id}/status",
        headers=headers_user,
        json={"status": "under_review", "comment": None},
    )
    assert response.status_code == 403


def test_admin_can_update_status(client):
    """Existing test - preserves regression coverage"""
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
