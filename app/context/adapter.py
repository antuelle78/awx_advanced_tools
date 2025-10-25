# context adapters
from fastapi import APIRouter
from app.context.manager import ContextManager

router = APIRouter(prefix="/context", tags=["Context"])


@router.post("/create")
async def create(ctx_id: str, data: dict):
    ContextManager.create_context(ctx_id, data)
    return {"status": "created"}


@router.get("/read/{ctx_id}")
async def read(ctx_id: str):
    return ContextManager.read_context(ctx_id)


@router.put("/update/{ctx_id}")
async def update(ctx_id: str, data: dict):
    ContextManager.update_context(ctx_id, data)
    return {"status": "updated"}


@router.delete("/delete/{ctx_id}")
async def delete(ctx_id: str):
    ContextManager.delete_context(ctx_id)
    return {"status": "deleted"}
