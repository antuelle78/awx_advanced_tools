import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from app.adapters.token_auth import verify_token
from app.context.manager import ContextManager

router = APIRouter(prefix="/context", tags=["Context"])

@router.post("/create")
async def create_context(data: dict, user: str = Depends(verify_token)):
    ctx_id = data.get("ctx_id") or str(uuid.uuid4())
    context_data = data.get("data", data)
    try:
        ContextManager.create_context(ctx_id, context_data)
        return {"context_id": ctx_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/read/{ctx_id}")
async def read_context(ctx_id: str, user: str = Depends(verify_token)):
    try:
        ctx = ContextManager.read_context(ctx_id)
        if not ctx:
            raise HTTPException(status_code=404, detail="Context not found")
        return ctx
    except KeyError:
        raise HTTPException(status_code=404, detail="Context not found")

@router.put("/update/{ctx_id}")
async def update_context(ctx_id: str, data: dict, user: str = Depends(verify_token)):
    try:
        ContextManager.update_context(ctx_id, data)
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete/{ctx_id}")
async def delete_context(ctx_id: str, user: str = Depends(verify_token)):
    try:
        ContextManager.delete_context(ctx_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
