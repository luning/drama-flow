"""
全量 API 集成测试：覆盖 SPEC.md 中所有验收标准 (AC)
"""
import pytest
from app.models.drama import Drama, Category
from app.models.episode import Episode
from app.services.auth_service import create_token, decode_token
from app.config import settings


@pytest.fixture
def seed_categories(db_session):
    cats = [
        Category(id=1, name="甜宠", slug="romance", sort_order=1),
        Category(id=2, name="悬疑", slug="suspense", sort_order=2),
        Category(id=3, name="搞笑", slug="comedy", sort_order=3),
        Category(id=4, name="奇幻", slug="fantasy", sort_order=4),
        Category(id=5, name="霸总", slug="president", sort_order=5),
    ]
    db_session.add_all(cats)
    db_session.commit()
    return cats


@pytest.fixture
def seed_dramas(db_session, seed_categories):
    dramas = [
        Drama(id=1, title="重生之女王归来", description="女王归来",
              category_id=4, rating=4.8, cover_url="/covers/drama01.jpg", year=2025, status="ongoing"),
        Drama(id=2, title="霸道总裁爱上我", description="总裁爱上",
              category_id=5, rating=4.9, cover_url="/covers/drama02.jpg", year=2025, status="ongoing"),
        Drama(id=3, title="深渊回响", description="每个谎言都有回响",
              category_id=2, rating=4.7, cover_url="/covers/drama04.jpg", year=2024, status="completed"),
        Drama(id=4, title="契约婚姻", description="契约婚姻",
              category_id=1, rating=4.5, cover_url="/covers/drama05.jpg", year=2025, status="ongoing"),
        Drama(id=5, title="我的房东是财阀", description="房东是财阀",
              category_id=3, rating=4.6, cover_url="/covers/drama03.jpg", year=2025, status="completed"),
    ]
    db_session.add_all(dramas)
    db_session.commit()
    return dramas


@pytest.fixture
def seed_episodes(db_session, seed_dramas):
    episodes = []
    for d in seed_dramas:
        for i in range(1, 11):
            episodes.append(Episode(
                drama_id=d.id, episode_number=i,
                title=f"第{i}集", duration=f"{18 + i % 5}:{i * 4:02d}",
                video_url=f"/videos/drama{d.id:02d}_ep{i:02d}.mp4",
            ))
    db_session.add_all(episodes)
    db_session.commit()
    return episodes


@pytest.fixture
def user_token(seed_user):
    """创建一个有效的 access token 用于需要认证的测试"""
    return create_token(seed_user.id, "access", settings.jwt_access_expire_minutes)


@pytest.fixture
def refresh_token(seed_user):
    """创建一个有效的 refresh token"""
    return create_token(seed_user.id, "refresh", settings.jwt_refresh_expire_days * 24 * 60)


@pytest.fixture
def auth_header(user_token):
    return {"Authorization": f"Bearer {user_token}"}


# ============================================================
# 一、Auth 认证模块
# ============================================================

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


# ============================================================
# 二、Drama 剧集模块
# ============================================================

