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
    response = client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
        "name": "Max",
    }


def test_create_user_duplicate_email():
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
    response = client.post(
        "/users",
        json={"email": "test@example.com", "name": "Other"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


def test_get_users():
    client.post("/users", json={"email": "a@example.com", "name": "Alice"})
    client.post("/users", json={"email": "b@example.com", "name": "Bob"})

    response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "email": "a@example.com", "name": "Alice"},
        {"id": 2, "email": "b@example.com", "name": "Bob"},
    ]


def test_get_user_by_id():
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
        "name": "Max",
    }


def test_get_user_by_id_not_found():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_task():
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )

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
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )

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
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
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
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )

    response = client.post(
        "/tasks",
        json={"title": "   ", "description": "Desc", "user_id": 1},
    )

    assert response.status_code == 422


def test_put_task():
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
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
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
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
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
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
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
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
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
    client.post(
        "/tasks",
        json={"title": "Task", "description": "Desc", "user_id": 1},
    )

    response = client.patch("/tasks/1", json={})

    assert response.status_code == 422


def test_delete_task():
    client.post(
        "/users",
        json={"email": "test@example.com", "name": "Max"},
    )
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


def test_put_user():
    client.post("/users", json={"email": "test@example.com", "name": "Max"})

    response = client.put(
        "/users/1",
        json={"email": "updated@example.com", "name": "Moritz"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "updated@example.com",
        "name": "Moritz",
    }


def test_put_user_not_found():
    response = client.put(
        "/users/999",
        json={"email": "updated@example.com", "name": "Moritz"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_put_user_duplicate_email():
    client.post("/users", json={"email": "a@example.com", "name": "Alice"})
    client.post("/users", json={"email": "b@example.com", "name": "Bob"})

    response = client.put(
        "/users/2",
        json={"email": "a@example.com", "name": "Bob Updated"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


def test_patch_user_name_only():
    client.post("/users", json={"email": "test@example.com", "name": "Max"})

    response = client.patch("/users/1", json={"name": "Moritz"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
        "name": "Moritz",
    }


def test_patch_user_email_only():
    client.post("/users", json={"email": "test@example.com", "name": "Max"})

    response = client.patch("/users/1", json={"email": "new@example.com"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "new@example.com",
        "name": "Max",
    }


def test_patch_user_empty_body():
    client.post("/users", json={"email": "test@example.com", "name": "Max"})

    response = client.patch("/users/1", json={})

    assert response.status_code == 422


def test_patch_user_duplicate_email():
    client.post("/users", json={"email": "a@example.com", "name": "Alice"})
    client.post("/users", json={"email": "b@example.com", "name": "Bob"})

    response = client.patch("/users/2", json={"email": "a@example.com"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


def test_delete_user():
    client.post("/users", json={"email": "test@example.com", "name": "Max"})

    delete_response = client.delete("/users/1")
    get_response = client.get("/users")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "id": 1,
        "email": "test@example.com",
        "name": "Max",
    }
    assert get_response.json() == []


def test_delete_user_not_found():
    response = client.delete("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_delete_user_with_existing_tasks():
    client.post("/users", json={"email": "test@example.com", "name": "Max"})
    client.post(
        "/tasks",
        json={"title": "Task", "description": "Desc", "user_id": 1},
    )

    response = client.delete("/users/1")

    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot delete user with existing tasks"}