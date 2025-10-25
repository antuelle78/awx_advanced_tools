# dependencies/llm.py
import httpx
from app.config import settings


async def llm_validate_payload(payload: dict, schema: dict):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.llm_endpoint}/validate",
            json={"payload": payload, "schema": schema},
        )
        resp.raise_for_status()


async def llm_generate_job(request: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{settings.llm_endpoint}/generate", json=request)
        resp.raise_for_status()
        return resp.json()


async def llm_summarize_log(log: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.llm_endpoint}/summarize", json={"log": log}
        )
        resp.raise_for_status()
        return resp.json().get("summary")
