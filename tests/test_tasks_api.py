from time import sleep


def assert_user_response(
    body: dict,
    *,
    user_id: int,
    email: str,
    name: str,
    role: str,
):
    assert body["id"] == user_id
    assert body["email"] == email
    assert body["name"] == name
    assert body["role"] == role
    assert "created_at" in body
    assert "updated_at" in body


def assert_task_response(
    body: dict,
    *,
    task_id: int,
    title: str,
    completed: bool,
    description: str | None,
    user_id: int,
):
    assert body["id"] == task_id
    assert body["title"] == title
    assert body["completed"] is completed
    assert body["description"] == description
    assert body["user_id"] == user_id
    assert "created_at" in body
    assert "updated_at" in body


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
    body = response.json()

    assert_task_response(
        body,
        task_id=1,
        title="My task",
        completed=False,
        description="Test description",
        user_id=1,
    )


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
    body = response.json()

    assert len(body) == 1
    assert_task_response(
        body[0],
        task_id=1,
        title="Alice Task",
        completed=False,
        description="A",
        user_id=1,
    )


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
    body = response.json()

    assert_task_response(
        body,
        task_id=1,
        title="Find me",
        completed=False,
        description="Some desc",
        user_id=1,
    )

    assert_user_response(
        body["user"],
        user_id=1,
        email="test@example.com",
        name="Max",
        role="user",
    )


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
    body = response.json()

    assert_task_response(
        body,
        task_id=1,
        title="Updated title",
        completed=True,
        description="Updated desc",
        user_id=1,
    )


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
    body = response.json()

    assert_task_response(
        body,
        task_id=1,
        title="New",
        completed=False,
        description="Old desc",
        user_id=1,
    )


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
    body = response.json()

    assert_task_response(
        body,
        task_id=1,
        title="Task",
        completed=False,
        description="New desc",
        user_id=1,
    )


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


def test_patch_task_updates_updated_at(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/tasks",
        json={"title": "Old title", "description": "Old desc"},
        headers=headers,
    )
    assert create_response.status_code == 200
    created_task = create_response.json()

    sleep(1)

    patch_response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"title": "New title"},
        headers=headers,
    )
    assert patch_response.status_code == 200
    updated_task = patch_response.json()

    assert updated_task["title"] == "New title"
    assert updated_task["created_at"] == created_task["created_at"]
    assert updated_task["updated_at"] != created_task["updated_at"]


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
    body = delete_response.json()

    assert_task_response(
        body,
        task_id=1,
        title="To delete",
        completed=False,
        description="Desc",
        user_id=1,
    )

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


def test_get_tasks_filter_by_completed(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Open task", "description": "A"},
        headers={"Authorization": f"Bearer {token}"},
    )

    client.post(
        "/tasks",
        json={"title": "Done task", "description": "B"},
        headers={"Authorization": f"Bearer {token}"},
    )

    client.patch(
        "/tasks/2",
        json={"completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/tasks?completed=true",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert_task_response(
        body[0],
        task_id=2,
        title="Done task",
        completed=True,
        description="B",
        user_id=1,
    )


def test_get_tasks_with_limit_and_offset(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Task 1", "description": "A"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/tasks",
        json={"title": "Task 2", "description": "B"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/tasks",
        json={"title": "Task 3", "description": "C"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/tasks?limit=2&offset=1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 2
    assert_task_response(
        body[0],
        task_id=2,
        title="Task 2",
        completed=False,
        description="B",
        user_id=1,
    )
    assert_task_response(
        body[1],
        task_id=3,
        title="Task 3",
        completed=False,
        description="C",
        user_id=1,
    )


def test_get_tasks_invalid_pagination_params(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    response = client.get(
        "/tasks?limit=0&offset=-1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_get_tasks_sorted_by_id_desc(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Task 1", "description": "A"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/tasks",
        json={"title": "Task 2", "description": "B"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/tasks",
        json={"title": "Task 3", "description": "C"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/tasks?sort_by=id&order=desc",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 3
    assert_task_response(
        body[0],
        task_id=3,
        title="Task 3",
        completed=False,
        description="C",
        user_id=1,
    )
    assert_task_response(
        body[1],
        task_id=2,
        title="Task 2",
        completed=False,
        description="B",
        user_id=1,
    )
    assert_task_response(
        body[2],
        task_id=1,
        title="Task 1",
        completed=False,
        description="A",
        user_id=1,
    )


def test_get_tasks_sorted_by_title_asc(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Bravo", "description": "B"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/tasks",
        json={"title": "Alpha", "description": "A"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/tasks?sort_by=title&order=asc",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 2
    assert_task_response(
        body[0],
        task_id=2,
        title="Alpha",
        completed=False,
        description="A",
        user_id=1,
    )
    assert_task_response(
        body[1],
        task_id=1,
        title="Bravo",
        completed=False,
        description="B",
        user_id=1,
    )


def test_get_tasks_invalid_sort_by(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    response = client.get(
        "/tasks?sort_by=unknown",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_get_tasks_search_by_title(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Fix login bug", "description": "Backend auth"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Pytest coverage"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/tasks?search=login",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert_task_response(
        body[0],
        task_id=1,
        title="Fix login bug",
        completed=False,
        description="Backend auth",
        user_id=1,
    )


def test_get_tasks_search_by_description(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Task A", "description": "API integration"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/tasks",
        json={"title": "Task B", "description": "Database migration"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/tasks?search=database",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert_task_response(
        body[0],
        task_id=2,
        title="Task B",
        completed=False,
        description="Database migration",
        user_id=1,
    )


def test_get_tasks_search_returns_empty_list(client, get_token):
    token = get_token("test@example.com", "Max", "secret123")

    client.post(
        "/tasks",
        json={"title": "Write docs", "description": "README update"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/tasks?search=frontend",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_tasks_search_only_own_tasks(client, get_token):
    token_a = get_token("a@example.com", "Alice", "secret123")
    token_b = get_token("b@example.com", "Bob", "secret123")

    client.post(
        "/tasks",
        json={"title": "Fix login bug", "description": "Alice task"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    client.post(
        "/tasks",
        json={"title": "Fix login bug", "description": "Bob task"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    response = client.get(
        "/tasks?search=login",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert_task_response(
        body[0],
        task_id=1,
        title="Fix login bug",
        completed=False,
        description="Alice task",
        user_id=1,
    )