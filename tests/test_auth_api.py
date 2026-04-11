from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.test", override=True)

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Max",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
        "name": "Max",
    }


def test_register_user_duplicate_email():
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Max",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Other",
            "password": "secret123",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


def test_login_success():
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Max",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_invalid_password():
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Max",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_read_me():
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Max",
            "password": "secret123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "secret123",
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
        "name": "Max",
        "role": "user",
    }


def test_read_me_without_token():
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}