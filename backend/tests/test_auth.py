"""
Auth 认证模块集成测试：AC-USER-01 ~ AC-USER-09
"""
from app.services.auth_service import decode_token


class TestAuth:
    """AC-USER-01 ~ AC-USER-09"""

    def test_register_success(self, client, db_session):
        """AC-USER-01: 用户可以使用邮箱+密码成功注册新账号"""
        response = client.post("/api/auth/register", json={
            "nickname": "NewUser", "email": "new@test.com", "password": "Pass1234"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@test.com"
        assert data["nickname"] == "NewUser"
        assert "id" in data
        assert "password" not in data  # 不返回密码

    def test_register_duplicate_email(self, client, seed_user):
        """AC-USER-02: 注册时重复邮箱返回 409 错误"""
        response = client.post("/api/auth/register", json={
            "nickname": "Another", "email": "test@test.com", "password": "Pass1234"
        })
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data

    def test_register_weak_password(self, client):
        """密码强度不足返回 422"""
        response = client.post("/api/auth/register", json={
            "nickname": "Weak", "email": "weak@test.com", "password": "123456"
        })
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """邮箱格式无效返回 422"""
        response = client.post("/api/auth/register", json={
            "nickname": "Bad", "email": "not-an-email", "password": "Pass1234"
        })
        assert response.status_code == 422

    def test_login_after_register(self, client, db_session):
        """AC-USER-03: 注册成功后用户可以立即登录"""
        client.post("/api/auth/register", json={
            "nickname": "NewUser", "email": "new@test.com", "password": "Pass1234"
        })
        response = client.post("/api/auth/login", json={
            "email": "new@test.com", "password": "Pass1234"
        })
        assert response.status_code == 200

    def test_login_success(self, client, seed_user):
        """AC-USER-04: 用户可以使用正确的邮箱+密码登录"""
        response = client.post("/api/auth/login", json={
            "email": "test@test.com", "password": "Pass1234"
        })
        assert response.status_code == 200

    def test_login_returns_valid_jwt(self, client, seed_user):
        """AC-USER-05: 登录成功后返回有效的 JWT Token（包含用户 ID 和过期时间）"""
        response = client.post("/api/auth/login", json={
            "email": "test@test.com", "password": "Pass1234"
        })
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

        # Token 可解码且包含用户 ID 和类型
        payload = decode_token(data["access_token"])
        assert int(payload["sub"]) == seed_user.id
        assert payload["type"] == "access"

        refresh_payload = decode_token(data["refresh_token"])
        assert int(refresh_payload["sub"]) == seed_user.id
        assert refresh_payload["type"] == "refresh"

    def test_login_wrong_password_returns_401(self, client, seed_user):
        """AC-USER-06: 登录错误密码返回 401 且不泄露用户是否存在"""
        response = client.post("/api/auth/login", json={
            "email": "test@test.com", "password": "wrongpass"
        })
        assert response.status_code == 401
        assert "邮箱或密码错误" in response.text

    def test_login_nonexistent_email_returns_401(self, client):
        """登录不存在的邮箱返回 401"""
        response = client.post("/api/auth/login", json={
            "email": "nobody@test.com", "password": "Pass1234"
        })
        assert response.status_code == 401

    def test_logout(self, client, seed_user, auth_header):
        """AC-USER-07: 用户可以成功登出，登出后 Token 不可再用"""
        response = client.post("/api/auth/logout", headers=auth_header)
        assert response.status_code == 200

    def test_logout_without_token_returns_401(self, client):
        """未携带 Token 登出返回 401"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

    def test_error_response_format(self, client):
        """AC-USER-08: 认证接口返回符合 OpenAPI 规范的错误格式"""
        response = client.post("/api/auth/register", json={
            "nickname": "Bad", "email": "bad", "password": "123"
        })
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_token_contains_user_id(self, client, seed_user, user_token):
        """AC-USER-09: Token 中包含用户 ID 和角色信息，可解码验证"""
        payload = decode_token(user_token)
        assert int(payload["sub"]) == seed_user.id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_refresh_token_success(self, client, seed_user):
        """Refresh 接口使用 refresh token 换取新 token"""
        # 先登录获取 refresh token
        login_resp = client.post("/api/auth/login", json={
            "email": "test@test.com", "password": "Pass1234"
        })
        refresh_token_str = login_resp.json()["refresh_token"]

        # 使用 refresh token 获取新 token
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token_str
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@test.com"

    def test_refresh_with_access_token_fails(self, client, seed_user, user_token):
        """使用 access token 来 refresh 应失败"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": user_token
        })
        assert response.status_code == 401

    def test_refresh_invalid_token(self, client):
        """无效的 refresh token 返回 401"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_token_here"
        })
        assert response.status_code == 401
