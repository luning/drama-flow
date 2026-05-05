import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.drama import Drama, Category
from app.models.episode import Episode
from app.services.auth_service import hash_password, create_token
from app.config import settings

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestSession()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_user(db_session):
    user = User(
        nickname="TestUser",
        email="test@test.com",
        hashed_password=hash_password("Pass1234"),
    )
    db_session.add(user)
    db_session.commit()
    return user


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
