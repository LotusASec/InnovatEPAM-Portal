import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.base import Base
import app.models  # noqa: F401


def test_register_success(client):
    client, _ = client  # ← Tuple unpacking ekle
    resp = client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "user@example.com"

def test_register_duplicate_email(client):
    client, _ = client  # ← Tuple unpacking ekle
    client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    resp = client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    assert resp.status_code == 409
    assert resp.json() == {"error": "email already registered"}

def test_login_success(client):
    client, _ = client  # ← Tuple unpacking ekle
    client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]

def test_login_invalid_password(client):
    client, _ = client  # ← Tuple unpacking ekle
    client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrongpass"})
    assert resp.status_code == 401
    assert resp.json() == {"error": "invalid credentials"}

def test_login_user_not_found(client):
    client, _ = client  # ← Tuple unpacking ekle
    resp = client.post("/api/auth/login", json={"email": "missing@example.com", "password": "password123"})
    assert resp.status_code == 404
    assert resp.json() == {"error": "user not found"}