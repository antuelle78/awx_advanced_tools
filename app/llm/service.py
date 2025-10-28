"""LLM service orchestrates template selection, client calls, and schema validation.

It is deliberately small – the heavy lifting is done by `LLMClient`.  The
service exposes a single async method `generate_payload` that takes an action
name, the request payload, and returns the JSON object that should be sent
to AWX.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

from .client import get_llm_client
from .templates import TEMPLATES

from app.schema.registry import get_schema

# Optional: simple in‑memory cache (replace with redis if needed)
_CACHE: Dict[str, Any] = {}


class PromptService:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def _cache_key(self, action: str, payload: Dict[str, Any]) -> str:
        # Use a deterministic hash of the action + sorted payload
        key = f"{action}:{json.dumps(payload, sort_keys=True)}"
        return key

    async def generate_payload(
        self, action: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        # 1. Validate the action exists
        if action not in TEMPLATES:
            raise ValueError(f"Unknown action {action}")

        # 2. Build the prompt
        template = TEMPLATES[action]
        # Render placeholders – assume simple string format
        prompt = template.format(**payload)

        # 3. Check cache
        key = self._cache_key(action, payload)
        if key in _CACHE:
            return _CACHE[key]

        # 4. Call LLM
        if action == "validate_schema":
            temperature = 0.8
        else:
            temperature = 0.2
        result = await self.client.get_payload(prompt, temperature=temperature)

        # 5. Validate result against schema
        schema = get_schema("AWX", action)
        if schema:
            import jsonschema
            try:
                jsonschema.validate(result, schema)
            except jsonschema.ValidationError as exc:  # pragma: no cover
                raise ValueError(f"LLM payload does not match schema: {exc}") from exc
        else:
            import logging
            logging.warning(f"No schema found for action '{action}', skipping validation")

        # 6. Cache & return
        _CACHE[key] = result
        return result

    # Synchronous wrapper for convenience
    def generate_payload_sync(
        self, action: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return asyncio.run(self.generate_payload(action, payload))
