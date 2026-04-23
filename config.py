from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "BeatWave"
    database_url: str = "sqlite:///./beatwave.db"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    hubtel_client_id: str = ""
    hubtel_client_secret: str = ""
    hubtel_sender_id: str = "BeatWave"

    frontend_url: str = "http://localhost:3000"
    max_upload_size_mb: int = 500

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
