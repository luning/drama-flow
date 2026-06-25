from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models.watch_record import WatchRecord
from app.models.episode import Episode
from app.models.drama import Drama
from app.schemas.watch_record import WatchRecordCreate
from app.services import media_urls


def upsert_record(db: Session, user_id: int, episode_id: int, data: WatchRecordCreate):
    """
    原子化 upsert：使用数据库层 INSERT ... ON CONFLICT DO UPDATE。
    避免应用层 SELECT → INSERT 之间的竞态条件（两个并发请求同时 SELECT 返回 None → 创建两条记录）。
    """
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert

    stmt = sqlite_insert(WatchRecord).values(
        user_id=user_id,
        episode_id=episode_id,
        progress=data.progress,
        last_position=data.last_position,
        completed=data.completed,
    )

    update_columns = {
        "progress": stmt.excluded.progress,
        "last_position": stmt.excluded.last_position,
        "completed": stmt.excluded.completed,
        "updated_at": stmt.excluded.updated_at,
    }

    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "episode_id"],
        set_=update_columns,
    )

    db.execute(stmt)
    db.commit()

    # 回读已 upsert 的记录
    record = db.query(WatchRecord).filter(
        WatchRecord.user_id == user_id,
        WatchRecord.episode_id == episode_id,
    ).first()
    return record


def get_record(db: Session, user_id: int, episode_id: int):
    return db.query(WatchRecord).filter(
        WatchRecord.user_id == user_id,
        WatchRecord.episode_id == episode_id,
    ).first()


def list_records(db: Session, user_id: int, page: int = 1, size: int = 20):
    query = db.query(WatchRecord).filter(WatchRecord.user_id == user_id)
    total = query.count()
    items = query.order_by(desc(WatchRecord.updated_at)) \
                 .offset((page - 1) * size).limit(size).all()
    return {"items": items, "total": total, "page": page, "size": size}


def continue_watching(db: Session, user_id: int, limit: int = 5):
    records = db.query(WatchRecord).filter(
        WatchRecord.user_id == user_id,
        WatchRecord.completed == False,
    ).order_by(desc(WatchRecord.updated_at)).limit(limit).all()

    result = []
    for r in records:
        ep = db.query(Episode).filter(Episode.id == r.episode_id).first()
        if not ep:
            continue
        drama = db.query(Drama).filter(Drama.id == ep.drama_id).first()
        if not drama:
            continue
        result.append({
            "drama_id": drama.id, "drama_title": drama.title,
            "drama_cover": media_urls.drama_cover_url(drama.cover_url),
            "episode_id": ep.id, "episode_number": ep.episode_number,
            "episode_title": ep.title,
            "progress": r.progress, "last_position": r.last_position,
            "updated_at": r.updated_at,
        })
    return result
