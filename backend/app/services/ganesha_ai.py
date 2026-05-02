import anthropic
import httpx
from ..core.config import settings
import uuid
import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables (don't override Kubernetes env vars)
load_dotenv(override=False)

PLACEHOLDER_ANTHROPIC = 'sk-ant-placeholder-will-be-added-by-user'


def _anthropic_key_usable(key: str | None) -> bool:
    return bool(key) and key != PLACEHOLDER_ANTHROPIC


class GaneshaAI:
    """
    GANESHA AI Command Processing Service.

    Routing precedence:
      1. OpenRouter (OpenAI-compatible) when OPENROUTER_API_KEY is set.
      2. Direct Anthropic Claude when ANTHROPIC_API_KEY is set.
      3. Deterministic keyword-based fallback.
    """

    def __init__(self):
        self.anthropic_key = settings.anthropic_api_key
        self.openrouter_key = settings.openrouter_api_key
        self.openrouter_base_url = settings.openrouter_base_url.rstrip('/')
        self.openrouter_model = settings.openrouter_model
        self.openrouter_site_url = settings.openrouter_site_url
        self.openrouter_app_name = settings.openrouter_app_name
        self.client = None  # Anthropic client, lazily initialized

        self.system_message = """You are GANESHA, Executive Assistant for Kailash (EV business command center).

Analyze commands and respond with JSON:
{
  "analysis": "brief analysis",
  "recommended_department": "department_id",
  "task_breakdown": ["task", "task"],
  "obstacles": ["obstacle"],
  "action_plan": "clear steps"
}

Departments: ganesha, vishwakarma, surya, tvashta, kartikeya, kamadeva, kubera, lakshmi, brihaspati, mitra, dharma, shukra, chandra, brahma, indra, chitragupta, prajapati, yama, vani, vayu"""

    def _has_any_provider(self) -> bool:
        return bool(self.openrouter_key) or _anthropic_key_usable(self.anthropic_key)

    async def process_command(self, command: str, priority: str = "medium", timeout: int = 30) -> dict:
        """Process a command through GANESHA AI with graceful fallback."""
        try:
            if not self._has_any_provider():
                print("No AI provider configured. Using fallback routing.")
                return self._get_fallback_response(command, "No AI - Using keyword routing")
            try:
                return await self._call_ai(command, priority, timeout)
            except Exception as ai_error:
                print(f"AI processing failed: {ai_error}. Using fallback.")
                return self._get_fallback_response(command, "AI Error - Using keyword routing")
        except Exception as e:
            print(f"Error in GANESHA AI processing: {e}")
            return self._get_fallback_response(command, str(e))

    async def _call_ai(self, command: str, priority: str, timeout: int) -> dict:
        if self.openrouter_key:
            return await self._call_openrouter(command, priority, timeout)
        return await self._call_anthropic(command, priority)

    async def _call_openrouter(self, command: str, priority: str, timeout: int) -> dict:
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
        }
        if self.openrouter_site_url:
            headers["HTTP-Referer"] = self.openrouter_site_url
        if self.openrouter_app_name:
            headers["X-Title"] = self.openrouter_app_name

        payload = {
            "model": self.openrouter_model,
            "max_tokens": 800,
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": f"Priority: {priority}\nCommand: {command}\nRespond with JSON only."},
            ],
        }

        async with httpx.AsyncClient(timeout=timeout or 30) as client:
            resp = await client.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return self._parse_ai_content(content, command)

    async def _call_anthropic(self, command: str, priority: str) -> dict:
        if not _anthropic_key_usable(self.anthropic_key):
            raise ValueError(
                "ANTHROPIC_API_KEY not configured. Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY."
            )
        if not self.client:
            self.client = anthropic.AsyncAnthropic(api_key=self.anthropic_key)

        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=800,
            temperature=0.7,
            messages=[
                {"role": "user", "content": f"{self.system_message}\n\nPriority: {priority}\nCommand: {command}\nProvide JSON analysis."}
            ],
        )
        content = response.content[0].text
        return self._parse_ai_content(content, command)

    def _parse_ai_content(self, content: str, command: str) -> dict:
        try:
            result = json.loads(content)
            if not all(k in result for k in ["recommended_department", "task_breakdown"]):
                raise ValueError("Missing required fields in AI response")
            return result
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse AI response as JSON: {e}")
            return {
                "analysis": content[:500] if len(content) > 500 else content,
                "recommended_department": self._infer_department(command),
                "task_breakdown": [command],
                "obstacles": [],
                "action_plan": "Command parsed. Processing initiated.",
            }

    def _infer_department(self, command: str) -> str:
        """Simple keyword-based department inference as fallback."""
        command_lower = command.lower()

        keywords = {
            "finance": "kubera",
            "money": "kubera",
            "revenue": "lakshmi",
            "sales": "lakshmi",
            "tech": "vishwakarma",
            "engineering": "vishwakarma",
            "energy": "surya",
            "solar": "surya",
            "fleet": "kartikeya",
            "vehicle": "kartikeya",
            "customer": "kamadeva",
            "analytics": "brihaspati",
            "data": "brihaspati",
            "legal": "dharma",
            "compliance": "dharma",
            "marketing": "shukra",
            "brand": "shukra",
            "hr": "chandra",
            "people": "chandra",
            "risk": "yama",
            "logistics": "vayu",
            "supply": "vayu",
        }

        for keyword, dept in keywords.items():
            if keyword in command_lower:
                return dept

        return "ganesha"

    def _get_fallback_response(self, command: str, error: str) -> dict:
        return {
            "analysis": f"Quick analysis: {error}. Using keyword-based routing.",
            "recommended_department": self._infer_department(command),
            "task_breakdown": [command],
            "obstacles": [f"AI processing issue: {error}"],
            "action_plan": "Task created with keyword-based routing. Manual review recommended.",
        }

    async def get_department_suggestion(self, command: str) -> str:
        """Quick department suggestion without full processing."""
        result = await self.process_command(command, timeout=None)
        return result.get("recommended_department", "ganesha")


_ganesha_ai_instance = None


def get_ganesha_ai() -> GaneshaAI:
    global _ganesha_ai_instance
    if _ganesha_ai_instance is None:
        _ganesha_ai_instance = GaneshaAI()
    return _ganesha_ai_instance
