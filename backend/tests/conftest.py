"""Pytest fixtures: isolated SQLite database and a TestClient.

The environment variables must be set *before* importing the application, because
the database path and secret key are read at import time.
"""
from __future__ import annotations

import os
import sys
import tempfile
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

_TMP_DIR = tempfile.mkdtemp(prefix="truthlens-tests-")
os.environ["TRUTHLENS_DB_PATH"] = str(Path(_TMP_DIR) / "test.db")
os.environ["TRUTHLENS_SECRET_KEY"] = "test-secret-key-not-for-production"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def registered_user(client):
    unique = uuid.uuid4().hex[:10]
    payload = {
        "name": "Test Student",
        "email": f"student-{unique}@example.com",
        "password": "StrongPass123",
        "confirm_password": "StrongPass123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    return {
        "token": data["access_token"],
        "email": payload["email"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user": data["user"],
        "payload": payload,
    }
