from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.adapters.token_auth import verify_token
from app.adapters.awx_service import awx_client
import httpx

router = APIRouter(prefix="/awx", tags=["AWX"])

class InventoryCreate(BaseModel):
    name: str
    organization: int
    variables: Optional[Dict] = None

@router.post("/job_templates/{template_id}/launch")
async def launch_job_template(template_id: int, extra_vars: dict | None = None, user: str = Depends(verify_token)):
    try:
        return await awx_client.launch_job_template(template_id, extra_vars)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.post("/inventories")
async def create_inventory(inventory: InventoryCreate, user: str = Depends(verify_token)):
    try:
        # The awx_client.create_inventory expects name and variables, let's adapt
        return await awx_client.create_inventory(
            name=inventory.name,
            variables=inventory.variables,
            organization=inventory.organization
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
