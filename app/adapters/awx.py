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

@router.get("/inventories")
async def list_inventories(user: str = Depends(verify_token)):
    try:
        return await awx_client.list_inventories()
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.get("/inventories/{inventory_id}")
async def get_inventory(inventory_id: int, user: str = Depends(verify_token)):
    try:
        return await awx_client.get_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.delete("/inventories/{inventory_id}")
async def delete_inventory(inventory_id: int, user: str = Depends(verify_token)):
    try:
        return await awx_client.delete_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.post("/inventories/{inventory_id}/sync")
async def sync_inventory(inventory_id: int, user: str = Depends(verify_token)):
    try:
        return await awx_client.sync_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/job_templates/{template_id}/schedules")
async def list_schedules(template_id: int, user: str = Depends(verify_token)):
    try:
        return await awx_client.list_schedules(template_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.patch("/schedules/{schedule_id}")
async def toggle_schedule(schedule_id: int, enabled: bool, user: str = Depends(verify_token)):
    try:
        return await awx_client.toggle_schedule(schedule_id, enabled)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

class ScheduleCreate(BaseModel):
    name: str
    rrule: str
    job_template_id: int

@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int, user: str = Depends(verify_token)):
    try:
        return await awx_client.delete_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.get("/templates")
async def list_templates(user: str = Depends(verify_token)):
    try:
        return await awx_client.list_templates()
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.get("/jobs")
async def list_jobs(page: int = 1, user: str = Depends(verify_token)):
    try:
        return await awx_client.list_jobs(page)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: int, user: str = Depends(verify_token)):
    try:
        return await awx_client.get_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

async def create_schedule(schedule: ScheduleCreate, user: str = Depends(verify_token)):
    try:
        return await awx_client.create_schedule(
            name=schedule.name,
            rrule=schedule.rrule,
            job_template_id=schedule.job_template_id
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
