from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from app.models.episode import Episode
from app.services.tos_service import tos_service
from app.config import settings


def _sign_episode(ep: Episode) -> dict:
    """为单集生成签名 URL，返回可直接序列化的 dict"""
    data = {
        "id": ep.id,
        "drama_id": ep.drama_id,
        "episode_number": ep.episode_number,
        "title": ep.title,
        "duration": ep.duration,
        "video_url": tos_service.video_url(ep.video_url),
        "cover_url": tos_service.cover_url(ep.video_url),
    }
    return data


def list_episodes(db: Session, drama_id: int):
    episodes = (
        db.query(Episode)
        .filter(Episode.drama_id == drama_id)
        .order_by(Episode.episode_number)
        .all()
    )
    return [_sign_episode(ep) for ep in episodes]


def get_episode(db: Session, episode_id: int):
    ep = db.query(Episode).filter(Episode.id == episode_id).first()
    if not ep:
        return None
    return _sign_episode(ep)


def get_video_url(db: Session, episode_id: int):
    """获取单集视频签名 URL 及过期时间"""
    if not tos_service.is_available():
        return None, None  # caller returns 503

    ep = db.query(Episode).filter(Episode.id == episode_id).first()
    if not ep:
        return None, None  # caller returns 404

    url = tos_service.video_url(ep.video_url)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=settings.tos_signed_url_expires)).isoformat()
    return url, expires_at
