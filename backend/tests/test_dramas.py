"""
Drama 剧集模块集成测试：AC-DRAMA-01 ~ AC-DRAMA-06
"""


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
