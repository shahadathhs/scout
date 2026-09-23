from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "scout"
    debug: bool = True
    api_prefix: str = "/api"

    database_url: str = "postgresql+asyncpg://scout:scout@localhost:5432/scout"

    # LLM — any OpenAI-compatible endpoint. Default: GLM (bigmodel.cn).
    llm_base_url: str = "https://open.bigmodel.cn/api/coding/paas/v4"
    llm_api_key: str = ""
    llm_model: str = "glm-4.6"  # planner / synthesis
    llm_fast_model: str = "glm-4.5-air"  # cheap calls: titles, routing, citation pass

    cors_origins: str = "http://localhost:3100"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
