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


def test_create_task():
    response = client.post("/tasks", json={"title": "1st Task"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "1st Task",
        "completed": False,
    }


def test_get_all_tasks():
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "Task A", "completed": False},
        {"id": 2, "title": "Task B", "completed": False},
    ]


def test_get_task_by_id_not_found():
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_task_with_empty_title():
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_patch_task_title_only():
    client.post("/tasks", json={"title": "Old"})

    response = client.patch("/tasks/1", json={"title": "New"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "New",
        "completed": False,
    }


def test_patch_task_with_empty_body():
    client.post("/tasks", json={"title": "Task"})

    response = client.patch("/tasks/1", json={})

    assert response.status_code == 422


def test_delete_task():
    client.post("/tasks", json={"title": "To delete"})

    delete_response = client.delete("/tasks/1")
    get_response = client.get("/tasks")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "id": 1,
        "title": "To delete",
        "completed": False,
    }
    assert get_response.json() == []


def test_get_task_by_id():
    client.post("/tasks", json={"title": "Find me"})

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Find me",
        "completed": False,
    }


def test_put_task():
    client.post("/tasks", json={"title": "Old title"})

    response = client.put(
        "/tasks/1",
        json={"title": "Updated title", "completed": True},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Updated title",
        "completed": True,
    }


def test_delete_task_not_found():
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_put_task_with_empty_title():
    client.post("/tasks", json={"title": "Old title"})

    response = client.put(
        "/tasks/1",
        json={"title": "   ", "completed": True},
    )

    assert response.status_code == 422