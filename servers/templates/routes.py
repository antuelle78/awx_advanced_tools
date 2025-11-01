"""
API routes for Templates server.

Handles:
- Job template creation and management
- Workflow template operations
"""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import (
    CreateJobTemplateRequest,
    CreateWorkflowTemplateRequest,
    UpdateWorkflowTemplateRequest,
    LaunchWorkflowRequest,
)
import httpx

router = APIRouter()


@router.post("/job_templates")
async def create_job_template(request: CreateJobTemplateRequest):
    """Create a new job template."""
    try:
        return await awx_client.create_job_template(
            name=request.name,
            inventory=request.inventory,
            project=request.project,
            playbook=request.playbook,
            description=request.description,
            extra_vars=request.extra_vars,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/workflow_job_templates")
async def list_workflow_templates():
    """List all workflow job templates."""
    try:
        return await awx_client.list_workflow_job_templates()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/workflow_job_templates")
async def create_workflow_template(request: CreateWorkflowTemplateRequest):
    """Create a new workflow template."""
    try:
        return await awx_client.create_workflow_job_template(
            name=request.name, description=request.description
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/workflow_job_templates/{workflow_id}")
async def update_workflow_template(
    workflow_id: int, request: UpdateWorkflowTemplateRequest
):
    """Update a workflow template."""
    try:
        return await awx_client.update_workflow_job_template(
            workflow_job_template_id=workflow_id,
            name=request.name,
            description=request.description,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/workflow_job_templates/{workflow_id}")
async def delete_workflow_template(workflow_id: int):
    """Delete a workflow template."""
    try:
        return await awx_client.delete_workflow_job_template(workflow_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/workflow_job_templates/{workflow_id}/launch")
async def launch_workflow_template(
    workflow_id: int, request: LaunchWorkflowRequest = None
):
    """Launch a workflow template."""
    try:
        extra_vars = request.extra_vars if request else None
        return await awx_client.launch_workflow_job_template(workflow_id, extra_vars)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        result = await awx_client.list_workflow_job_templates()
        return {"status": "connected", "workflow_count": result.get("count", 0)}
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"AWX connection failed: {str(exc)}"
        )
