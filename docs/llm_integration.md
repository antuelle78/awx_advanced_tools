# LLM Integration Guide for MCP Server

> The goal is to add a **LLM layer** that:
> * **Validates** request payloads against JSON‑schema
> * **Translates** high‑level intent into concrete AWX job templates
> * **Summarises** raw AWX logs
> * **Caches** LLM responses (optional)
> * **Secures** the calls and controls cost

## 1.  Project Layout (new modules)

```
app/
├─ llm/
│  ├─ client.py          # LLM client (Pydantic settings + Async chat wrapper)
│  └─ templates.py       # Prompt templates + helper
├─ dependencies/
│  └─ llm.py             # FastAPI dependency helpers that call the LLM
└─ main.py                # Add imports and update the /mcp route
```

## 2.  LLM Client (`app/llm/client.py`)

```python
from pydantic import BaseModel, Field
import httpx

class LLMSettings(BaseModel):
    endpoint: str = Field(..., env="LLM_ENDPOINT")
    api_key: str = Field(..., env="LLM_API_KEY")
    model: str = Field("gpt-4o-mini", env="LLM_MODEL")
    temperature: float = Field(0.2, env="LLM_TEMPERATURE")
    max_tokens: int = Field(512, env="LLM_MAX_TOKENS")

settings = LLMSettings()

class LLMClient:
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.headers = {
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self.settings.endpoint,
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

# Singleton instance for the whole app
llm_client = LLMClient(settings)
```

## 3.  Prompt Templates (`app/llm/templates.py`)

```python
from typing import Any

# Prompt templates
SCHEMA_VALIDATION_PROMPT = """
You are an expert in JSON schema validation.

**Task**: Validate the following payload against the provided schema.

**Schema**:
{schema}

**Payload**:
{payload}

Respond in JSON:
{
  "valid": true/false,
  "errors": [ ... ]   # only if valid is false
}
"""

PLAYBOOK_GENERATION_PROMPT = """
You are an Ansible automation specialist.

Given the high‑level request below, produce an Ansible job template ID
and the exact `extra_vars` JSON that should be passed to that template.

If you cannot find a suitable template, return:
{ "error": "No matching job template found" }

**Request**:
{request}
"""

LOG_SUMMARY_PROMPT = """
You are a systems engineer.

Summarize the following AWX job log in 3 sentences, highlighting
any failures or key actions.

**Log**:
{log}
"""

# Utility

def build_prompt(template: str, **kwargs: Any) -> str:
    return template.format(**kwargs)
```

## 4.  LLM Helpers (`app/dependencies/llm.py`)

```python
from fastapi import Depends, HTTPException
from app.llm.client import llm_client
from app.llm.templates import (
    SCHEMA_VALIDATION_PROMPT,
    PLAYBOOK_GENERATION_PROMPT,
    LOG_SUMMARY_PROMPT,
    build_prompt,
)
import json
from jsonschema import ValidationError

# 4.1. Schema validation via LLM
async def llm_validate_payload(payload: dict, schema: dict) -> None:
    prompt = build_prompt(
        SCHEMA_VALIDATION_PROMPT,
        schema=json.dumps(schema, indent=2),
        payload=json.dumps(payload, indent=2),
    )
    result = await llm_client.chat([{"role": "user", "content": prompt}])
    try:
        resp = json.loads(result)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="LLM returned invalid JSON")
    if not resp.get("valid", False):
        raise HTTPException(
            status_code=422,
            detail=f"LLM validation failed: {resp.get('errors')}",
        )

# 4.2. Playbook generation
async def llm_generate_job(request: dict) -> dict:
    prompt = build_prompt(
        PLAYBOOK_GENERATION_PROMPT,
        request=json.dumps(request, indent=2),
    )
    result = await llm_client.chat([{"role": "user", "content": prompt}])
    try:
        resp = json.loads(result)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="LLM returned invalid JSON")
    if "error" in resp:
        raise HTTPException(status_code=404, detail=resp["error"])
    return resp  # {"job_template_id": 123, "extra_vars": {...}}

# 4.3 Log summarization
async def llm_summarize_log(log: str) -> str:
    prompt = build_prompt(LOG_SUMMARY_PROMPT, log=log)
    return await llm_client.chat([{"role": "user", "content": prompt}])
```

## 5.  Integration into the `/mcp` route (snippet for `app/main.py`)

```python
from fastapi import Depends, HTTPException
from app.llm.client import llm_client
from app.llm.templates import (
    SCHEMA_VALIDATION_PROMPT,
    PLAYBOOK_GENERATION_PROMPT,
    LOG_SUMMARY_PROMPT,
    build_prompt,
)
import json
from jsonschema import validate, ValidationError

# The main route will now import the new LLM helpers from `app.dependencies.llm`.
# The rest of the route logic remains unchanged – just add calls to:
# * llm_validate_payload
# * llm_generate_job
# * llm_summarize_log
```

## 6.  Caching (optional – `app/cache.py`)

```python
import aioredis
import json
from app.config import settings

redis = aioredis.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
    encoding="utf-8",
    decode_responses=True,
)

async def get_or_set(key: str, compute, ttl: int = 300):
    cached = await redis.get(key)
    if cached is not None:
        return json.loads(cached)
    result = await compute()
    await redis.set(key, json.dumps(result), ex=ttl)
    return result
```