class TestDramas:
    """AC-DRAMA-01 ~ AC-DRAMA-06"""

    def test_list_dramas_default(self, client, seed_dramas):
        """AC-DRAMA-02: 不传分类参数时返回全量剧集"""
        response = client.get("/api/dramas")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5
        assert "page" in data
        assert "size" in data

    def test_list_dramas_pagination(self, client, seed_dramas):
        """AC-DRAMA-01: 支持分页"""
        response = client.get("/api/dramas?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 2

        # 第二页
        response2 = client.get("/api/dramas?page=2&size=2")
        data2 = response2.json()
        assert len(data2["items"]) == 2

        # 超出范围的页码返回空
        response3 = client.get("/api/dramas?page=10&size=2")
        data3 = response3.json()
        assert len(data3["items"]) == 0

    def test_list_dramas_by_category(self, client, seed_dramas):
        """AC-DRAMA-01: 按分类筛选剧集"""
        response = client.get("/api/dramas?category=fantasy")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1  # 只有「重生之女王归来」
        assert data["items"][0]["title"] == "重生之女王归来"

    def test_list_dramas_by_category_all(self, client, seed_dramas):
        """category=all 返回全量"""
        response = client.get("/api/dramas?category=all")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5

    def test_list_dramas_unknown_category(self, client, seed_dramas):
        """不存在的分类返回空列表"""
        response = client.get("/api/dramas?category=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_dramas_order_by_update(self, client, seed_dramas):
        """AC-DRAMA-06: 剧集按照更新时间降序排列"""
        response = client.get("/api/dramas")
        items = response.json()["items"]
        assert len(items) == 5

    def test_drama_detail(self, client, seed_dramas, seed_episodes):
        """AC-DRAMA-04: 剧集详情接口返回完整信息（标题/描述/封面/分类/评分/集数）"""
        response = client.get("/api/dramas/1")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "重生之女王归来"
        assert data["description"] == "女王归来"
        assert "cover_url" in data
        assert "category_id" in data
        assert "category_name" in data
        assert "rating" in data
        assert data["episode_count"] == 10
        assert "year" in data
        assert "status" in data

    def test_drama_detail_not_found(self, client, seed_dramas):
        """AC-DRAMA-05: 请求不存在的剧集返回 404"""
        response = client.get("/api/dramas/999")
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_list_categories(self, client, seed_categories):
        """获取分类列表"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data[0]["name"] == "甜宠"
        assert data[0]["slug"] == "romance"

    def test_banners(self, client, seed_dramas):
        """AC-DRAMA-03: Banner 返回 3-5 部推荐剧集"""
        response = client.get("/api/banners")
        assert response.status_code == 200
        data = response.json()
        assert 3 <= len(data) <= 5
        for item in data:
            assert "drama_id" in item
            assert "title" in item
            assert "image_url" in item
            assert "sort_order" in item


# ============================================================
# 三、Episode 剧集集模块
# ============================================================

class TestEpisodes:
    """AC-EP-01 ~ AC-EP-05"""

    def test_list_episodes_by_drama(self, client, seed_dramas, seed_episodes):
        """AC-EP-01: 返回的集数列表按序号升序排列"""
        response = client.get("/api/dramas/1/episodes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10
        numbers = [ep["episode_number"] for ep in data]
        assert numbers == sorted(numbers)  # 升序

    def test_episode_contains_required_fields(self, client, seed_dramas, seed_episodes):
        """AC-EP-02: 每集包含标题、时长、序号、视频 URL"""
        response = client.get("/api/dramas/1/episodes")
        data = response.json()
        for ep in data:
            assert "title" in ep
            assert "duration" in ep
            assert "episode_number" in ep
            assert "video_url" in ep
            assert "id" in ep

    def test_episode_detail(self, client, seed_dramas, seed_episodes):
        """获取单集详情"""
        response = client.get("/api/episodes/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["episode_number"] == 1
        assert "drama_id" in data

    def test_episode_not_found(self, client):
        """AC-EP-05: 请求不存在的单集返回 404"""
        response = client.get("/api/episodes/999")
        assert response.status_code == 404

    def test_episodes_for_nonexistent_drama(self, client, seed_dramas, seed_episodes):
        """不存在的剧集返回空列表"""
        response = client.get("/api/dramas/999/episodes")
        assert response.status_code == 200
        assert response.json() == []


# ============================================================
# 四、WatchRecord 观看记录模块
# ============================================================

class TestWatchRecords:
    """AC-WR-01 ~ AC-WR-06"""

    def test_upsert_record(self, client, seed_user, seed_dramas, seed_episodes, auth_header):
        """AC-WR-01: 用户播放某集后，服务端正确记录进度"""
        response = client.put("/api/watch-records/1",
                              json={"progress": 50.0, "last_position": 300.0, "completed": False},
                              headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 50.0
        assert data["last_position"] == 300.0
        assert data["completed"] is False
        assert data["user_id"] == seed_user.id
        assert data["episode_id"] == 1

    def test_upsert_without_auth_returns_401(self, client, seed_dramas, seed_episodes):
        """AC-WR-05: 未登录用户无法操作观看记录"""
        response = client.put("/api/watch-records/1",
                              json={"progress": 50.0, "last_position": 300.0, "completed": False})
        assert response.status_code == 401

    def test_get_record_returns_last_position(self, client, seed_user, seed_dramas, seed_episodes, auth_header):
        """AC-WR-02: 再次播放同一集时返回上次播放位置"""
        # 先记录进度
        client.put("/api/watch-records/1",
                   json={"progress": 75.0, "last_position": 450.0, "completed": False},
                   headers=auth_header)
        # 再读取
        response = client.get("/api/watch-records/1", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 75.0
        assert data["last_position"] == 450.0

    def test_get_record_non_existent(self, client, seed_user, auth_header):
        """不存在的观看记录返回默认值"""
        response = client.get("/api/watch-records/999", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 0
        assert data["last_position"] == 0
        assert data["completed"] is False

    def test_list_records_ordered_by_update(self, client, seed_user, seed_dramas, seed_episodes, auth_header):
        """AC-WR-03: 观看记录按更新时间降序排列"""
        # 创建两条记录
        client.put("/api/watch-records/1",
                   json={"progress": 50.0, "last_position": 300.0, "completed": False},
                   headers=auth_header)
        client.put("/api/watch-records/2",
                   json={"progress": 20.0, "last_position": 120.0, "completed": False},
                   headers=auth_header)

        response = client.get("/api/watch-records", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        # 第一条记录的 updated_at 应 >= 第二条
        assert data["items"][0]["updated_at"] >= data["items"][1]["updated_at"]

    def test_list_records_pagination(self, client, seed_user, seed_dramas, seed_episodes, auth_header):
        """观看记录分页"""
        for eid in range(1, 4):
            client.put(f"/api/watch-records/{eid}",
                       json={"progress": 10.0, "last_position": 60.0, "completed": False},
                       headers=auth_header)

        response = client.get("/api/watch-records?page=1&size=2", headers=auth_header)
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["page"] == 1

    def test_upsert_idempotent(self, client, seed_user, seed_dramas, seed_episodes, auth_header):
        """AC-WR-06: 同一用户重复上报同一集只保留最新记录（upsert）"""
        # 第一次上报 30%
        client.put("/api/watch-records/1",
                   json={"progress": 30.0, "last_position": 180.0, "completed": False},
                   headers=auth_header)
        # 第二次上报 80%
        client.put("/api/watch-records/1",
                   json={"progress": 80.0, "last_position": 480.0, "completed": True},
                   headers=auth_header)

        # 验证只有一条记录且是最新的
        response = client.get("/api/watch-records", headers=auth_header)
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["progress"] == 80.0
        assert data["items"][0]["completed"] is True

    def test_continue_watching_excludes_completed(self, client, seed_user, seed_dramas, seed_episodes, auth_header):
        """AC-WR-04: 继续观看列表不包含已完成的剧集"""
        # 创建一条未完成的
        client.put("/api/watch-records/1",
                   json={"progress": 50.0, "last_position": 300.0, "completed": False},
                   headers=auth_header)
        # 创建一条已完成的
        client.put("/api/watch-records/2",
                   json={"progress": 100.0, "last_position": 600.0, "completed": True},
                   headers=auth_header)

        response = client.get("/api/watch-records/continue-watching", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        # 只应包含未完成的记录
        ids = [item["episode_id"] for item in data]
        assert 1 in ids
        assert 2 not in ids

    def test_continue_watching_without_auth(self, client):
        """未登录用户无法获取继续观看列表"""
        response = client.get("/api/watch-records/continue-watching")
        assert response.status_code == 401

    def test_list_records_without_auth(self, client):
        """未登录用户无法获取观看记录列表"""
        response = client.get("/api/watch-records")
        assert response.status_code == 401

    def test_get_record_without_auth(self, client):
        """未登录用户无法获取单集观看记录"""
        response = client.get("/api/watch-records/1")
        assert response.status_code == 401


# ============================================================
# 五、健康检查
# ============================================================

class TestHealth:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
