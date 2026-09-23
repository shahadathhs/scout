"""Provider-agnostic LLM client — any OpenAI-compatible endpoint.

Configure via env:
  RESEARCH_BASE_URL   (default: z.ai GLM endpoint; also accepts OpenRouter/Groq/OpenAI)
  RESEARCH_API_KEY    (falls back to GLM_API_KEY, then OPENAI_API_KEY)
  RESEARCH_MODEL      (default: glm-4.6)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import httpx

DEFAULT_BASE_URL = "https://api.z.ai/api/paas/v4"
DEFAULT_MODEL = "glm-4.6"


def _base_url() -> str:
    return (
        os.environ.get("RESEARCH_BASE_URL")
        or os.environ.get("GLM_BASE_URL")
        or DEFAULT_BASE_URL
    ).rstrip("/")


def _api_key() -> str:
    return (
        os.environ.get("RESEARCH_API_KEY")
        or os.environ.get("GLM_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    )


def _model() -> str:
    return os.environ.get("RESEARCH_MODEL") or DEFAULT_MODEL


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # raw JSON


@dataclass
class Message:
    role: str
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None  # for role="tool" messages

    def to_api(self) -> dict:
        if self.role == "assistant" and self.tool_calls:
            return {
                "role": "assistant",
                "content": self.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": tc.arguments},
                    }
                    for tc in self.tool_calls
                ],
            }
        if self.role == "tool":
            return {
                "role": "tool",
                "tool_call_id": self.tool_call_id,
                "content": self.content or "",
            }
        return {"role": self.role, "content": self.content or ""}


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[ToolCall]
    finish_reason: str
    usage: dict


class LLMClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout: float = 120.0):
        self.base_url = (base_url or _base_url()).rstrip("/")
        self.api_key = api_key or _api_key()
        self.model = model or _model()
        self.timeout = timeout
        if not self.api_key:
            raise RuntimeError(
                "No API key. Set RESEARCH_API_KEY, GLM_API_KEY, or OPENAI_API_KEY."
            )

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        payload: dict = {
            "model": self.model,
            "messages": [m.to_api() for m in messages],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = [
                {"type": "function", "function": t} for t in tools
            ]
            payload["tool_choice"] = "auto"

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"LLM API {resp.status_code}: {resp.text[:500]}"
                )
            data = resp.json()

        choice = data["choices"][0]
        raw = choice.get("message", {})
        tool_calls = [
            ToolCall(
                id=tc["id"],
                name=tc["function"]["name"],
                arguments=tc["function"].get("arguments") or "{}",
            )
            for tc in raw.get("tool_calls") or []
        ]
        return LLMResponse(
            content=raw.get("content") or "",
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason", ""),
            usage=data.get("usage", {}),
        )
