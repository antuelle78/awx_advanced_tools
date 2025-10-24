from fastapi import APIRouter, Depends
from app.adapters.token_auth import verify_token
from app.dependencies.llm import llm_validate_payload, llm_generate_job, llm_summarize_log

router = APIRouter(prefix="/llm", tags=["LLM"])

@router.post("/validate")
async def validate_payload(payload: dict, schema: dict, user: str = Depends(verify_token)):
    await llm_validate_payload(payload, schema)
    return {"status": "valid"}

@router.post("/generate")
async def generate_job(request: dict, user: str = Depends(verify_token)):
    resp = await llm_generate_job(request)
    return resp

@router.post("/summarize")
async def summarize_log(log: str, user: str = Depends(verify_token)):
    summary = await llm_summarize_log(log)
    return {"summary": summary}
