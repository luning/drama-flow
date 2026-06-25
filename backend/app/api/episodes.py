from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import episode_service
from app.services.tos_service import tos_service
from app.config import settings

router = APIRouter()


@router.get("/dramas/{drama_id}/episodes")
def list_episodes(drama_id: int, db: Session = Depends(get_db)):
    episodes = episode_service.list_episodes(db, drama_id)
    return episodes


@router.get("/episodes/{episode_id}")
def episode_detail(episode_id: int, db: Session = Depends(get_db)):
    ep = episode_service.get_episode(db, episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="单集不存在")
    return ep


@router.get("/episodes/{episode_id}/video-url")
def episode_video_url(episode_id: int, db: Session = Depends(get_db)):
    if not settings.local_media_base_url and not tos_service.is_available():
        raise HTTPException(status_code=503, detail="视频服务暂不可用")
    url, expires_at = episode_service.get_video_url(db, episode_id)
    if not url:
        raise HTTPException(status_code=404, detail="单集不存在")
    return {"url": url, "expires_at": expires_at}
