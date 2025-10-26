"""LLM client wrapper.

This module uses the official OpenAI SDK (or any other SDK that follows the same
`ChatCompletion` API).  The client is intentionally lightweight – it only exposes
one public method `get_payload` which sends a prompt and expects a JSON string
in the response.

The module is written to be easily swapped for other providers – just
replace the import and adjust the request payload.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict
from abc import ABC, abstractmethod

from app.config import settings


class BaseLLMClient(ABC):
    @abstractmethod
    async def get_payload(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAIClient(BaseLLMClient):
    """Simple wrapper around the OpenAI chat completion API."""

    def __init__(self) -> None:
        try:
            import openai
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "OpenAI SDK not installed. Install with `pip install openai`"
            ) from exc

        self.openai = openai
        self.endpoint = settings.llm_endpoint
        self.model = settings.llm_model
        self.api_key = settings.llm_api_key
        if not self.api_key:  # pragma: no cover
            raise ValueError(
                "LLM_API_KEY environment variable is required for the default provider"
            )
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "3000"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

        self.openai.api_key = self.api_key
        if self.endpoint:
            self.openai.api_base = self.endpoint.split("/v1/")[0]  # strip path

    async def get_payload(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> Dict[str, Any]:
        request = {
            "model": model or self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": temperature or self.temperature,
            "response_format": {"type": "json_object"},
        }
        try:
            response = await self.openai.ChatCompletion.acreate(**request)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("LLM request failed") from exc

        content = response.choices[0].message.content
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise ValueError(f"LLM did not return valid JSON: {content}") from exc
        return payload


class OllamaClient(BaseLLMClient):
    """Client for Ollama."""

    def __init__(self) -> None:
        try:
            import ollama
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Ollama SDK not installed. Install with `pip install ollama`"
            ) from exc
        self.client = ollama.AsyncClient(host=settings.llm_endpoint)
        self.model = settings.llm_model
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    async def get_payload(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> Dict[str, Any]:
        request = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature or self.temperature},
        }
        try:
            response = await self.client.generate(**request)  # type: ignore
            content = response["response"]
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("LLM request failed") from exc

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise ValueError(f"LLM did not return valid JSON: {content}") from exc
        return payload


def get_llm_client() -> BaseLLMClient:
    if settings.llm_provider == "ollama":
        return OllamaClient()
    from importlib.util import find_spec
    if find_spec("openai") is None:
        # OpenAI SDK not available, fallback to Ollama if configured
        if settings.llm_provider == "ollama":
            return OllamaClient()
        raise RuntimeError("OpenAI SDK not installed and llm_provider not set to ollama")
    return OpenAIClient()

LLMClient = get_llm_client()
