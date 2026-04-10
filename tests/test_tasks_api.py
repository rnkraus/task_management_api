from pathlib import Path
from dotenv import load_dotenv

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import Base, engine


def test_create_task_requires_auth(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Protected task",
            "description": "Should fail",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_task_authenticated(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

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


def test_get_tasks_only_returns_own_tasks(client, get_token):
    token_a = get_token("a@example.com", "Alice", "secret123")
    token_b = get_token("b@example.com", "Bob", "secret123")

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

    response = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "Alice Task",
            "completed": False,
            "description": "A",
            "user_id": 1,
        }
    ]


def test_get_foreign_task_returns_404(client, get_token):
    token_a = get_token("a@example.com", "Alice", "secret123")
    token_b = get_token("b@example.com", "Bob", "secret123")

    task = client.post(
        "/tasks",
        json={"title": "Alice Task", "description": "A"},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()

    response = client.get(
        f"/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_foreign_task_returns_404(client, get_token):
    token_a = get_token("a@example.com", "Alice", "secret123")
    token_b = get_token("b@example.com", "Bob", "secret123")

    task = client.post(
        "/tasks",
        json={"title": "Alice Task", "description": "A"},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()

    response = client.put(
        f"/tasks/{task['id']}",
        json={
            "title": "Hacked",
            "completed": True,
            "description": "Changed",
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_foreign_task_returns_404(client, get_token):
    token_a = get_token("a@example.com", "Alice", "secret123")
    token_b = get_token("b@example.com", "Bob", "secret123")

    task = client.post(
        "/tasks",
        json={"title": "Alice Task", "description": "A"},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()

    response = client.delete(
        f"/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_get_own_task_by_id(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    task = client.post(
        "/tasks",
        json={"title": "Find me", "description": "Some desc"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    response = client.get(
        f"/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Find me",
        "completed": False,
        "description": "Some desc",
        "user_id": 1,
        "user": {
            "id": 1,
            "email": "test@example.com",
            "name": "Max",
        },
    }


def test_get_task_by_id_not_found(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    response = client.get(
        "/tasks/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_task_with_empty_title(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    response = client.post(
        "/tasks",
        json={"title": "   ", "description": "Desc"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_put_own_task(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

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


def test_put_task_with_empty_title(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

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


def test_patch_own_task_title_only(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

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


def test_patch_own_task_description_only(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

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


def test_patch_task_with_empty_body(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

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


def test_delete_own_task(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

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


def test_delete_task_not_found(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    response = client.delete(
        "/tasks/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}