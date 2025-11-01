"""
API routes for Core Operations server.

Handles:
- Job template listing and launching
- Job status monitoring
"""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import LaunchJobRequest
import httpx

router = APIRouter()


@router.get("/job_templates")
async def list_templates(name: str = None):
    """List all job templates."""
    try:
        return await awx_client.list_templates(name)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/job_templates/{template_id}/launch")
async def launch_job_template(template_id: int, request: LaunchJobRequest = None):
    """Launch a job template."""
    try:
        extra_vars = request.extra_vars if request else None
        return await awx_client.launch_job_template(template_id, extra_vars)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/jobs")
async def list_jobs(page: int = 1):
    """List jobs with pagination."""
    try:
        return await awx_client.list_jobs(page)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    """Get job status and details."""
    try:
        return await awx_client.get_job(job_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        result = await awx_client.list_templates()
        return {
            "status": "connected",
            "template_count": result.get("count", 0)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AWX connection failed: {str(exc)}")
