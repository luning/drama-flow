"""
WatchRecord 观看记录模块集成测试：AC-WR-01 ~ AC-WR-06
"""


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
