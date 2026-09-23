from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "scout"
    debug: bool = True
    api_prefix: str = "/api"

    database_url: str = "postgresql+asyncpg://scout:scout@localhost:5432/scout"

    cors_origins: str = "http://localhost:3100"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
