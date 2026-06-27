from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional

from app.models.drama import Drama, Category
from app.models.episode import Episode
from app.models.watch_record import WatchRecord
from app.models.user import User
from app.services import media_urls


def _episode_counts(db: Session, drama_ids: list[int]) -> dict[int, int]:
    """Bulk-fetch episode counts for given drama IDs to avoid N+1 queries."""
    if not drama_ids:
        return {}
    rows = (
        db.query(Episode.drama_id, func.count(Episode.id))
        .filter(Episode.drama_id.in_(drama_ids))
        .group_by(Episode.drama_id)
        .all()
    )
    return {drama_id: count for drama_id, count in rows}


def _drama_dict(drama: Drama, ep_count: int) -> dict:
    """Convert a Drama ORM object to the API-response dict."""
    return {
        "id": drama.id,
        "title": drama.title,
        "category_id": drama.category_id,
        "category_slug": drama.category.slug if drama.category else "",
        "rating": drama.rating,
        "cover_url": media_urls.drama_cover_url(drama.cover_url),
        "year": drama.year,
        "status": drama.status,
        "episode_count": ep_count,
    }


def _personalized_recommendations(db: Session, user_id: int, all_dramas: list) -> list:
    """Sort dramas by watch history: same-category unwatched first, then in-progress,
    then other-category unwatched, then completed. Within each tier, sort by rating
    descending. 'Completed' means ALL episodes of a drama have been watched
    (completed=True)."""
    total_map = _episode_counts(db, [d.id for d in all_dramas])

    watch_data = db.query(
        WatchRecord.episode_id, Episode.drama_id, WatchRecord.completed
    ).join(Episode, Episode.id == WatchRecord.episode_id).filter(
        WatchRecord.user_id == user_id
    ).all()

    if not watch_data:
        return all_dramas

    completed_count = {}
    all_watched = set()
    for w in watch_data:
        all_watched.add(w.drama_id)
        if w.completed:
            completed_count[w.drama_id] = completed_count.get(w.drama_id, 0) + 1

    completed_drama_ids = set()
    for did in all_watched:
        if completed_count.get(did, 0) >= total_map.get(did, 0):
            completed_drama_ids.add(did)

    in_progress_ids = all_watched - completed_drama_ids

    watched_category_ids = set()
    for d in all_dramas:
        if d.id in all_watched and d.category_id is not None:
            watched_category_ids.add(d.category_id)

    def priority(drama):
        if drama.id in completed_drama_ids:
            return 3
        if drama.id in in_progress_ids:
            return 1
        if drama.category_id in watched_category_ids:
            return 0
        return 2

    def sort_key(drama):
        return (priority(drama), -drama.rating)

    return sorted(all_dramas, key=sort_key)


def list_dramas(db: Session, user: Optional[User] = None, category: Optional[str] = None, page: int = 1, size: int = 20):
    query = db.query(Drama).options(joinedload(Drama.category))

    if category and category != "all":
        query = query.join(Category).filter(Category.slug == category)

    total = query.count()

    if user and (not category or category == "all"):
        all_items = query.order_by(desc(Drama.updated_at)).all()
        sorted_items = _personalized_recommendations(db, user.id, all_items)
        items = sorted_items[(page - 1) * size : page * size]
    else:
        items = query.order_by(desc(Drama.updated_at)) \
                     .offset((page - 1) * size) \
                     .limit(size) \
                     .all()

    ep_map = _episode_counts(db, [d.id for d in items])
    result = [_drama_dict(d, ep_map.get(d.id, 0)) for d in items]
    return {"items": result, "total": total, "page": page, "size": size}


def get_drama_detail(db: Session, drama_id: int):
    drama = db.query(Drama).options(joinedload(Drama.category)).filter(Drama.id == drama_id).first()
    if not drama:
        return None
    ep_count = _episode_counts(db, [drama.id]).get(drama.id, 0)
    base = _drama_dict(drama, ep_count)
    base["description"] = drama.description
    base["category_name"] = drama.category.name if drama.category else ""
    base["created_at"] = drama.created_at
    return base


def list_categories(db: Session):
    return db.query(Category).order_by(Category.sort_order).all()


def list_banners(db: Session):
    dramas = db.query(Drama).order_by(desc(Drama.rating)).limit(5).all()
    return [
        {"drama_id": d.id, "title": d.title, "image_url": media_urls.drama_cover_url(d.cover_url), "sort_order": i}
        for i, d in enumerate(dramas)
    ]
