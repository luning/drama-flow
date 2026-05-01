from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import episode_service

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
