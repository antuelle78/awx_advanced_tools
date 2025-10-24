# context adapters
from fastapi import APIRouter, Depends
from app.context.manager import ContextManager
from app.adapters.token_auth import verify_token

router = APIRouter(prefix="/context", tags=["Context"])

@router.post("/create")
async def create(ctx_id: str, data: dict, user: str = Depends(verify_token)):
    ContextManager.create_context(ctx_id, data)
    return {"status": "created"}

@router.get("/read/{ctx_id}")
async def read(ctx_id: str, user: str = Depends(verify_token)):
    return ContextManager.read_context(ctx_id)

@router.put("/update/{ctx_id}")
async def update(ctx_id: str, data: dict, user: str = Depends(verify_token)):
    ContextManager.update_context(ctx_id, data)
    return {"status": "updated"}

@router.delete("/delete/{ctx_id}")
async def delete(ctx_id: str, user: str = Depends(verify_token)):
    ContextManager.delete_context(ctx_id)
    return {"status": "deleted"}
