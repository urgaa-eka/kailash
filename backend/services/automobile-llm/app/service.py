"""Automobile LLM — domain-specialized chat.

Implements the moat ladder:
  1. OpenRouter pass-through (any chat model) — ships today.
  2. Llama-3.1-8B fine-tune on scraped regulations + synthetic data.
  3. Continued fine-tune on anonymized customer data.
  4. Automobile-LLM-13B licensed model.

The model id is controlled by ``AUTOMOBILE_LLM_MODEL``; the service prepends
an automobile-domain system prompt unless the caller supplies one.
"""
from __future__ import annotations

import os

import httpx

from backend.shared import UpstreamError, ValidationError, get_logger

log = get_logger("automobile-llm")

DEFAULT_MODEL = "meta-llama/llama-3.1-8b-instruct"

SYSTEM_PROMPT = (
    "You are KAILASH Automobile LLM, an expert in Indian automobile "
    "regulations, vehicle parts, HSN / GST codes, charger infrastructure, "
    "servicing workflows, insurance and RTO processes. Answer precisely, "
    "cite clauses and sections when possible, prefer concise bullet "
    "structure, and never invent statutory numbers."
)


async def chat(messages: list[dict], model: str | None = None, temperature: float = 0.2) -> dict:
    if not messages:
        raise ValidationError("messages required")

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise UpstreamError(
            "OPENROUTER_API_KEY not configured",
            hint="set OPENROUTER_API_KEY in env",
        )

    if not any(m.get("role") == "system" for m in messages):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

    model_id = model or os.environ.get("AUTOMOBILE_LLM_MODEL", DEFAULT_MODEL)
    base = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL", "https://kailash.ai"),
        "X-Title": os.environ.get("OPENROUTER_APP_NAME", "KAILASH-AI"),
    }
    payload = {"model": model_id, "messages": messages, "temperature": temperature}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(f"{base.rstrip('/')}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        raise UpstreamError(f"openrouter {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        raise UpstreamError(f"openrouter call failed: {e}")

    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {
        "model": model_id,
        "text": text,
        "usage": data.get("usage"),
        "raw_id": data.get("id"),
    }
