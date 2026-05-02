from sqlalchemy.orm import Session
from app.models.episode import Episode
from app.services.tos_service import tos_service


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
