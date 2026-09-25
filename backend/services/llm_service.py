"""
Thin wrapper around the Anthropic Messages API. Every "brain" call the
agents make (choose next question, evaluate an answer, build a roadmap,
parse a resume) goes through here, so swapping models/providers later
means touching one file.
"""
import json
import re
from typing import Any, Dict, Optional

import httpx

from config import settings

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


class LLMService:
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.model = settings.llm_model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def complete_json(self, system: str, user: str, max_tokens: int = 1000) -> Optional[Dict[str, Any]]:
        """Call the model and parse a JSON object out of its reply.
        Returns None if the LLM isn't configured or the call fails —
        callers fall back to deterministic logic in that case, so the
        product still works without an API key (with lower-quality
        questions/evaluations)."""
        if not self.configured:
            return None
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    ANTHROPIC_URL,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": max_tokens,
                        "system": system + "\nRespond with ONLY a single valid JSON object. No prose, no markdown fences.",
                        "messages": [{"role": "user", "content": user}],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                text = "".join(
                    block.get("text", "") for block in data.get("content", [])
                    if block.get("type") == "text"
                )
                return self._parse_json(text)
        except Exception:
            return None

    @staticmethod
    def _parse_json(text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()
        text = re.sub(r"^```json\s*|\s*```$", "", text)
        text = re.sub(r"^```\s*|\s*```$", "", text)
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    return None
        return None


llm_service = LLMService()
