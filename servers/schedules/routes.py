"""API routes for Schedules Management server."""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import CreateScheduleRequest, UpdateScheduleRequest
import httpx

router = APIRouter()


@router.get("/schedules/template/{template_id}")
async def list_schedules(template_id: int):
    """List schedules for a job template."""
    try:
        return await awx_client.list_schedules(template_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: int):
    """Get schedule details."""
    try:
        return await awx_client.get_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/schedules")
async def create_schedule(request: CreateScheduleRequest):
    """Create a new schedule."""
    try:
        return await awx_client.create_schedule(
            name=request.name,
            rrule=request.rrule,
            job_template_id=request.job_template_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/schedules/{schedule_id}")
async def update_schedule(schedule_id: int, request: UpdateScheduleRequest):
    """Update schedule."""
    try:
        return await awx_client.update_schedule(
            schedule_id=schedule_id,
            name=request.name,
            rrule=request.rrule,
            enabled=request.enabled,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/schedules/{schedule_id}/toggle")
async def toggle_schedule(schedule_id: int, enabled: bool):
    """Enable/disable schedule."""
    try:
        return await awx_client.toggle_schedule(schedule_id, enabled)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    """Delete schedule."""
    try:
        return await awx_client.delete_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        result = await awx_client.list_templates()
        return {"status": "connected", "template_count": result.get("count", 0)}
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"AWX connection failed: {str(exc)}"
        )
