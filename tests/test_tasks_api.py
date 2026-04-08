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


def create_user_and_get_token(email: str, name: str, password: str) -> str:
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "name": name,
            "password": password,
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_create_task_requires_auth():
    response = client.post(
        "/tasks",
        json={
            "title": "Protected task",
            "description": "Should fail",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_task_authenticated():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    response = client.post(
        "/tasks",
        json={
            "title": "My task",
            "description": "Test description",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "My task",
        "completed": False,
        "description": "Test description",
        "user_id": 1,
    }


def test_get_tasks_only_returns_own_tasks():
    token_a = create_user_and_get_token("a@example.com", "Alice", "secret123")
    token_b = create_user_and_get_token("b@example.com", "Bob", "secret123")

    client.post(
        "/tasks",
        json={"title": "Alice Task", "description": "A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    client.post(
        "/tasks",
        json={"title": "Bob Task", "description": "B"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    response_a = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert response_a.status_code == 200
    assert response_a.json() == [
        {
            "id": 1,
            "title": "Alice Task",
            "completed": False,
            "description": "A",
            "user_id": 1,
        }
    ]


def test_get_foreign_task_returns_404():
    token_a = create_user_and_get_token("a@example.com", "Alice", "secret123")
    token_b = create_user_and_get_token("b@example.com", "Bob", "secret123")

    create_response = client.post(
        "/tasks",
        json={"title": "Alice Task", "description": "A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_foreign_task_returns_404():
    token_a = create_user_and_get_token("a@example.com", "Alice", "secret123")
    token_b = create_user_and_get_token("b@example.com", "Bob", "secret123")

    create_response = client.post(
        "/tasks",
        json={"title": "Alice Task", "description": "A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Hacked",
            "completed": True,
            "description": "Changed",
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_foreign_task_returns_404():
    token_a = create_user_and_get_token("a@example.com", "Alice", "secret123")
    token_b = create_user_and_get_token("b@example.com", "Bob", "secret123")

    create_response = client.post(
        "/tasks",
        json={"title": "Alice Task", "description": "A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_get_own_task_by_id():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    create_response = client.post(
        "/tasks",
        json={"title": "Find me", "description": "Some desc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Find me",
        "completed": False,
        "description": "Some desc",
        "user_id": 1,
    }


def test_get_task_by_id_not_found():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    response = client.get(
        "/tasks/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_task_with_empty_title():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    response = client.post(
        "/tasks",
        json={"title": "   ", "description": "Desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_put_own_task():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Old title", "description": "Old desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.put(
        "/tasks/1",
        json={
            "title": "Updated title",
            "completed": True,
            "description": "Updated desc",
        },
        headers={"Authorization": f"Bearer {token}"},
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
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Old title", "description": "Desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.put(
        "/tasks/1",
        json={
            "title": "   ",
            "completed": True,
            "description": "Updated desc",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_patch_own_task_title_only():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Old", "description": "Old desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.patch(
        "/tasks/1",
        json={"title": "New"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "New",
        "completed": False,
        "description": "Old desc",
        "user_id": 1,
    }


def test_patch_own_task_description_only():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Task", "description": "Old desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.patch(
        "/tasks/1",
        json={"description": "New desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Task",
        "completed": False,
        "description": "New desc",
        "user_id": 1,
    }


def test_patch_task_with_empty_body():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Task", "description": "Desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.patch(
        "/tasks/1",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_delete_own_task():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "To delete", "description": "Desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    delete_response = client.delete(
        "/tasks/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    get_response = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "id": 1,
        "title": "To delete",
        "completed": False,
        "description": "Desc",
        "user_id": 1,
    }
    assert get_response.status_code == 200
    assert get_response.json() == []


def test_delete_task_not_found():
    token = create_user_and_get_token("test@example.com", "Max", "secret123")

    response = client.delete(
        "/tasks/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}