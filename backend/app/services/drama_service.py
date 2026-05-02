from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional

from app.models.drama import Drama, Category
from app.models.episode import Episode
from app.services.tos_service import tos_service


def list_dramas(db: Session, category: Optional[str] = None, page: int = 1, size: int = 20):
    query = db.query(Drama).options(joinedload(Drama.category))

    if category and category != "all":
        query = query.join(Category).filter(Category.slug == category)

    total = query.count()
    items = query.order_by(desc(Drama.updated_at)) \
                 .offset((page - 1) * size) \
                 .limit(size) \
                 .all()

    result = []
    for d in items:
        ep_count = db.query(Episode).filter(Episode.drama_id == d.id).count()
        result.append({
            "id": d.id, "title": d.title, "category_id": d.category_id,
            "category_slug": d.category.slug if d.category else "",
            "rating": d.rating, "cover_url": tos_service.direct_url(d.cover_url) if d.cover_url else "", "year": d.year,
            "status": d.status, "episode_count": ep_count,
        })
    return {"items": result, "total": total, "page": page, "size": size}


def get_drama_detail(db: Session, drama_id: int):
    drama = db.query(Drama).options(joinedload(Drama.category)).filter(Drama.id == drama_id).first()
    if not drama:
        return None
    ep_count = db.query(Episode).filter(Episode.drama_id == drama.id).count()
    return {
        "id": drama.id, "title": drama.title, "description": drama.description,
        "category_id": drama.category_id,
        "category_name": drama.category.name if drama.category else "",
        "rating": drama.rating, "cover_url": tos_service.direct_url(drama.cover_url) if drama.cover_url else "", "year": drama.year,
        "status": drama.status, "episode_count": ep_count, "created_at": drama.created_at,
    }


def list_categories(db: Session):
    return db.query(Category).order_by(Category.sort_order).all()


def list_banners(db: Session):
    dramas = db.query(Drama).order_by(desc(Drama.rating)).limit(5).all()
    return [
        {"drama_id": d.id, "title": d.title, "image_url": tos_service.direct_url(d.cover_url) if d.cover_url else "", "sort_order": i}
        for i, d in enumerate(dramas)
    ]
