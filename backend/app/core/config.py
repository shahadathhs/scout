"""Environment-driven settings (adda-style)."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    # LLM (any OpenAI-compatible endpoint)
    llm_base_url: str = "https://api.z.ai/api/paas/v4"
    llm_api_key: str = ""
    llm_model: str = "glm-4.6"
    fast_model: str = ""  # falls back to llm_model

    # research knobs
    max_subagents: int = 4
    subagent_step_budget: int = 8


settings = Settings()
