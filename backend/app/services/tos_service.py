from typing import Optional
from tos import TosClientV2, HttpMethodType
from app.config import settings


class TosService:
    """火山引擎 TOS 对象存储服务，生成预签名 URL"""

    def __init__(self):
        if not settings.tos_access_key or not settings.tos_secret_key:
            self._client = None
            return
        self._client = TosClientV2(
            settings.tos_access_key,
            settings.tos_secret_key,
            settings.tos_endpoint,
            settings.tos_region,
        )

    def is_available(self) -> bool:
        return self._client is not None

    def signed_url(self, object_key: str, expires: Optional[int] = None) -> str:
        """生成预签名 GET URL"""
        if not self._client:
            return ""
        result = self._client.pre_signed_url(
            HttpMethodType.Http_Method_Get,
            settings.tos_bucket,
            object_key,
            expires or settings.tos_signed_url_expires,
        )
        return result.signed_url

    def video_url(self, path: str, expires: Optional[int] = None) -> str:
        """根据数据库中的 video_url 路径生成预签名 URL"""
        if not path:
            return ""
        key = path.removeprefix("/")
        return self.signed_url(key, expires)

    def direct_url(self, object_key: str) -> str:
        """生成公开文件的直接访问 URL（不走签名）"""
        if not object_key:
            return ""
        return f"https://{settings.tos_domain}/{object_key}"

    def cover_url(self, video_path: str) -> str:
        """根据 video_url 路径推断封面图的公开访问 URL"""
        if not video_path:
            return ""
        key = video_path.removeprefix("/")
        name, _ = key.rsplit(".", 1)
        return self.direct_url(f"{name}_cover.jpg")


tos_service = TosService()
