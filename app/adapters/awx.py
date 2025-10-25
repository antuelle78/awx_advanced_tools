from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.adapters.awx_service import awx_client
import httpx

router = APIRouter(prefix="/awx", tags=["AWX"])


class InventoryCreate(BaseModel):
    name: str
    organization: int
    variables: Optional[Dict] = None


class UserCreate(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


@router.post("/job_templates/{template_id}/launch")
async def launch_job_template(template_id: int, extra_vars: dict | None = None):
    try:
        return await awx_client.launch_job_template(template_id, extra_vars)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


# User endpoints
@router.get("/users")
async def list_users():
    try:
        return await awx_client.list_users()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        return await awx_client.get_user(user_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/users")
async def create_user(user: UserCreate):
    try:
        return await awx_client.create_user(
            user.username, user.password, user.first_name, user.last_name, user.email
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    try:
        return await awx_client.update_user(
            user_id, user.username, user.first_name, user.last_name, user.email
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        return await awx_client.delete_user(user_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/inventories")
async def list_inventories():
    try:
        return await awx_client.list_inventories()
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/inventories/{inventory_id}")
async def get_inventory(inventory_id: int):
    try:
        return await awx_client.get_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/inventories/{inventory_id}")
async def delete_inventory(inventory_id: int):
    try:
        return await awx_client.delete_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/inventories/{inventory_id}/sync")
async def sync_inventory(inventory_id: int):
    try:
        return await awx_client.sync_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/job_templates/{template_id}/schedules")
async def list_schedules(template_id: int):
    try:
        return await awx_client.list_schedules(template_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/schedules/{schedule_id}")
async def toggle_schedule(schedule_id: int, enabled: bool):
    try:
        return await awx_client.toggle_schedule(schedule_id, enabled)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


class ScheduleCreate(BaseModel):
    name: str
    rrule: str
    job_template_id: int


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    try:
        return await awx_client.delete_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/templates")
async def list_templates():
    try:
        return await awx_client.list_templates()
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/jobs")
async def list_jobs(page: int = 1):
    try:
        return await awx_client.list_jobs(page)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: int):
    try:
        return await awx_client.get_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/job_templates/{template_id}/schedules")
async def create_schedule(template_id: int, schedule: ScheduleCreate):
    try:
        return await awx_client.create_schedule(
            name=schedule.name, rrule=schedule.rrule, job_template_id=template_id
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
