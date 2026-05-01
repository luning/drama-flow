from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WatchRecordCreate(BaseModel):
    progress: float       # 0-100
    last_position: float  # seconds
    completed: bool = False


class WatchRecordResponse(BaseModel):
    id: int
    user_id: int
    episode_id: int
    progress: float
    last_position: float
    completed: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class ContinueWatchingItem(BaseModel):
    drama_id: int
    drama_title: str
    drama_cover: str
    episode_id: int
    episode_number: int
    episode_title: str
    progress: float
    last_position: float
    updated_at: datetime
