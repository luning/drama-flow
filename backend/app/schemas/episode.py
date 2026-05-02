from pydantic import BaseModel
from typing import Optional


class EpisodeResponse(BaseModel):
    id: int
    drama_id: int
    episode_number: int
    title: str
    duration: str
    video_url: str
    cover_url: str = ""

    class Config:
        from_attributes = True


class VideoUrlResponse(BaseModel):
    url: str
    expires_at: int
