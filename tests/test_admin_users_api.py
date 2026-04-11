def test_normal_user_cannot_read_users(client, get_token):
    token = get_token("user@example.com", "Normal User", "secret123")

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_normal_user_cannot_read_user_by_id(client, get_token):
    token = get_token("user@example.com", "Normal User", "secret123")

    response = client.get(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_admin_can_read_users(client, get_token, make_admin):
    admin_email = "admin@example.com"
    admin_token = get_token(admin_email, "Admin", "secret123")
    make_admin(admin_email)

    get_token("user@example.com", "Normal User", "secret123")

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "email": "admin@example.com",
            "name": "Admin",
            "role": "admin",
        },
        {
            "id": 2,
            "email": "user@example.com",
            "name": "Normal User",
            "role": "user",
        },
    ]


def test_admin_can_read_user_by_id(client, get_token, make_admin):
    admin_email = "admin@example.com"
    admin_token = get_token(admin_email, "Admin", "secret123")
    make_admin(admin_email)

    get_token("user@example.com", "Normal User", "secret123")

    response = client.get(
        "/users/2",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "email": "user@example.com",
        "name": "Normal User",
        "role": "user",
    }


def test_admin_can_patch_user_by_id(client, get_token, make_admin):
    admin_email = "admin@example.com"
    admin_token = get_token(admin_email, "Admin", "secret123")
    make_admin(admin_email)

    get_token("user@example.com", "Normal User", "secret123")

    response = client.patch(
        "/users/2",
        json={"name": "Updated User"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "email": "user@example.com",
        "name": "Updated User",
        "role": "user",
    }


def test_normal_user_cannot_patch_user_by_id(client, get_token):
    token = get_token("user@example.com", "Normal User", "secret123")

    response = client.patch(
        "/users/1",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_admin_can_delete_user_by_id(client, get_token, make_admin):
    admin_email = "admin@example.com"
    admin_token = get_token(admin_email, "Admin", "secret123")
    make_admin(admin_email)

    get_token("user@example.com", "Normal User", "secret123")

    response = client.delete(
        "/users/2",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "email": "user@example.com",
        "name": "Normal User",
        "role": "user",
    }


def test_normal_user_can_read_own_profile(client, get_token):
    token = get_token("user@example.com", "Normal User", "secret123")

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "user@example.com",
        "name": "Normal User",
        "role": "user",
    }