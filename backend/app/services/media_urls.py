from pathlib import Path

from app.config import settings
from app.services.tos_service import tos_service


def drama_cover_url(db_cover_path: str) -> str:
    """Drama 封面 URL：本地开发走 /media/，生产走 TOS 公开 URL"""
    if not db_cover_path:
        return ""
    if settings.local_media_base_url:
        filename = Path(db_cover_path).name
        return f"{settings.local_media_base_url}/media/{filename}"
    return tos_service.direct_url(db_cover_path)


def episode_video_url(db_video_path: str) -> str:
    """剧集视频 URL：本地开发走 /media/，生产走 TOS 签名 URL"""
    if not db_video_path:
        return ""
    if settings.local_media_base_url:
        filename = Path(db_video_path).name
        return f"{settings.local_media_base_url}/media/{filename}"
    return tos_service.video_url(db_video_path)


def episode_cover_url(db_video_path: str) -> str:
    """从视频路径推断封面 URL：本地开发走 /media/，生产走 TOS 公开 URL"""
    if not db_video_path:
        return ""
    if settings.local_media_base_url:
        filename = Path(db_video_path).stem + "_cover.jpg"
        return f"{settings.local_media_base_url}/media/{filename}"
    return tos_service.cover_url(db_video_path)
