"""scout backend entry."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="scout", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3100"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "model": settings.llm_model,
        "key_present": bool(settings.llm_api_key),
    }
