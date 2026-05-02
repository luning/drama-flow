from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DramaFlow"
    debug: bool = True

    database_url: str = "sqlite:///./dramaflow.db"

    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 120
    jwt_refresh_expire_days: int = 7

    # Volcengine TOS (对象存储) — 通过 .env 注入
    tos_access_key: str = ""
    tos_secret_key: str = ""
    tos_endpoint: str = "tos-cn-beijing.volces.com"
    tos_region: str = "cn-beijing"
    tos_bucket: str = ""
    tos_domain: str = ""

    # 预签名 URL 过期时间（秒），默认 6 小时
    tos_signed_url_expires: int = 21600

    class Config:
        env_file = ".env"


settings = Settings()
