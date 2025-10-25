from fastapi import APIRouter
from app.dependencies.llm import (
    llm_validate_payload,
    llm_generate_job,
    llm_summarize_log,
)

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/validate")
async def validate_payload(payload: dict, schema: dict):
    await llm_validate_payload(payload, schema)
    return {"status": "valid"}


@router.post("/generate")
async def generate_job(request: dict):
    resp = await llm_generate_job(request)
    return resp


@router.post("/summarize")
async def summarize_log(log: str):
    summary = await llm_summarize_log(log)
    return {"summary": summary}
