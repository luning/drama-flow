from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    sort_order = Column(Integer, default=0)
    dramas = relationship("Drama", back_populates="category")


class Drama(Base):
    __tablename__ = "dramas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), default="")
    category_id = Column(Integer, ForeignKey("categories.id"))
    rating = Column(Float, default=0.0)
    cover_url = Column(String(500), default="")
    year = Column(Integer)
    status = Column(String(20), default="ongoing")  # ongoing | completed
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="dramas")
    episodes = relationship("Episode", back_populates="drama", order_by="Episode.episode_number")
