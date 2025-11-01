"""
API routes for Project Management server.

Handles:
- Project listing, creation, updates
- Project deletion and synchronization
"""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import CreateProjectRequest, UpdateProjectRequest
import httpx

router = APIRouter()


@router.get("/projects")
async def list_projects(name: str = None):
    """List all projects, optionally filtered by name."""
    try:
        return await awx_client.list_projects(name)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/projects/{project_id}")
async def get_project(project_id: int):
    """Get project details by ID."""
    try:
        return await awx_client.get_project(project_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/projects")
async def create_project(request: CreateProjectRequest):
    """Create a new project."""
    try:
        return await awx_client.create_project(
            name=request.name,
            scm_type=request.scm_type,
            scm_url=request.scm_url,
            description=request.description
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/projects/{project_id}")
async def update_project(project_id: int, request: UpdateProjectRequest):
    """Update project details."""
    try:
        return await awx_client.update_project(
            project_id=project_id,
            name=request.name,
            scm_type=request.scm_type,
            scm_url=request.scm_url,
            description=request.description
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    """Delete a project."""
    try:
        return await awx_client.delete_project(project_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/projects/{project_id}/sync")
async def sync_project(project_id: int):
    """Sync project from SCM."""
    try:
        return await awx_client.sync_project(project_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        result = await awx_client.list_projects()
        return {
            "status": "connected",
            "project_count": result.get("count", 0)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AWX connection failed: {str(exc)}")
