from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_mode: str = "demo"
    database_url: str = "sqlite:///./demo.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    upload_dir: str = "./data/uploads"
    session_ttl_hours: int = 8


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.app_mode != "demo":
        raise RuntimeError("Este MVP solo permite APP_MODE=demo; producción no implementada.")
    return settings
