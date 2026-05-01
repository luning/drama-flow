"""
Auth 集成测试（行为级，不测实现）
"""


def test_register_success(client, db_session):
    response = client.post("/api/auth/register", json={
        "nickname": "TestUser", "email": "test@test.com", "password": "Pass1234"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@test.com"
    assert "password" not in data


def test_register_duplicate_email(client, seed_user):
    response = client.post("/api/auth/register", json={
        "nickname": "Another", "email": "test@test.com", "password": "Pass1234"
    })
    assert response.status_code == 409


def test_login_success(client, seed_user):
    response = client.post("/api/auth/login", json={
        "email": "test@test.com", "password": "Pass1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client, seed_user):
    response = client.post("/api/auth/login", json={
        "email": "test@test.com", "password": "wrongpass"
    })
    assert response.status_code == 401
