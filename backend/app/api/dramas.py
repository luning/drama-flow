from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.middleware.auth_middleware import get_optional_user
from app.models.user import User
from app.services import drama_service

router = APIRouter()


@router.get("/dramas")
def list_dramas(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    return drama_service.list_dramas(db, user, category, page, size)


@router.get("/dramas/{drama_id}")
def drama_detail(drama_id: int, db: Session = Depends(get_db)):
    result = drama_service.get_drama_detail(db, drama_id)
    if not result:
        raise HTTPException(status_code=404, detail="剧集不存在")
    return result


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return drama_service.list_categories(db)


@router.get("/banners")
def banners(db: Session = Depends(get_db)):
    return drama_service.list_banners(db)
