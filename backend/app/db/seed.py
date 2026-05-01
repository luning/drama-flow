"""
seed-data Skill：幂等导入测试数据。
通过 `python -m app.db.seed` 调用，可重复执行。
"""
from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.drama import Drama, Category
from app.models.episode import Episode
from app.models.watch_record import WatchRecord


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(Drama).count()
    if existing > 0:
        print(f"[seed] 数据已存在（{existing} 部剧集），跳过导入")
        return

    # 分类
    categories = [
        Category(id=1, name="甜宠", slug="romance", sort_order=1),
        Category(id=2, name="悬疑", slug="suspense", sort_order=2),
        Category(id=3, name="搞笑", slug="comedy", sort_order=3),
        Category(id=4, name="奇幻", slug="fantasy", sort_order=4),
        Category(id=5, name="霸总", slug="president", sort_order=5),
    ]
    db.add_all(categories)

    # 剧集
    dramas = [
        Drama(id=1, title="重生之女王归来", description="她是商界女王，却遭人暗算重生回到十年前...",
              category_id=4, rating=4.8, cover_url="/covers/drama01.jpg", year=2025, status="ongoing"),
        Drama(id=2, title="霸道总裁爱上我", description="平凡女孩意外闯入总裁的世界...",
              category_id=5, rating=4.9, cover_url="/covers/drama02.jpg", year=2025, status="ongoing"),
        Drama(id=3, title="我的房东是财阀", description="为了省钱租了个地下室，没想到房东竟是...",
              category_id=3, rating=4.6, cover_url="/covers/drama03.jpg", year=2025, status="completed"),
        Drama(id=4, title="深渊回响", description="每个谎言都有回响，每个真相都有代价...",
              category_id=2, rating=4.7, cover_url="/covers/drama04.jpg", year=2024, status="completed"),
        Drama(id=5, title="契约婚姻", description="一场契约开始的婚姻，却在不经意间动了真心...",
              category_id=1, rating=4.5, cover_url="/covers/drama05.jpg", year=2025, status="ongoing"),
    ]
    db.add_all(dramas)
    db.flush()

    # 集数
    episodes = []
    for d in dramas:
        for i in range(1, 11):
            episodes.append(Episode(
                drama_id=d.id, episode_number=i,
                title=f"第{i}集", duration=f"{18 + i % 5}:{i * 4:02d}",
                video_url=f"/videos/drama{d.id:02d}_ep{i:02d}.mp4",
            ))
    db.add_all(episodes)

    db.commit()
    print(f"[seed] 导入完成：{len(dramas)} 部剧集，{len(episodes)} 集")
    db.close()


if __name__ == "__main__":
    seed()
