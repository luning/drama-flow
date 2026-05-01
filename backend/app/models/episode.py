from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    duration = Column(String(20), default="")
    video_url = Column(String(500), default="")
    created_at = Column(DateTime, server_default=func.now())

    drama = relationship("Drama", back_populates="episodes")
    watch_records = relationship("WatchRecord", back_populates="episode")
