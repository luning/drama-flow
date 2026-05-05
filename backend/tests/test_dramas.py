"""
Drama 剧集模块集成测试：AC-DRAMA-01 ~ AC-DRAMA-06
"""


class TestDramas:
    """AC-DRAMA-01 ~ AC-DRAMA-06 [Changed: AC-DRAMA-01/02 personalized part tested in TestDramasPersonalized]"""

    def test_list_dramas_default(self, client, seed_dramas):
        """AC-DRAMA-02 [Changed]: 不传分类参数时未登录用户返回全量剧集（已登录用户个性化排序见 TestDramasPersonalized）"""
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


class TestDramasPersonalized:
    """AC-DRAMA-01/02/07/08/09: Personalized recommendation based on watch history"""

    def test_logged_in_personalized_sort(self, client, seed_user, seed_drama_fantasy2, auth_header):
        """AC-DRAMA-07 / REC-01: Logged-in user with watch history gets same-category-first sort."""
        client.put("/api/watch-records/1",
                   json={"progress": 50.0, "last_position": 300.0, "completed": False},
                   headers=auth_header)

        response = client.get("/api/dramas", headers=auth_header)
        assert response.status_code == 200
        items = response.json()["items"]
        item_ids = [d["id"] for d in items]

        pos_drama6 = item_ids.index(6)
        pos_drama2 = item_ids.index(2)

        assert pos_drama6 < pos_drama2, \
            f"Drama 6 (same category) at position {pos_drama6} should be before Drama 2 (other category) at position {pos_drama2}"
        assert response.json()["total"] == 6

    def test_completed_dramas_downgraded(self, client, seed_user, seed_drama_fantasy2, auth_header):
        """AC-DRAMA-08 / REC-02: Fully completed dramas appear at lower positions than in-progress."""
        client.put("/api/watch-records/11",
                   json={"progress": 50.0, "last_position": 300.0, "completed": False},
                   headers=auth_header)
        # Mark ALL 10 episodes of drama 3 (ids 21-30) as completed
        for ep_id in range(21, 31):
            client.put(f"/api/watch-records/{ep_id}",
                       json={"progress": 100.0, "last_position": 600.0, "completed": True},
                       headers=auth_header)

        response = client.get("/api/dramas", headers=auth_header)
        assert response.status_code == 200
        items = response.json()["items"]
        item_ids = [d["id"] for d in items]

        pos_drama2 = item_ids.index(2)
        pos_drama3 = item_ids.index(3)

        assert pos_drama2 < pos_drama3, \
            f"In-progress Drama 2 at position {pos_drama2} should be before completed Drama 3 at position {pos_drama3}"

    def test_unauthenticated_default_sort(self, client, seed_drama_fantasy2):
        """AC-DRAMA-09 / REC-03: Unauthenticated user gets default sort (no personalization)."""
        response = client.get("/api/dramas")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6
        assert len(data["items"]) == 6
        assert "page" in data
        assert "size" in data

    def test_no_watch_records_fallback(self, client, seed_user, seed_drama_fantasy2, auth_header):
        """REC-04: Authenticated user with NO watch records gets default sort (fallback)."""
        response = client.get("/api/dramas", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6
        assert len(data["items"]) == 6

    def test_personalized_with_pagination(self, client, seed_user, seed_drama_fantasy2, auth_header):
        """AC-DRAMA-01 [Changed]: 已登录用户个性化排序 + 分页正常交互"""
        client.put("/api/watch-records/1",
                   json={"progress": 50.0, "last_position": 300.0, "completed": False},
                   headers=auth_header)

        # Page with size=2, should get 2 items
        response = client.get("/api/dramas?page=1&size=2", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6
        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["items"]) == 2
        # First page should have top-2 priority items (priority 0: same-category unwatched)
        assert data["items"][0]["id"] == 6  # 龙族崛起, same fantasy category

        # Page 2 should have next items
        response2 = client.get("/api/dramas?page=2&size=2", headers=auth_header)
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 2

    def test_in_progress_sorted_by_rating(self, client, seed_user, seed_drama_fantasy2, auth_header):
        """AC-DRAMA-07: 同层（进行中）按评分降序排列。"""
        client.put("/api/watch-records/1",
                   json={"progress": 50.0, "last_position": 300.0, "completed": False},
                   headers=auth_header)
        client.put("/api/watch-records/21",
                   json={"progress": 30.0, "last_position": 180.0, "completed": False},
                   headers=auth_header)

        response = client.get("/api/dramas", headers=auth_header)
        items = response.json()["items"]
        item_ids = [d["id"] for d in items]

        # Drama 1 (奇幻, ⭐4.8) and drama 3 (悬疑, ⭐4.7) both in-progress
        # Should be sorted by rating descending: drama 1 before drama 3
        pos_1 = item_ids.index(1)
        pos_3 = item_ids.index(3)
        assert pos_1 < pos_3, \
            f"Drama 1 (⭐4.8) at #{pos_1} should be before Drama 3 (⭐4.7) at #{pos_3}"

    def test_other_category_sorted_by_rating(self, client, seed_user, seed_drama_fantasy2, auth_header):
        """AC-DRAMA-07: 同层（其他未看）按评分降序排列：2(4.9)→3(4.7)→5(4.6)→4(4.5)。"""
        client.put("/api/watch-records/1",
                   json={"progress": 50.0, "last_position": 300.0, "completed": False},
                   headers=auth_header)

        response = client.get("/api/dramas", headers=auth_header)
        items = response.json()["items"]
        item_ids = [d["id"] for d in items]

        # Priority 2 (other-category unwatched) should be sorted by rating desc
        expected = [2, 3, 5, 4]
        positions = [item_ids.index(did) for did in expected]
        assert positions == sorted(positions), \
            f"Other-category unwatched expected order {expected}, got positions: {dict(zip(expected, positions))}"
