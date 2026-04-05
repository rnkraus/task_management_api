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


def test_create_user():
    response = client.post("/users", json={"email": "test@example.com"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
    }


def test_create_user_duplicate_email():
    client.post("/users", json={"email": "test@example.com"})
    response = client.post("/users", json={"email": "test@example.com"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


def test_get_users():
    client.post("/users", json={"email": "a@example.com"})
    client.post("/users", json={"email": "b@example.com"})

    response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "email": "a@example.com"},
        {"id": 2, "email": "b@example.com"},
    ]


def test_get_user_by_id():
    client.post("/users", json={"email": "test@example.com"})

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
    }


def test_get_user_by_id_not_found():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_task():
    client.post("/users", json={"email": "test@example.com"})

    response = client.post(
        "/tasks",
        json={
            "title": "1st Task",
            "description": "Test description",
            "user_id": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "1st Task",
        "completed": False,
        "description": "Test description",
        "user_id": 1,
    }


def test_create_task_with_invalid_user_id():
    response = client.post(
        "/tasks",
        json={
            "title": "Task without valid user",
            "description": "Should fail",
            "user_id": 999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_get_all_tasks():
    client.post("/users", json={"email": "test@example.com"})

    client.post(
        "/tasks",
        json={"title": "Task A", "description": "Desc A", "user_id": 1},
    )
    client.post(
        "/tasks",
        json={"title": "Task B", "description": "Desc B", "user_id": 1},
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "Task A",
            "completed": False,
            "description": "Desc A",
            "user_id": 1,
        },
        {
            "id": 2,
            "title": "Task B",
            "completed": False,
            "description": "Desc B",
            "user_id": 1,
        },
    ]


def test_get_task_by_id():
    client.post("/users", json={"email": "test@example.com"})
    client.post(
        "/tasks",
        json={"title": "Find me", "description": "Some desc", "user_id": 1},
    )

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Find me",
        "completed": False,
        "description": "Some desc",
        "user_id": 1,
    }


def test_get_task_by_id_not_found():
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_task_with_empty_title():
    client.post("/users", json={"email": "test@example.com"})

    response = client.post(
        "/tasks",
        json={"title": "   ", "description": "Desc", "user_id": 1},
    )

    assert response.status_code == 422


def test_put_task():
    client.post("/users", json={"email": "test@example.com"})
    client.post(
        "/tasks",
        json={"title": "Old title", "description": "Old desc", "user_id": 1},
    )

    response = client.put(
        "/tasks/1",
        json={
            "title": "Updated title",
            "completed": True,
            "description": "Updated desc",
            "user_id": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Updated title",
        "completed": True,
        "description": "Updated desc",
        "user_id": 1,
    }


def test_put_task_with_empty_title():
    client.post("/users", json={"email": "test@example.com"})
    client.post(
        "/tasks",
        json={"title": "Old title", "description": "Desc", "user_id": 1},
    )

    response = client.put(
        "/tasks/1",
        json={
            "title": "   ",
            "completed": True,
            "description": "Updated desc",
            "user_id": 1,
        },
    )

    assert response.status_code == 422


def test_patch_task_title_only():
    client.post("/users", json={"email": "test@example.com"})
    client.post(
        "/tasks",
        json={"title": "Old", "description": "Old desc", "user_id": 1},
    )

    response = client.patch("/tasks/1", json={"title": "New"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "New",
        "completed": False,
        "description": "Old desc",
        "user_id": 1,
    }


def test_patch_task_description_only():
    client.post("/users", json={"email": "test@example.com"})
    client.post(
        "/tasks",
        json={"title": "Task", "description": "Old desc", "user_id": 1},
    )

    response = client.patch("/tasks/1", json={"description": "New desc"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Task",
        "completed": False,
        "description": "New desc",
        "user_id": 1,
    }


def test_patch_task_with_empty_body():
    client.post("/users", json={"email": "test@example.com"})
    client.post(
        "/tasks",
        json={"title": "Task", "description": "Desc", "user_id": 1},
    )

    response = client.patch("/tasks/1", json={})

    assert response.status_code == 422


def test_delete_task():
    client.post("/users", json={"email": "test@example.com"})
    client.post(
        "/tasks",
        json={"title": "To delete", "description": "Desc", "user_id": 1},
    )

    delete_response = client.delete("/tasks/1")
    get_response = client.get("/tasks")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "id": 1,
        "title": "To delete",
        "completed": False,
        "description": "Desc",
        "user_id": 1,
    }
    assert get_response.json() == []


def test_delete_task_not_found():
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}