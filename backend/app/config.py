from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DramaFlow"
    debug: bool = True

    database_url: str = "sqlite:///./dramaflow.db"

    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 120
    jwt_refresh_expire_days: int = 7

    qiniu_access_key: str = ""
    qiniu_secret_key: str = ""
    qiniu_bucket: str = ""
    qiniu_domain: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
