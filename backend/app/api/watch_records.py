from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.watch_record import WatchRecordCreate
from app.services import watch_record_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter()


@router.put("/watch-records/{episode_id}")
def upsert_record(
    episode_id: int,
    data: WatchRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return watch_record_service.upsert_record(db, user.id, episode_id, data)


# 注意：静态路径必须定义在参数化路径之前，否则 continue-watching 会
# 被 {episode_id} 路径捕获并返回 422（无法将 "continue-watching" 转为 int）
@router.get("/watch-records/continue-watching")
def continue_watching(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return watch_record_service.continue_watching(db, user.id)


@router.get("/watch-records/{episode_id}")
def get_record(
    episode_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = watch_record_service.get_record(db, user.id, episode_id)
    if not record:
        return {"progress": 0, "last_position": 0, "completed": False}
    return record


@router.get("/watch-records")
def list_records(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return watch_record_service.list_records(db, user.id, page, size)
