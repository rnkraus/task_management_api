def test_improve_task_returns_ai_suggestion(client, monkeypatch):
    def fake_improve_task(title, description):
        return {
            "suggested_title": "Improved title",
            "suggested_description": "Improved description",
        }

    monkeypatch.setattr("app.api.ai.improve_task", fake_improve_task)

    response = client.post(
        "/ai/improve-task",
        json={
            "title": "fix bug",
            "description": "login kaputt",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "suggested_title": "Improved title",
        "suggested_description": "Improved description",
    }


def test_improve_existing_task_returns_ai_suggestion(client, get_token, monkeypatch):
    token = get_token("user@example.com", "User", "secret123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/tasks",
        json={
            "title": "fix login bug",
            "description": "login kaputt",
        },
        headers=headers,
    )
    task_id = create_response.json()["id"]

    def fake_improve_task(title, description):
        assert title == "fix login bug"
        assert description == "login kaputt"
        return {
            "suggested_title": "Fix login authentication bug",
            "suggested_description": "Investigate and resolve the login issue.",
        }

    monkeypatch.setattr("app.api.ai.improve_task", fake_improve_task)

    response = client.post(
        f"/ai/tasks/{task_id}/improve",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "suggested_title": "Fix login authentication bug",
        "suggested_description": "Investigate and resolve the login issue.",
    }


def test_improve_existing_task_returns_404_for_foreign_task(client, get_token):
    token_a = get_token("a@example.com", "Alice", "secret123")
    token_b = get_token("b@example.com", "Bob", "secret123")

    task = client.post(
        "/tasks",
        json={
            "title": "Alice task",
            "description": "private",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()

    response = client.post(
        f"/ai/tasks/{task['id']}/improve",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_group_tasks_returns_grouped_tasks(client, get_token, monkeypatch):
    token = get_token("user@example.com", "User", "secret123")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/tasks",
        json={"title": "Fix login bug", "description": "Auth"},
        headers=headers,
    )
    client.post(
        "/tasks",
        json={"title": "Buy groceries", "description": "Milk and bread"},
        headers=headers,
    )

    def fake_group_tasks(tasks):
        assert tasks == [
            {
                "id": 1,
                "title": "Fix login bug",
                "description": "Auth",
                "completed": False,
                "priority": 3,
                "due_date": None,
            },
            {
                "id": 2,
                "title": "Buy groceries",
                "description": "Milk and bread",
                "completed": False,
                "priority": 3,
                "due_date": None,
            },
        ]
        return {
            "groups": [
                {
                    "group_name": "Work",
                    "tasks": [{"id": 1, "title": "Fix login bug"}],
                },
                {
                    "group_name": "Personal",
                    "tasks": [{"id": 2, "title": "Buy groceries"}],
                },
            ]
        }

    monkeypatch.setattr("app.api.ai.group_tasks", fake_group_tasks)

    response = client.get("/ai/group-tasks", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "groups": [
            {
                "group_name": "Work",
                "tasks": [{"id": 1, "title": "Fix login bug"}],
            },
            {
                "group_name": "Personal",
                "tasks": [{"id": 2, "title": "Buy groceries"}],
            },
        ]
    }


def test_plan_returns_ordered_steps(client, get_token, monkeypatch):
    token = get_token("user@example.com", "User", "secret123")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/tasks",
        json={"title": "Fix login bug", "description": "Auth"},
        headers=headers,
    )
    client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Pytest"},
        headers=headers,
    )

    def fake_create_task_plan(tasks):
        assert tasks == [
            {
                "id": 1,
                "title": "Fix login bug",
                "description": "Auth",
                "completed": False,
                "priority": 3,
                "due_date": None,
            },
            {
                "id": 2,
                "title": "Write tests",
                "description": "Pytest",
                "completed": False,
                "priority": 3,
                "due_date": None,
            },
        ]
        return {
            "steps": [
                {
                    "id": 1,
                    "title": "Fix login bug",
                    "reason": "This blocks core functionality.",
                    "due_date": None,
                },
                {
                    "id": 2,
                    "title": "Write tests",
                    "reason": "Tests should validate the fix.",
                    "due_date": None,
                },
            ]
        }

    monkeypatch.setattr("app.api.ai.create_task_plan", fake_create_task_plan)

    response = client.get("/ai/plan", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "steps": [
            {
                "id": 1,
                "title": "Fix login bug",
                "reason": "This blocks core functionality.",
                "due_date": None,
            },
            {
                "id": 2,
                "title": "Write tests",
                "reason": "Tests should validate the fix.",
                "due_date": None,
            },
        ]
    }
    

def test_group_tasks_requires_auth(client):
    response = client.get("/ai/group-tasks")

    assert response.status_code == 401


def test_plan_with_no_tasks_returns_empty(client, get_token, monkeypatch):
    token = get_token("user@example.com", "User", "secret123")
    headers = {"Authorization": f"Bearer {token}"}

    def fake_plan(tasks):
        assert tasks == []
        return {"steps": []}

    monkeypatch.setattr("app.api.ai.create_task_plan", fake_plan)

    response = client.get("/ai/plan", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"steps": []}


def test_group_tasks_filters_invalid_titles(client, get_token, monkeypatch):
    token = get_token("user@example.com", "User", "secret123")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/tasks", json={"title": "ok task"}, headers=headers)
    client.post("/tasks", json={"title": "a"}, headers=headers)
    client.post("/tasks", json={"title": ""}, headers=headers)

    def fake_group(tasks):
        assert tasks == [
            {
                "id": 1,
                "title": "ok task",
                "description": None,
                "completed": False,
                "priority": 3,
                "due_date": None,
            }
        ]
        return {"groups": []}

    monkeypatch.setattr("app.api.ai.group_tasks", fake_group)

    response = client.get("/ai/group-tasks", headers=headers)

    assert response.status_code == 200