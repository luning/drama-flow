from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    sort_order: int

    class Config:
        from_attributes = True


class DramaListItem(BaseModel):
    id: int
    title: str
    category_id: int
    rating: float
    cover_url: str
    year: Optional[int] = None
    status: str
    episode_count: int = 0

    class Config:
        from_attributes = True


class DramaDetail(BaseModel):
    id: int
    title: str
    description: str
    category_id: int
    category_name: str = ""
    rating: float
    cover_url: str
    year: Optional[int] = None
    status: str
    episode_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class BannerItem(BaseModel):
    drama_id: int
    title: str
    image_url: str
    sort_order: int


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
