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


class ProjectCreate(BaseModel):
    name: str
    scm_type: str
    scm_url: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    scm_type: Optional[str] = None
    scm_url: Optional[str] = None
    description: Optional[str] = None


class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


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


@router.post("/inventories")
async def create_inventory(inventory: InventoryCreate, dry_run: bool = False):
    if dry_run:
        return {
            "status": "dry_run",
            "action": "create_inventory",
            "name": inventory.name,
            "organization": inventory.organization,
        }
    try:
        return await awx_client.create_inventory(
            inventory.name, inventory.variables, inventory.organization
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/inventories/{inventory_id}")
async def get_inventory(inventory_id: int):
    try:
        return await awx_client.get_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/inventories/{inventory_id}")
async def delete_inventory(inventory_id: int, dry_run: bool = False):
    if dry_run:
        return {"status": "dry_run", "action": "delete_inventory", "id": inventory_id}
    try:
        await awx_client.delete_inventory(inventory_id)
        return {"status": "deleted", "id": inventory_id}
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


# Project endpoints
@router.get("/projects")
async def list_projects():
    try:
        return await awx_client.list_projects()
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/projects/{project_id}")
async def get_project(project_id: int):
    try:
        return await awx_client.get_project(project_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/projects")
async def create_project(project: ProjectCreate):
    try:
        return await awx_client.create_project(
            project.name, project.scm_type, project.scm_url, project.description
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/projects/{project_id}")
async def update_project(project_id: int, project: ProjectUpdate):
    try:
        return await awx_client.update_project(
            project_id,
            project.name,
            project.scm_type,
            project.scm_url,
            project.description,
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, dry_run: bool = False):
    if dry_run:
        return {"status": "dry_run", "action": "delete_project", "id": project_id}
    try:
        return await awx_client.delete_project(project_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/projects/{project_id}/sync")
async def sync_project(project_id: int):
    try:
        return await awx_client.sync_project(project_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


# Organization endpoints
@router.get("/organizations")
async def list_organizations():
    try:
        return await awx_client.list_organizations()
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/organizations/{organization_id}")
async def get_organization(organization_id: int):
    try:
        return await awx_client.get_organization(organization_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/organizations")
async def create_organization(organization: OrganizationCreate):
    try:
        return await awx_client.create_organization(
            organization.name, organization.description
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/organizations/{organization_id}")
async def update_organization(organization_id: int, organization: OrganizationUpdate):
    try:
        return await awx_client.update_organization(
            organization_id, organization.name, organization.description
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/organizations/{organization_id}")
async def delete_organization(organization_id: int):
    try:
        return await awx_client.delete_organization(organization_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


# Activity Stream endpoints
@router.get("/activity_stream")
async def list_activity_stream(page: int = 1, page_size: int = 20):
    try:
        return await awx_client.list_activity_stream(page, page_size)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
