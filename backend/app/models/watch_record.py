from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class WatchRecord(Base):
    __tablename__ = "watch_records"

    __table_args__ = (
        UniqueConstraint("user_id", "episode_id", name="uq_user_episode"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    progress = Column(Float, default=0.0)       # 0-100
    last_position = Column(Float, default=0.0)  # seconds
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    episode = relationship("Episode", back_populates="watch_records")
