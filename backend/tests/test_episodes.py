"""
Episode 剧集集模块集成测试：AC-EP-01 ~ AC-EP-05
"""


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

    def test_video_url_tos_unavailable(self, client, monkeypatch):
        """AC-EP-03: TOS 服务不可用且非本地模式时返回 503"""
        monkeypatch.setattr("app.services.tos_service.tos_service.is_available", lambda: False)
        monkeypatch.setattr("app.api.episodes.settings", type("S", (), {"local_media_base_url": ""})())
        response = client.get("/api/episodes/1/video-url")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data

    def test_video_url_episode_not_found(self, client):
        """AC-EP-03: 单集不存在时返回 404"""
        response = client.get("/api/episodes/999/video-url")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_video_url_success(self, client, seed_dramas, seed_episodes):
        """AC-EP-03: 视频 URL 有效期内可正常播放
        [Changed] local_media_base_url 模式下返回本地绝对 URL（http://...），expires_at 为 null；
        生产 TOS 模式下返回 https:// 签名 URL，expires_at 为 ISO 时间字符串。"""
        response = client.get("/api/episodes/1/video-url")
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "expires_at" in data
        assert data["url"].startswith("http")

    def test_video_url_renew_signature(self, client, seed_dramas, seed_episodes):
        """AC-EP-04: 生产模式下视频 URL 包含 TOS 签名参数，过期后可重新获取
        [Changed] local_media_base_url 模式下跳过 TOS 签名参数断言，仅验证可获取有效 URL。"""
        from app.config import settings
        response = client.get("/api/episodes/1/video-url")
        assert response.status_code == 200
        data = response.json()
        assert data["url"].startswith("http")
        if not settings.local_media_base_url:
            assert data["url"].startswith("https://")
            assert "X-Tos-Signature" in data["url"]
            assert "X-Tos-Algorithm" in data["url"]
            assert "X-Tos-Expires=21600" in data["url"]
