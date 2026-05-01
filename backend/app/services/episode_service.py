from sqlalchemy.orm import Session
from app.models.episode import Episode


def list_episodes(db: Session, drama_id: int):
    return db.query(Episode).filter(Episode.drama_id == drama_id) \
              .order_by(Episode.episode_number).all()


def get_episode(db: Session, episode_id: int):
    return db.query(Episode).filter(Episode.id == episode_id).first()
