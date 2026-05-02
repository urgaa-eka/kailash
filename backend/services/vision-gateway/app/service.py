"""Vision LLM Gateway — route vision requests across providers.

Routing policy (default ``auto``):
  - cheap / low latency → ``openai/gpt-4o-mini``
  - heavy reasoning → ``anthropic/claude-3.5-sonnet``
  - long context → ``google/gemini-1.5-pro``

All calls go through OpenRouter so we get one billing surface, retries,
and consistent error handling.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

from backend.shared import UpstreamError, ValidationError, get_logger

log = get_logger("vision-gateway")


MODELS: dict[str, str] = {
    "fast":    "openai/gpt-4o-mini",
    "balanced":"anthropic/claude-3.5-sonnet",
    "long":    "google/gemini-1.5-pro",
}


@dataclass
class RouteDecision:
    tier: str
    model: str
    reason: str


def choose(tier: str | None, prompt: str) -> RouteDecision:
    if tier and tier in MODELS:
        return RouteDecision(tier=tier, model=MODELS[tier], reason="explicit tier")
    n = len(prompt)
    if n > 8000:
        return RouteDecision(tier="long", model=MODELS["long"], reason=f"prompt_chars={n}")
    if n > 2000:
        return RouteDecision(tier="balanced", model=MODELS["balanced"], reason=f"prompt_chars={n}")
    return RouteDecision(tier="fast", model=MODELS["fast"], reason=f"prompt_chars={n}")


async def call_openrouter(model: str, messages: list[dict]) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise UpstreamError(
            "OPENROUTER_API_KEY not configured",
            hint="set OPENROUTER_API_KEY in env or .env",
        )
    base = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL", "https://kailash.ai"),
        "X-Title": os.environ.get("OPENROUTER_APP_NAME", "KAILASH-AI"),
    }
    payload = {"model": model, "messages": messages}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(f"{base.rstrip('/')}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        raise UpstreamError(f"openrouter {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        raise UpstreamError(f"openrouter call failed: {e}")


def build_messages(prompt: str, image_url: str | None) -> list[dict]:
    if not prompt and not image_url:
        raise ValidationError("prompt or image_url required")
    content: list[dict] = []
    if prompt:
        content.append({"type": "text", "text": prompt})
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    return [{"role": "user", "content": content}]
